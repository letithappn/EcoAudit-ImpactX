"""Small in-memory run store for the ImpactX MVP."""

from __future__ import annotations

import tempfile
import threading
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from ecoaudit.optimization.models import ScenarioResult
from ecoaudit.pipeline import PipelineExecution, execute_pipeline


STAGES = (
    "Uploading",
    "Parsing",
    "AI Classification",
    "Validation",
    "Carbon Calculation",
    "Carbon Intelligence",
    "Scenario Analysis",
    "Recommendations",
)

STAGE_PROGRESS = {stage: round(index / (len(STAGES) - 1) * 100) for index, stage in enumerate(STAGES)}


@dataclass
class RunSession:
    run_id: str
    filename: str
    provider: str
    year: int
    country: str
    input_path: Path
    size_bytes: int
    status: str = "queued"
    stage: str = "Uploading"
    progress: int = 0
    error: str | None = None
    execution: PipelineExecution | None = None
    scenario_results: list[ScenarioResult] = field(default_factory=list)


class RunStore:
    def __init__(self) -> None:
        self._runs: dict[str, RunSession] = {}
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="ecoaudit-run")

    def create(
        self,
        filename: str,
        content: bytes,
        provider: str,
        year: int,
        country: str,
    ) -> RunSession:
        run_id = uuid4().hex
        safe_filename = Path(filename).name or "upload.csv"
        run_dir = Path(tempfile.mkdtemp(prefix=f"ecoaudit-{run_id}-"))
        input_path = run_dir / safe_filename
        input_path.write_bytes(content)
        session = RunSession(
            run_id=run_id,
            filename=safe_filename,
            provider=provider,
            year=year,
            country=country,
            input_path=input_path,
            size_bytes=len(content),
        )
        with self._lock:
            self._runs[run_id] = session
        self._executor.submit(self._process, session)
        return session

    def get(self, run_id: str) -> RunSession | None:
        with self._lock:
            return self._runs.get(run_id)

    def _set_stage(self, session: RunSession, stage: str) -> None:
        with self._lock:
            session.stage = stage
            session.progress = STAGE_PROGRESS.get(stage, session.progress)
            session.status = "running"

    def _process(self, session: RunSession) -> None:
        try:
            execution = execute_pipeline(
                session.input_path,
                provider=session.provider,
                year=session.year,
                country=session.country,
                progress=lambda stage: self._set_stage(session, stage),
            )
            with self._lock:
                session.execution = execution
                session.status = "complete_with_review" if execution.classification_stats.needs_review else "complete"
                session.stage = "Recommendations"
                session.progress = 100
        except Exception as error:
            with self._lock:
                session.status = "failed"
                session.stage = "Recommendations"
                session.progress = 100
                session.error = str(error)


run_store = RunStore()
