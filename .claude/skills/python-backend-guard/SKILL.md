# python-backend-guard

Use this skill for all Python backend work.

Architecture rules:
- Keep handlers thin.
- Put orchestration in services.
- Put DB access in repositories.
- Keep pure processing logic in pipeline/ranking modules.
- Do not leak external library specific types outside their collector layer.
- Prefer typed dataclasses / pydantic models where appropriate.
- Keep files small and focused.
- Do not introduce unnecessary frameworks.
