from copy import deepcopy

from langchain_core.messages import HumanMessage, SystemMessage

from src.models import get_chat_model
from src.prompts import (
    SYSTEM_STYLE,
    cartographer_prompt,
    conflict_gap_prompt,
    mapper_prompt,
)
from src.schemas import (
    CartographerOutput,
    CollaboratorInput,
    ConflictGapOutput,
    ConflictItem,
    GraphEdge,
    GraphNode,
    MapperOutput,
)
from src.utils.mermaid import ensure_mermaid_flowchart

CONFLICT_KIND = "conflict"
RESOLVED_CONFLICT_KIND = "resolved_conflict"


def _escape_mermaid_label(text: str) -> str:
    return (text or "").replace('"', "'").strip()


def _node_to_mermaid(node: GraphNode) -> str:
    label = _escape_mermaid_label(node.label)
    kind = (node.kind or "").strip().lower()

    if kind == CONFLICT_KIND:
        return f'    {node.id}{{"{label}"}}'

    return f'    {node.id}["{label}"]'


def _edge_to_mermaid(edge: GraphEdge) -> str:
    edge_label = _escape_mermaid_label(edge.label)
    if edge_label:
        return f'    {edge.source} -->|"{edge_label}"| {edge.target}'
    return f"    {edge.source} --> {edge.target}"


def _pick_anchor_node_id(nodes: list[GraphNode]) -> str | None:
    for node in nodes:
        if (node.kind or "").strip().lower() in {"goal", "root", "theme"}:
            return node.id
    return nodes[0].id if nodes else None


def _normalize_conflict_nodes(
    nodes: list[GraphNode],
    edges: list[GraphEdge],
    conflicts: list[ConflictItem],
) -> tuple[list[GraphNode], list[GraphEdge]]:
    normalized_nodes = [node.model_copy() for node in nodes]
    normalized_edges = [edge.model_copy() for edge in edges]
    conflict_indexes = [
        index
        for index, node in enumerate(normalized_nodes)
        if (node.kind or "").strip().lower() == CONFLICT_KIND
    ]
    edge_id_map: dict[str, str] = {}

    for node_index, conflict in zip(conflict_indexes, conflicts):
        old_id = normalized_nodes[node_index].id
        edge_id_map[old_id] = conflict.id
        normalized_nodes[node_index] = normalized_nodes[node_index].model_copy(
            update={
                "id": conflict.id,
                "label": conflict.display_label,
                "kind": CONFLICT_KIND,
            }
        )

    if edge_id_map:
        normalized_edges = [
            edge.model_copy(
                update={
                    "source": edge_id_map.get(edge.source, edge.source),
                    "target": edge_id_map.get(edge.target, edge.target),
                }
            )
            for edge in normalized_edges
        ]

    existing_ids = {node.id for node in normalized_nodes}
    anchor_id = _pick_anchor_node_id(normalized_nodes)
    for conflict in conflicts[len(conflict_indexes):]:
        if conflict.id in existing_ids:
            continue
        normalized_nodes.append(
            GraphNode(
                id=conflict.id,
                label=conflict.display_label,
                kind=CONFLICT_KIND,
            )
        )
        existing_ids.add(conflict.id)
        if anchor_id:
            normalized_edges.append(
                GraphEdge(source=anchor_id, target=conflict.id, label="conflict")
            )

    return normalized_nodes, normalized_edges


def build_mermaid_from_graph(
    nodes: list[GraphNode],
    edges: list[GraphEdge],
) -> str:
    lines = ["flowchart TD"]

    for node in nodes:
        lines.append(_node_to_mermaid(node))

    for edge in edges:
        lines.append(_edge_to_mermaid(edge))

    conflict_ids = [
        node.id
        for node in nodes
        if (node.kind or "").strip().lower() == CONFLICT_KIND
    ]
    resolved_conflict_ids = [
        node.id
        for node in nodes
        if (node.kind or "").strip().lower() == RESOLVED_CONFLICT_KIND
    ]

    if conflict_ids or resolved_conflict_ids:
        lines.append("")
    if conflict_ids:
        lines.append(
            "    classDef conflict fill:#3a1d28,stroke:#fb7185,color:#ffe4e6,stroke-width:1.5px;"
        )
        lines.append(f"    class {','.join(conflict_ids)} conflict;")
    if resolved_conflict_ids:
        lines.append(
            "    classDef resolvedConflict fill:#142a22,stroke:#34d399,color:#d1fae5,stroke-width:1.5px;"
        )
        lines.append(f"    class {','.join(resolved_conflict_ids)} resolvedConflict;")

    return "\n".join(lines)


def _selected_opinion(conflict: ConflictItem, side: str | None) -> str:
    if side == "right":
        return conflict.right_opinion
    return conflict.left_opinion


def normalize_graph_from_cartographer(
    cartographer_output: CartographerOutput,
    conflicts: list[ConflictItem],
) -> CartographerOutput:
    nodes = [GraphNode.model_validate(node) for node in cartographer_output.graph_nodes]
    edges = [GraphEdge.model_validate(edge) for edge in cartographer_output.graph_edges]
    normalized_nodes, normalized_edges = _normalize_conflict_nodes(nodes, edges, conflicts)
    generated_mermaid = build_mermaid_from_graph(normalized_nodes, normalized_edges)

    cartographer_output.graph_nodes = normalized_nodes
    cartographer_output.graph_edges = normalized_edges
    cartographer_output.mermaid_text = ensure_mermaid_flowchart(generated_mermaid)
    return cartographer_output


def apply_conflict_resolutions_to_idea_result(
    baseline_idea_result: dict,
    conflict_resolutions: dict[str, str],
) -> dict:
    resolved_result = deepcopy(baseline_idea_result)
    conflicts = [
        ConflictItem.model_validate(item)
        for item in resolved_result["analyzer"]["conflicts"]
    ]
    conflict_map = {item.id: item for item in conflicts}
    nodes = [
        GraphNode.model_validate(node)
        for node in resolved_result["cartographer"]["graph_nodes"]
    ]
    edges = [
        GraphEdge.model_validate(edge)
        for edge in resolved_result["cartographer"]["graph_edges"]
    ]

    updated_nodes: list[GraphNode] = []
    updated_conflicts: list[ConflictItem] = []
    for conflict in conflicts:
        updated_conflicts.append(
            conflict.model_copy(
                update={"selected_side": conflict_resolutions.get(conflict.id)}
            )
        )
    updated_conflict_map = {item.id: item for item in updated_conflicts}

    for node in nodes:
        node_kind = (node.kind or "").strip().lower()
        if node.id in conflict_map and node_kind in {
            CONFLICT_KIND,
            RESOLVED_CONFLICT_KIND,
        }:
            conflict = updated_conflict_map[node.id]
            if conflict.selected_side:
                updated_nodes.append(
                    node.model_copy(
                        update={
                            "label": _selected_opinion(conflict, conflict.selected_side),
                            "kind": RESOLVED_CONFLICT_KIND,
                        }
                    )
                )
            else:
                updated_nodes.append(
                    node.model_copy(
                        update={
                            "label": conflict.display_label,
                            "kind": CONFLICT_KIND,
                        }
                    )
                )
        else:
            updated_nodes.append(node.model_copy())

    resolved_result["analyzer"]["conflicts"] = [
        conflict.model_dump() for conflict in updated_conflicts
    ]
    resolved_result["cartographer"]["graph_nodes"] = [
        node.model_dump() for node in updated_nodes
    ]
    resolved_result["cartographer"]["graph_edges"] = [
        edge.model_dump() for edge in edges
    ]
    resolved_result["cartographer"]["mermaid_text"] = ensure_mermaid_flowchart(
        build_mermaid_from_graph(updated_nodes, edges)
    )
    resolved_result["conflict_resolutions"] = {
        conflict_id: side
        for conflict_id, side in conflict_resolutions.items()
        if side in {"left", "right"}
    }
    return resolved_result


def run_mapper_agent(collaborators: list[CollaboratorInput]) -> MapperOutput:
    model = get_chat_model("mapper").with_structured_output(MapperOutput)
    return model.invoke(
        [
            SystemMessage(content=SYSTEM_STYLE),
            HumanMessage(content=mapper_prompt(collaborators)),
        ]
    )


def run_conflict_gap_agent(
    collaborators: list[CollaboratorInput],
    mapper_output: MapperOutput,
) -> ConflictGapOutput:
    model = get_chat_model("conflict_gap").with_structured_output(ConflictGapOutput)
    return model.invoke(
        [
            SystemMessage(content=SYSTEM_STYLE),
            HumanMessage(
                content=conflict_gap_prompt(collaborators, mapper_output.merged_idea)
            ),
        ]
    )


def run_cartographer_agent(
    mapper_output: MapperOutput,
    analyzer_output: ConflictGapOutput,
) -> CartographerOutput:
    model = get_chat_model("cartographer").with_structured_output(CartographerOutput)
    output = model.invoke(
        [
            SystemMessage(content=SYSTEM_STYLE),
            HumanMessage(
                content=cartographer_prompt(
                    merged_idea=mapper_output.merged_idea,
                    themes=mapper_output.major_themes,
                    assumptions=mapper_output.assumptions_detected,
                    open_questions=mapper_output.open_questions,
                    conflicts=analyzer_output.conflicts,
                    gaps=analyzer_output.gaps,
                )
            ),
        ]
    )
    return normalize_graph_from_cartographer(output, analyzer_output.conflicts)
