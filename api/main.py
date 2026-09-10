"""FastAPI application for the EcoAudit ImpactX product."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.ai.validation import resolve_category, resolve_scope, resolve_unit
from ecoaudit.optimization.interventions import AbsoluteReduction, FuelSubstitution, PercentageReduction
from ecoaudit.optimization.models import ScenarioDefinition

from api.schemas import (
    ActivitiesResponse,
    ActivityDTO,
    AIConfigRequest,
    AIConfigResponse,
    AIStatusResponse,
    AITestRequest,
    AITestResponse,
    EvidenceResponse,
    RecommendationsResponse,
    RunCreateResponse,
    RunStatusResponse,
    RunSummaryResponse,
    ScenarioRequest,
    ScenarioResponse,
)
from ecoaudit.ai.gemini_provider import DEFAULT_GEMINI_MODEL, test_gemini_connection
from api.serializers import (
    activities_dto,
    decimal,
    evidence_dto,
    recommendation_dto,
    report_parts,
    scenario_dto,
)
from api.store import RunSession, run_store


MAX_UPLOAD_MB = int(os.getenv("ECOAUDIT_MAX_UPLOAD_MB", "50"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
MAX_ACTIVITY_PAGE_SIZE = 250
ALLOWED_PROVIDERS = {"mock", "gemini"}

app = FastAPI(title="EcoAudit AI API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _session(run_id: str) -> RunSession:
    session = run_store.get(run_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return session


def _execution(session: RunSession):
    if session.status == "failed":
        raise HTTPException(status_code=409, detail=session.error or "Run failed")
    if session.execution is None:
        raise HTTPException(status_code=409, detail="Run is still processing")
    return session.execution


def _parse_decimal(value: str | None, field: str) -> Decimal:
    if value is None or not value.strip():
        raise HTTPException(status_code=422, detail=f"{field} is required")
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError) as error:
        raise HTTPException(status_code=422, detail=f"{field} must be numeric") from error


def _intervention(request: ScenarioRequest):
    if request.intervention_type == "PercentageReduction":
        return PercentageReduction(_parse_decimal(request.reduction_percentage, "reduction_percentage"))
    if request.intervention_type == "AbsoluteReduction":
        return AbsoluteReduction(_parse_decimal(request.reduction_amount, "reduction_amount"))

    required = {
        "new_activity_type": request.new_activity_type,
        "new_unit": request.new_unit,
        "new_scope": request.new_scope,
        "new_category": request.new_category,
        "conversion_multiplier": request.conversion_multiplier,
    }
    missing = [key for key, value in required.items() if value is None or not str(value).strip()]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing fuel substitution fields: {', '.join(missing)}")

    unit = resolve_unit(request.new_unit or "")
    scope = resolve_scope(request.new_scope or "")
    category = resolve_category(request.new_category or "")
    if unit is None or scope is None or category is None:
        raise HTTPException(status_code=422, detail="Fuel substitution unit, scope, or category is invalid")

    return FuelSubstitution(
        new_activity_type=request.new_activity_type or "",
        new_unit=unit,
        new_scope=scope,
        new_category=category,
        conversion_multiplier=_positive_decimal(request.conversion_multiplier, "conversion_multiplier"),
        new_unit_price=(
            _non_negative_decimal(request.new_unit_price, "new_unit_price")
            if request.new_unit_price else None
        ),
    )


def _positive_decimal(value: str | None, field: str) -> Decimal:
    parsed = _parse_decimal(value, field)
    if parsed <= 0:
        raise HTTPException(status_code=422, detail=f"{field} must be greater than zero")
    return parsed


def _non_negative_decimal(value: str | None, field: str) -> Decimal:
    parsed = _parse_decimal(value, field)
    if parsed < 0:
        raise HTTPException(status_code=422, detail=f"{field} cannot be negative")
    return parsed


def _validate_upload(filename: str, content: bytes) -> None:
    if Path(filename).suffix.lower() != ".csv":
        raise HTTPException(status_code=415, detail="Only .csv files are supported")
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"CSV exceeds the configured {MAX_UPLOAD_MB} MB upload limit",
        )


@app.get("/api/health")
@app.head("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/ai/status", response_model=AIStatusResponse)
def get_ai_status() -> AIStatusResponse:
    has_key = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    model = os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    return AIStatusResponse(
        configured=has_key,
        provider="gemini" if has_key else "mock",
        model=model,
        status="active" if has_key else "offline",
        message="Gemini API connected and active" if has_key else "GEMINI_API_KEY is not set; running with deterministic mock engine",
    )


@app.post("/api/ai/config", response_model=AIConfigResponse)
def configure_ai(request: AIConfigRequest) -> AIConfigResponse:
    key = request.api_key.strip()
    if not key:
        raise HTTPException(status_code=422, detail="API key cannot be empty")

    model = request.model or os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    os.environ["GEMINI_API_KEY"] = key
    os.environ["GEMINI_MODEL"] = model

    return AIConfigResponse(
        success=True,
        message=f"Gemini API key configured successfully with model {model}",
        model=model,
    )


@app.post("/api/ai/test", response_model=AITestResponse)
def test_ai(request: AITestRequest) -> AITestResponse:
    key = request.api_key.strip()
    if not key:
        raise HTTPException(status_code=422, detail="API key cannot be empty")

    model = request.model or os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    result = test_gemini_connection(api_key=key, model_name=model)
    return AITestResponse(
        success=result["success"],
        message=result["message"],
        model=result["model"],
        response=result.get("response"),
    )



@app.post("/api/runs", response_model=RunCreateResponse, status_code=202)
async def create_run(
    file: UploadFile = File(...),
    provider: str = Query("mock"),
    year: int = Query(2024),
    country: str = Query("UK"),
) -> RunCreateResponse:
    if provider not in ALLOWED_PROVIDERS:
        raise HTTPException(status_code=422, detail="provider must be mock or gemini")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    _validate_upload(file.filename or "upload.csv", content)
    session = run_store.create(file.filename or "upload.csv", content, provider, year, country)
    return RunCreateResponse(run_id=session.run_id, status=session.status, stage=session.stage)


@app.post("/api/demo", response_model=RunCreateResponse, status_code=202)
def create_demo(
    provider: str = Query("mock"),
    year: int = Query(2024),
    country: str = Query("UK"),
    preset: str = Query("competition"),
) -> RunCreateResponse:
    if provider not in ALLOWED_PROVIDERS:
        raise HTTPException(status_code=422, detail="provider must be mock or gemini")
    project_root = Path(__file__).resolve().parent.parent
    if preset == "chicago":
        demo_path = project_root / "Chicago_Energy_Benchmarking_20260909.csv"
    elif preset == "synthetic":
        demo_path = project_root / "data" / "demo" / "synthetic_company_data.csv"
    else:
        demo_path = project_root / "data" / "demo" / "competition_demo.csv"
        if not demo_path.exists():
            demo_path = project_root / "Chicago_Energy_Benchmarking_20260909.csv"
    if not demo_path.exists():
        raise HTTPException(status_code=404, detail="Demo file not found")
    content = demo_path.read_bytes()
    session = run_store.create(demo_path.name, content, provider, year, country)
    return RunCreateResponse(run_id=session.run_id, status=session.status, stage=session.stage)


@app.get("/api/runs")
def list_runs() -> list[dict]:
    sessions = run_store.list()
    return [
        {
            "run_id": s.run_id,
            "filename": s.filename,
            "status": s.status,
            "stage": s.stage,
            "progress": s.progress,
            "provider": s.provider,
            "year": s.year,
            "country": s.country,
        }
        for s in reversed(sessions)
    ]


@app.get("/api/runs/{run_id}/status", response_model=RunStatusResponse)
def get_status(run_id: str) -> RunStatusResponse:
    session = _session(run_id)
    statistics = session.execution.statistics if session.execution else {}
    return RunStatusResponse(
        run_id=session.run_id,
        status=session.status,
        stage=session.stage,
        progress=session.progress,
        provider=session.provider,
        year=session.year,
        country=session.country,
        filename=session.filename,
        statistics=statistics,
        error=session.error,
    )


@app.get("/api/runs/{run_id}/summary", response_model=RunSummaryResponse)
def get_summary(run_id: str) -> RunSummaryResponse:
    session = _session(run_id)
    execution = _execution(session)
    parts = report_parts(execution.intelligence)
    return RunSummaryResponse(
        run_id=session.run_id,
        filename=session.filename,
        provider=session.provider,
        year=session.year,
        country=session.country,
        total_emissions=decimal(execution.batch_result.total_emissions) or "0",
        emissions_unit=execution.batch_result.emissions_unit,
        scope_totals={key.value: decimal(value) or "0" for key, value in execution.batch_result.scope_totals.items()},
        statistics=execution.statistics,
        **parts,
    )


@app.get("/api/runs/{run_id}/activities", response_model=ActivitiesResponse)
def get_activities(
    run_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=MAX_ACTIVITY_PAGE_SIZE),
    status: str | None = Query(None),
) -> ActivitiesResponse:
    session = _session(run_id)
    execution = _execution(session)
    if status not in {None, "validated", "review", "rejected"}:
        raise HTTPException(status_code=422, detail="status must be validated, review, or rejected")

    records = execution.classification_records
    if status:
        filtered = []
        for record in records:
            if record.activity_data is None:
                record_status = "rejected"
            elif (record.activity_data.metadata or {}).get("ai_needs_review"):
                record_status = "review"
            else:
                record_status = "validated"
            if record_status == status:
                filtered.append(record)
        records = filtered

    return ActivitiesResponse(
        run_id=run_id,
        total=len(records),
        offset=offset,
        limit=limit,
        activities=activities_dto(records[offset:offset + limit]),
    )


@app.get("/api/runs/{run_id}/evidence", response_model=EvidenceResponse)
def get_evidence(run_id: str) -> EvidenceResponse:
    session = _session(run_id)
    execution = _execution(session)
    source_rows = {
        record.source_row: record.raw_row
        for record in execution.classification_records
    }
    unique: dict[str, object] = {}
    for result in execution.batch_result.results:
        unique[result.result_id] = result
    for scenario in session.scenario_results:
        for result in scenario.scenario_results:
            unique[result.result_id] = result
    return EvidenceResponse(
        run_id=run_id,
        evidence=[
            evidence_dto(result, source_rows.get(result.activity.source_row))
            for result in unique.values()
        ],
        calculation_rejections=execution.calculation_rejections,
    )


@app.post("/api/runs/{run_id}/scenarios", response_model=ScenarioResponse)
def create_scenario(run_id: str, request: ScenarioRequest) -> ScenarioResponse:
    session = _session(run_id)
    execution = _execution(session)
    intervention = _intervention(request)
    definition = ScenarioDefinition(
        name=request.name,
        description=request.description,
        target_activity_ids=frozenset(request.target_activity_ids),
        intervention=intervention,
        assumptions=intervention.get_assumptions(),
    )
    try:
        result = execution.scenario_engine.evaluate(definition, execution.batch_result)
    except Exception as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    session.scenario_results.append(result)
    return ScenarioResponse(run_id=run_id, scenario=scenario_dto(result))


@app.get("/api/runs/{run_id}/recommendations", response_model=RecommendationsResponse)
def get_recommendations(run_id: str) -> RecommendationsResponse:
    session = _session(run_id)
    execution = _execution(session)
    return RecommendationsResponse(
        run_id=run_id,
        recommendations=[recommendation_dto(item) for item in execution.recommendations],
    )
