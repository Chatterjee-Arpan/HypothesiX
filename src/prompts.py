from src.schemas import CollaboratorInput, ConflictItem


SYSTEM_STYLE = (
    "You are an expert product and research synthesis agent. "
    "Return concise, concrete, structured outputs. "
    "Acknowledge uncertainty clearly and avoid generic fluff."
)


def format_collaborators(collaborators: list[CollaboratorInput]) -> str:
    blocks = []
    for index, item in enumerate(collaborators, start=1):
        blocks.append(
            f"[{index}] name={item.name}\n"
            f"tag={item.tag or 'feature'}\n"
            f"contribution={item.contribution.strip()}"
        )
    return "\n\n".join(blocks)


def mapper_prompt(collaborators: list[CollaboratorInput]) -> str:
    return (
        "Merge the collaborator viewpoints into one usable project idea.\n"
        "Focus on core goal, repeated themes, normalized overlaps, assumptions, and open questions.\n"
        "Keep the merged idea crisp and demo-safe.\n\n"
        "Formatting rules:\n"
        "- core_goal: one concise sentence\n"
        "- merged_idea: one short, clear paragraph\n"
        "- major_themes: return 4 to 6 short keyword phrases only\n"
        "- each major_themes item must be 1 to 2 words\n"
        "- do not write full sentences for major_themes\n"
        "- assumptions_detected: short bullet-style items\n"
        "- open_questions: short bullet-style items\n\n"
        "Good major_themes examples:\n"
        '- "Privacy-first identity"\n'
        '- "Data ownership"\n'
        '- "UX friction"\n'
        '- "Regulatory compliance"\n'
        '- "Trust and adoption"\n\n'
        f"Collaborator inputs:\n{format_collaborators(collaborators)}"
    )


def conflict_gap_prompt(collaborators: list[CollaboratorInput], merged_idea: str) -> str:
    return (
        "Analyze the merged idea and the original collaborator inputs.\n"
        "Find disagreements, conflicting assumptions, scope mismatches, missing pieces, missing owners, "
        "missing evidence, unresolved risks, and unresolved questions.\n"
        "Prefer short concrete bullets and stable structured conflicts.\n\n"
        "Formatting rules:\n"
        "- conflicts must be returned as structured objects, not plain strings\n"
        "- each conflict object must include:\n"
        "  id: stable slug like conflict_1\n"
        "  display_label: short 'Opinion A vs Opinion B' label without contributor names\n"
        "  left_opinion: 2 to 5 words\n"
        "  left_contributor: exact contributor name\n"
        "  right_opinion: 2 to 5 words\n"
        "  right_contributor: exact contributor name\n"
        "- never omit left_contributor or right_contributor when a conflict is emitted\n"
        "- do not include contributor names inside display_label\n"
        "- do not write long explanations inside the opinion fields\n"
        "- only emit conflicts when there is a real disagreement or incompatible assumption\n"
        "- gaps: short concrete bullets only\n"
        "- unresolved_questions: short concrete bullets only\n"
        "- risk_flags: short concrete bullets only\n\n"
        "Conflict examples:\n"
        '- {id: "conflict_1", display_label: "Privacy-first onboarding vs low-friction signup", left_opinion: "Privacy-first onboarding", left_contributor: "Alice", right_opinion: "Low-friction signup", right_contributor: "Bob"}\n'
        '- {id: "conflict_2", display_label: "Flexible workflow vs fixed process", left_opinion: "Flexible workflow", left_contributor: "Asha", right_opinion: "Fixed process", right_contributor: "Leo"}\n\n'
        f"Merged idea:\n{merged_idea}\n\n"
        f"Collaborator inputs:\n{format_collaborators(collaborators)}"
    )


def format_conflicts_for_cartographer(conflicts: list[ConflictItem]) -> str:
    lines = []
    for item in conflicts:
        lines.append(
            f"id={item.id} | display_label={item.display_label} | "
            f"left={item.left_opinion} ({item.left_contributor}) | "
            f"right={item.right_opinion} ({item.right_contributor})"
        )
    return "\n".join(lines) if lines else "None"


def cartographer_prompt(
    merged_idea: str,
    themes: list[str],
    assumptions: list[str],
    open_questions: list[str],
    conflicts: list[ConflictItem],
    gaps: list[str],
) -> str:
    return (
        "Convert the project state into a readable graph for Mermaid flowchart rendering.\n"
        "Represent goals, themes, assumptions, blockers, gaps, and open questions as scan-friendly graph nodes.\n"
        "Keep the graph visually clean, compact, and easy to read.\n\n"
        "Conflict rendering rules:\n"
        "- Represent each conflict as a terminal conflict node, not as a downstream continuation.\n"
        "- Create exactly one graph node for each provided conflict item.\n"
        "- For each conflict node, use the provided conflict id exactly as the node id.\n"
        '- For each conflict node, use the provided display_label exactly as the node label in the form "Opinion A vs Opinion B".\n'
        '- Set kind="conflict" for every conflict node.\n'
        "- Do not add contributor names inside the conflict node text.\n"
        "- Conflict nodes must be terminal leaves.\n"
        "- Do not expand conflict nodes into extra downstream child boxes.\n\n"
        "Layout rules:\n"
        "- Keep the merged idea or root goal near the top.\n"
        "- Put major themes as primary branches.\n"
        "- Place assumptions, gaps, and open questions as supporting child nodes where relevant.\n"
        "- Keep labels short and scannable.\n"
        "- Avoid redundant nodes and avoid clutter.\n\n"
        f"Merged idea:\n{merged_idea}\n\n"
        f"Themes: {themes}\n"
        f"Assumptions: {assumptions}\n"
        f"Open questions: {open_questions}\n"
        f"Conflicts:\n{format_conflicts_for_cartographer(conflicts)}\n"
        f"Gaps: {gaps}"
    )


def skeptic_prompt(merged_state: dict) -> str:
    return (
        "Stress-test the consolidated idea. Attack weak logic, brittle assumptions, and unsupported claims "
        "without being theatrical.\n\n"
        f"Consolidated state:\n{merged_state}"
    )


def execution_realist_prompt(merged_state: dict) -> str:
    return (
        "Challenge feasibility, execution complexity, adoption, operations, coordination, and scope.\n"
        "Keep notes concise and specific.\n\n"
        f"Consolidated state:\n{merged_state}"
    )


def judge_prompt(merged_state: dict, skeptic_output: dict, execution_output: dict) -> str:
    return (
        "Synthesize the Skeptic and Execution Realist outputs into a sharp verdict.\n"
        "Rank the top three risks, identify the most dangerous assumption, and recommend the smallest useful validation step.\n\n"
        f"Consolidated state:\n{merged_state}\n\n"
        f"Skeptic output:\n{skeptic_output}\n\n"
        f"Execution Realist output:\n{execution_output}"
    )
