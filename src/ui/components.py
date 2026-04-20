import html

import streamlit as st
import streamlit.components.v1 as components

from src.utils.mermaid import ensure_mermaid_flowchart, mermaid_html

TAG_OPTIONS = [
    "feature",
    "concern",
    "assumption",
    "blocker",
    "question",
    "user problem",
    "technical note",
]


def conflict_radio_key(conflict_id: str) -> str:
    return f"conflict_choice_{conflict_id}"


def badge(label: str, kind: str) -> str:
    return f'<span class="status-badge {kind}">{html.escape(label)}</span>'


def render_header(has_api_key: bool) -> None:
    key_badge = badge("OpenAI key loaded", "stable" if has_api_key else "risky")
    stage_badges = "".join(
        [
            badge("Idea Git", "merged"),
            badge("Gladiator Arena", "risky"),
            badge("Mermaid Flowchart", "unresolved"),
            key_badge,
        ]
    )
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-brand">HypothesiX</div>
            <div class="hero-title">Merge viewpoints. Expose tension. Pressure-test the idea.</div>
            <div class="hero-subtitle">
                A premium multi-agent workshop for turning six to eight collaborator perspectives into one clear project state,
                then optionally sending that state into a separate Gladiator Arena for stress testing.
            </div>
            <div class="badge-row">{stage_badges}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stage_divider(title: str, note: str, intense: bool = False) -> None:
    classes = "section-shell arena-shell" if intense else "section-shell"
    st.markdown(
        f"""
        <div class="{classes}">
            <div class="section-kicker">Stage</div>
            <div class="section-title">{html.escape(title)}</div>
            <div class="section-note">{html.escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_collaborator_board() -> None:
    st.markdown("### Collaborator Input Board")
    rows = st.session_state["board_rows"]

    for row_start in range(0, len(rows), 3):
        grid_cols = st.columns(3, gap="large")

        for col_offset, col in enumerate(grid_cols):
            index = row_start + col_offset
            if index >= len(rows):
                continue

            row = rows[index]
            name_key = f"name_{index}"
            tag_key = f"tag_{index}"
            contribution_key = f"contribution_{index}"

            current_tag = st.session_state.get(tag_key, row.get("tag", TAG_OPTIONS[0]))
            if current_tag not in TAG_OPTIONS:
                current_tag = TAG_OPTIONS[0]
                st.session_state[tag_key] = current_tag

            with col:
                st.markdown(f"#### Collaborator {index + 1}")

                st.text_input(
                    "Name",
                    key=name_key,
                    placeholder=f"Contributor {index + 1}",
                    label_visibility="collapsed",
                )
                row["name"] = st.session_state[name_key]

                st.selectbox(
                    "Tag",
                    TAG_OPTIONS,
                    index=TAG_OPTIONS.index(current_tag),
                    key=tag_key,
                    label_visibility="collapsed",
                )
                row["tag"] = st.session_state[tag_key]

                st.text_area(
                    "Contribution",
                    key=contribution_key,
                    height=180,
                    placeholder="Add the collaborator's perspective, concern, blocker, or proposal.",
                    label_visibility="collapsed",
                )
                row["contribution"] = st.session_state[contribution_key]


class PipelineRenderer:
    def __init__(self, steps: list[str], intense: bool = False) -> None:
        self.steps = steps
        self.states = {step: "pending" for step in steps}
        self.intense = intense

        cols = st.columns(len(steps), gap="medium")
        self.placeholders = {}

        for step, col in zip(steps, cols):
            with col:
                self.placeholders[step] = st.empty()

        self.render_all()

    def render_all(self) -> None:
        for step in self.steps:
            self.placeholders[step].markdown(
                f'<div class="pipeline-step pipeline-step-compact {self.states[step]}"><strong>{html.escape(step)}</strong><br>{self._message(step)}</div>',
                unsafe_allow_html=True,
            )

    def _message(self, step: str) -> str:
        state = self.states[step]
        if state == "running":
            return "Processing current state..."
        if state == "completed":
            return "Completed and passed downstream."
        return "Queued and waiting."

    def update(self, step: str, status: str) -> None:
        self.states[step] = status
        self.render_all()


def render_agent_pipeline(steps: list[str], intense: bool = False) -> PipelineRenderer:
    return PipelineRenderer(steps, intense=intense)


def render_list_card(title: str, items: list[str], empty_copy: str, kind: str) -> None:
    st.markdown(
        f'<div class="result-card"><div class="result-title">{html.escape(title)}</div>',
        unsafe_allow_html=True,
    )
    if items:
        for item in items:
            st.markdown(
                f'<div class="list-chip">{html.escape(item)}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"<div class='result-value'>{html.escape(empty_copy)}</div>",
            unsafe_allow_html=True,
        )
    st.markdown(badge(kind, kind), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def render_keyword_panel(title: str, items: list[str], empty_copy: str) -> None:
    if items:
        chips = "".join(
            f'<span class="keyword-chip">{html.escape(item)}</span>'
            for item in items
        )
        body = f'<div class="keyword-row">{chips}</div>'
    else:
        body = f'<div class="result-value">{html.escape(empty_copy)}</div>'

    st.markdown(
        f"""
        <div class="result-card result-card-wide">
            <div class="result-title">{html.escape(title)}</div>
            {body}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_bullet_panel(
    title: str,
    items: list[str],
    empty_copy: str,
    tone_class: str,
    badge_label: str,
    badge_kind: str,
) -> None:
    if items:
        bullets = "".join(f"<li>{html.escape(item)}</li>" for item in items)
        body = f'<ul class="bullet-list">{bullets}</ul>'
    else:
        body = f'<div class="result-value">{html.escape(empty_copy)}</div>'

    st.markdown(
        f"""
        <div class="result-card tone-card {tone_class}">
            <div class="panel-topline">
                <div class="result-title">{html.escape(title)}</div>
                {badge(badge_label, badge_kind)}
            </div>
            {body}
        </div>
        """,
        unsafe_allow_html=True,
    )


def conflict_display_label(conflict: dict) -> str:
    return str(conflict.get("display_label", "Conflict")).strip() or "Conflict"

def conflict_map_label(conflict: dict) -> str:
    left_opinion = str(conflict.get("left_opinion", "Left opinion")).strip()
    left_contributor = str(conflict.get("left_contributor", "Contributor")).strip()
    right_opinion = str(conflict.get("right_opinion", "Right opinion")).strip()
    right_contributor = str(conflict.get("right_contributor", "Contributor")).strip()

    return f"{left_opinion} ({left_contributor}) vs {right_opinion} ({right_contributor})"


def conflict_option_label(conflict: dict, side: str) -> str:
    if side == "right":
        opinion = conflict.get("right_opinion", "Right opinion")
        contributor = conflict.get("right_contributor", "Contributor")
    else:
        opinion = conflict.get("left_opinion", "Left opinion")
        contributor = conflict.get("left_contributor", "Contributor")
    return f"{opinion} ({contributor})"


def render_conflict_resolution_panel(
    conflicts: list[dict],
    resolution_history: list[str],
    conflict_resolutions: dict[str, str],
) -> bool:
    st.markdown("### Resolve Conflicts")
    header_cols = st.columns([4, 1])
    with header_cols[0]:
        st.markdown(
            '<div class="conflict-panel-note">Choose a side for any unresolved conflict. The graph above will update automatically. Click on Decision Log to check Conflict Resolution History.</div>',
            unsafe_allow_html=True,
        )
    with header_cols[1]:
        reset_clicked = st.button("Reset to Original Graph", use_container_width=True)

    if not conflicts:
        st.info("No structured conflicts were surfaced in the current idea map.")
    else:
        for index, conflict in enumerate(conflicts, start=1):
            selected_side = conflict_resolutions.get(conflict["id"])
            badge_markup = (
                badge("resolved", "stable")
                if selected_side
                else badge("unresolved", "unresolved")
            )
            st.markdown(
                f"""
                <div class="conflict-resolution-card">
                    <div class="panel-topline">
                        <div class="result-title">Conflict {index}</div>
                        {badge_markup}
                    </div>
                    <div class="conflict-card-label">{html.escape(conflict_display_label(conflict))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.radio(
                "Choose a side",
                options=["left", "right"],
                index=None if selected_side is None else ["left", "right"].index(selected_side),
                format_func=lambda side, conflict=conflict: conflict_option_label(
                    conflict, side
                ),
                key=conflict_radio_key(conflict["id"]),
                label_visibility="collapsed",
            )

    with st.expander("Decision Log", expanded=False):
        if resolution_history:
            for entry in reversed(resolution_history):
                st.markdown(
                    f'<div class="history-entry">{html.escape(entry)}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No conflict decisions recorded yet.")

    return reset_clicked


def render_idea_git_results(
    result: dict,
    current_mermaid_text: str,
    resolution_history: list[str],
    conflict_resolutions: dict[str, str],
) -> bool:
    mapper = result["mapper"]
    analyzer = result["analyzer"]
    cartographer = result["cartographer"]
    conflict_labels = [
    conflict_map_label(conflict) for conflict in analyzer["conflicts"]
]

    st.markdown("### Consolidated Idea State")

    # 1) Merged Idea - full width single box
    st.markdown(
        f"""
        <div class="result-card result-card-wide">
            <div class="panel-topline">
                <div class="result-title">Merged Idea</div>
                {badge("merged", "merged")}
            </div>
            <div class="result-value">{html.escape(mapper['merged_idea'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2) Major Themes - single full width keyword box
    render_keyword_panel(
        "Major Themes",
        mapper["major_themes"],
        "No themes surfaced.",
    )

    # 3) 3 side-by-side boxes
    row = st.columns(3)
    with row[0]:
        render_bullet_panel(
            "Conflict Map",
            conflict_labels,
            "No material conflicts surfaced.",
            "conflict-tone",
            "conflict",
            "conflict",
        )
    with row[1]:
        render_bullet_panel(
            "Gap Map",
            analyzer["gaps"],
            "No major gaps surfaced.",
            "gap-tone",
            "gap",
            "gap",
        )
    with row[2]:
        render_bullet_panel(
            "Risk Flags",
            analyzer["risk_flags"],
            "No major risk flags surfaced.",
            "risk-tone",
            "risky",
            "risky",
        )

    # Keep Mermaid below, if you still want the flowchart section
    st.markdown("### Idea Map")
    mermaid_text = ensure_mermaid_flowchart(
        current_mermaid_text or cartographer["mermaid_text"]
    )
    try:
        components.html(mermaid_html(mermaid_text), height=520, scrolling=True)
    except Exception:
        st.warning("Mermaid rendering fell back to plain text because the chart could not be displayed.")

    with st.expander("Mermaid Export Text", expanded=False):
        st.code(mermaid_text, language="mermaid")

    return render_conflict_resolution_panel(
        analyzer["conflicts"],
        resolution_history,
        conflict_resolutions,
    )


def render_gladiator_results(result: dict) -> None:
    skeptic = result["skeptic"]
    execution = result["execution_realist"]
    judge = result["judge"]

    st.markdown("### Gladiator Verdict")

    # 1) Full-width verdict box
    st.markdown(
        f"""
        <div class="result-card result-card-wide gladiator-verdict-tone">
            <div class="panel-topline">
                <div class="result-title">Final Verdict</div>
                {badge("verdict", "stable")}
            </div>
            <div class="result-value">{html.escape(judge['final_verdict'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2) Full-width confidence box
    st.markdown(
        f"""
        <div class="result-card result-card-wide gladiator-confidence-tone">
            <div class="panel-topline">
                <div class="result-title">Confidence Level</div>
                {badge("confidence", "unresolved")}
            </div>
            <div class="result-value">{html.escape(judge['confidence_level'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # spacing
    st.markdown('<div class="gladiator-row-gap"></div>', unsafe_allow_html=True)

    # 3) First 3-card row
    row_one = st.columns(3, gap="large")
    with row_one[0]:
        render_bullet_panel(
            "Conceptual Attacks",
            skeptic["conceptual_attacks"],
            "No conceptual attacks surfaced.",
            "gladiator-attack-tone",
            "conflict",
            "conflict",
        )
    with row_one[1]:
        render_bullet_panel(
            "Weak Assumptions",
            skeptic["weak_assumptions"],
            "No weak assumptions surfaced.",
            "gladiator-assumption-tone",
            "risky",
            "risky",
        )
    with row_one[2]:
        render_bullet_panel(
            "Unsupported Claims",
            skeptic["unsupported_claims"],
            "No unsupported claims surfaced.",
            "gladiator-claims-tone",
            "gap",
            "gap",
        )

    st.markdown('<div class="gladiator-row-gap"></div>', unsafe_allow_html=True)

    # 4) Second 3-card row
    row_two = st.columns(3, gap="large")
    with row_two[0]:
        render_bullet_panel(
            "Execution Risks",
            execution["execution_risks"],
            "No execution risks surfaced.",
            "gladiator-execution-tone",
            "risky",
            "risky",
        )
    with row_two[1]:
        render_bullet_panel(
            "Adoption Risks",
            execution["adoption_risks"],
            "No adoption risks surfaced.",
            "gladiator-adoption-tone",
            "risky",
            "risky",
        )
    with row_two[2]:
        render_bullet_panel(
            "Scope Risks",
            execution["scope_risks"],
            "No scope risks surfaced.",
            "gladiator-scope-tone",
            "conflict",
            "conflict",
        )

    st.markdown('<div class="gladiator-row-gap"></div>', unsafe_allow_html=True)

    # 5) Bottom row
    row_three = st.columns(3, gap="large")
    with row_three[0]:
        st.markdown(
            f"""
            <div class="result-card tone-card gladiator-danger-tone">
                <div class="panel-topline">
                    <div class="result-title">Most Dangerous Assumption</div>
                    {badge("critical", "risky")}
                </div>
                <div class="result-value">{html.escape(judge['most_dangerous_assumption'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with row_three[1]:
        st.markdown(
            f"""
            <div class="result-card tone-card gladiator-step-tone">
                <div class="panel-topline">
                    <div class="result-title">Smallest Validation Step</div>
                    {badge("next step", "stable")}
                </div>
                <div class="result-value">{html.escape(judge['smallest_validation_step'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with row_three[2]:
        render_bullet_panel(
            "Top Risks Ranked",
            judge["top_risks_ranked"],
            "No top risks ranked.",
            "gladiator-toprisks-tone",
            "priority",
            "risky",
        )


def render_export_panel(idea_result: dict, gladiator_result: dict | None) -> None:
    st.markdown("### Export")
    st.markdown('<div class="export-card">Copy-friendly outputs for handoff, docs, or demos.</div>', unsafe_allow_html=True)
    st.text_area(
        "Merged Summary",
        value=idea_result["mapper"]["merged_idea"],
        height=140,
    )
    st.text_area(
        "Mermaid Flowchart Text",
        value=idea_result["cartographer"]["mermaid_text"],
        height=240,
    )
    verdict = ""
    if gladiator_result:
        verdict = gladiator_result["judge"]["final_verdict"]
    st.text_area("Gladiator Verdict", value=verdict, height=120)
