from typing import Any, Literal, Optional, TypedDict

from pydantic import BaseModel, Field


class CollaboratorInput(BaseModel):
    name: str = Field(..., description="Collaborator display name.")
    contribution: str = Field(..., description="Free-text collaborator contribution.")
    tag: Optional[str] = Field(default="feature", description="Optional contribution tag.")


class MapperOutput(BaseModel):
    core_goal: str = Field(
        ...,
        description="One concise sentence describing the central project goal."
    )
    major_themes: list[str] = Field(
        ...,
        description=(
            "Return 4 to 6 short keyword-style themes only. "
            "Each item must be 1 to 4 words, not a full sentence. "
            "Examples: 'Privacy-first identity', 'Data ownership', 'UX friction'."
        ),
    )
    merged_idea: str = Field(
        ...,
        description="A crisp merged project idea in a short paragraph."
    )
    assumptions_detected: list[str] = Field(
        ...,
        description="Short bullet points listing explicit or implicit assumptions."
    )
    open_questions: list[str] = Field(
        ...,
        description="Short bullet points listing unresolved questions."
    )


class ConflictItem(BaseModel):
    id: str = Field(
        ...,
        description="Stable conflict identifier such as conflict_1."
    )
    display_label: str = Field(
        ...,
        description=(
            "Short human-readable label in the form "
            "'Opinion A vs Opinion B' without contributor names."
        ),
    )
    left_opinion: str = Field(
        ...,
        description="Left-side opinion label in 2 to 5 words."
    )
    left_contributor: str = Field(
        ...,
        description="Contributor name exactly as provided in the input."
    )
    right_opinion: str = Field(
        ...,
        description="Right-side opinion label in 2 to 5 words."
    )
    right_contributor: str = Field(
        ...,
        description="Contributor name exactly as provided in the input."
    )
    selected_side: Literal["left", "right"] | None = Field(
        default=None,
        description="Optional user selection applied later in deterministic conflict resolution.",
    )


class ConflictGapOutput(BaseModel):
    conflicts: list[ConflictItem] = Field(
        ...,
        description=(
            "Structured conflicts with stable ids and short opinion labels so the UI can "
            "resolve them deterministically without re-running the model."
        ),
    )
    gaps: list[str] = Field(
        ...,
        description=(
            "Short concrete bullet points for missing pieces, unclear owners, "
            "missing evidence, or unresolved execution gaps."
        ),
    )
    unresolved_questions: list[str] = Field(
        ...,
        description="Short concrete unresolved questions that still need answers."
    )
    risk_flags: list[str] = Field(
        ...,
        description="Short concrete risk bullets, not long paragraphs."
    )


class GraphNode(BaseModel):
    id: str = Field(..., description="Stable node identifier.")
    label: str = Field(..., description="Short graph label.")
    kind: str = Field(
        ...,
        description=(
            "Graph node kind such as goal, theme, assumption, gap, question, "
            "conflict, or resolved_conflict."
        ),
    )


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str = ""


class CartographerOutput(BaseModel):
    graph_nodes: list[GraphNode]
    graph_edges: list[GraphEdge]
    mermaid_text: str
    concise_state_summary: str


class SkepticOutput(BaseModel):
    conceptual_attacks: list[str]
    weak_assumptions: list[str]
    unsupported_claims: list[str]


class ExecutionRealistOutput(BaseModel):
    execution_risks: list[str]
    adoption_risks: list[str]
    scope_risks: list[str]
    feasibility_notes: list[str]


class JudgeOutput(BaseModel):
    top_risks_ranked: list[str]
    most_dangerous_assumption: str
    smallest_validation_step: str
    final_verdict: str
    confidence_level: str


class IdeaGitState(TypedDict, total=False):
    collaborators: list[CollaboratorInput]
    mapper_output: MapperOutput
    analyzer_output: ConflictGapOutput
    cartographer_output: CartographerOutput
    errors: list[str]


class GladiatorState(TypedDict, total=False):
    merged_state: dict[str, Any]
    skeptic_output: SkepticOutput
    execution_output: ExecutionRealistOutput
    judge_output: JudgeOutput
    errors: list[str]
