from src.schemas import CollaboratorInput

DEFAULT_TAG = "feature"


def prepare_collaborator_inputs(rows: list[dict]) -> tuple[list[CollaboratorInput], list[str]]:
    collaborators: list[CollaboratorInput] = []
    warnings: list[str] = []

    for index, row in enumerate(rows, start=1):
        contribution = str(row.get("contribution", "")).strip()
        if not contribution:
            continue
        name = str(row.get("name", "")).strip() or f"Collaborator {index}"
        tag = str(row.get("tag", DEFAULT_TAG)).strip() or DEFAULT_TAG
        collaborators.append(
            CollaboratorInput(name=name, contribution=contribution, tag=tag)
        )

    if collaborators and len(collaborators) < 6:
        warnings.append(
            "Fewer than six filled collaborator inputs were provided. The orchestrator will run, but synthesis confidence may be lower."
        )

    vague_count = sum(1 for item in collaborators if len(item.contribution.split()) < 8)
    if vague_count:
        warnings.append(
            f"{vague_count} contribution(s) are very brief. The app will preserve uncertainty where inputs are underspecified."
        )

    return collaborators, warnings
