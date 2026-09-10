# Superpowers Core Directive

## Methodology & Engineering Discipline

This workspace enforces the **Superpowers** software development methodology. All AI agents working on this codebase must adhere strictly to these core tenets:

### 1. The Rule of Skill Invocation
- If a skill applies to your task, you MUST invoke and follow the skill.
- Before coding new features: brainstorm or structure the implementation plan first.
- For bugs/failures: use `systematic-debugging`.
- For new features/refactoring: use `test-driven-development`.

### 2. Test-Driven Development (The Iron Law)
```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```
- Write a minimal failing test first showing expected behavior.
- Run the test and verify it fails for the expected reason.
- Write minimal implementation code to pass the test.
- Verify all tests pass (Green).
- Refactor and clean up while staying Green.

### 3. Systematic Debugging (Root Cause First)
```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```
- Read full error messages, stack traces, and line numbers.
- Reproduce the failure consistently.
- Inspect recent changes, git diff, and config modifications.
- Formulate a testable hypothesis and gather evidence before changing code. Symptom patching is unacceptable.

### 4. Verification Before Completion
```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```
- Never claim a task, fix, or build is working without fresh execution output.
- Run the full verification command and inspect output and exit code before making assertions.
- "Evidence before claims, always."

### 5. Structured Planning & Incremental Execution
- Break complex requirements into bite-sized, atomic, verifiable implementation steps.
- Maintain clear acceptance criteria and verification gates for each milestone.
