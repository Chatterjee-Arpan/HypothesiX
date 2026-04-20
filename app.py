import os
from copy import deepcopy
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()
OPENAI_GPT_KEY = os.getenv("OPENAI_GPT_KEY")

import streamlit as st

from src.agents.idea_git_agents import apply_conflict_resolutions_to_idea_result
from src.config import DEFAULT_COLLABORATORS, MAX_COLLABORATORS
from src.demo_data import DEMO_COLLABORATORS
from src.orchestrators.gladiator import runGladiatorOrchestrator
from src.orchestrators.idea_git import runIdeaGitOrchestrator
from src.ui.components import (
    conflict_radio_key,
    render_agent_pipeline,
    render_collaborator_board,
    render_export_panel,
    render_gladiator_results,
    render_header,
    render_idea_git_results,
    render_stage_divider,
)
from src.ui.styles import inject_global_styles
from src.utils.parsing import prepare_collaborator_inputs


def initialize_session_state() -> None:
    defaults = {
        "collaborator_count": DEFAULT_COLLABORATORS,
        "board_rows": [],
        "idea_result": None,
        "initial_idea_result": None,
        "resolved_idea_result": None,
        "current_mermaid_text": "",
        "conflict_resolutions": {},
        "resolution_history": [],
        "idea_error": None,
        "gladiator_result": None,
        "gladiator_error": None,
        # "gladiator_unlocked": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state["board_rows"]:
        st.session_state["board_rows"] = [
            {"name": "", "tag": "feature", "contribution": ""}
            for _ in range(st.session_state["collaborator_count"])
        ]


def sync_board_rows() -> None:
    rows = st.session_state["board_rows"]
    target_count = st.session_state["collaborator_count"]
    if len(rows) < target_count:
        rows.extend(
            {"name": "", "tag": "feature", "contribution": ""}
            for _ in range(target_count - len(rows))
        )
    elif len(rows) > target_count:
        st.session_state["board_rows"] = rows[:target_count]


def sync_board_widget_state() -> None:
    rows = st.session_state["board_rows"]
    for index, row in enumerate(rows):
        st.session_state[f"name_{index}"] = row.get("name", "")
        st.session_state[f"tag_{index}"] = row.get("tag", "feature")
        st.session_state[f"contribution_{index}"] = row.get("contribution", "")

    for index in range(len(rows), MAX_COLLABORATORS):
        st.session_state.pop(f"name_{index}", None)
        st.session_state.pop(f"tag_{index}", None)
        st.session_state.pop(f"contribution_{index}", None)


def clear_conflict_widget_state() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("conflict_choice_"):
            st.session_state.pop(key, None)


def clear_idea_state() -> None:
    clear_conflict_widget_state()
    st.session_state["idea_result"] = None
    st.session_state["initial_idea_result"] = None
    st.session_state["resolved_idea_result"] = None
    st.session_state["current_mermaid_text"] = ""
    st.session_state["conflict_resolutions"] = {}
    st.session_state["resolution_history"] = []
    st.session_state["idea_error"] = None
    st.session_state["gladiator_result"] = None
    st.session_state["gladiator_error"] = None
    # st.session_state["gladiator_unlocked"] = False


def initialize_idea_resolution_state(idea_result: dict) -> None:
    baseline_result = deepcopy(idea_result)
    st.session_state["idea_result"] = deepcopy(baseline_result)
    st.session_state["initial_idea_result"] = baseline_result
    st.session_state["resolved_idea_result"] = deepcopy(baseline_result)
    st.session_state["current_mermaid_text"] = baseline_result["cartographer"][
        "mermaid_text"
    ]
    st.session_state["conflict_resolutions"] = {}
    st.session_state["resolution_history"] = []
    st.session_state["gladiator_result"] = None
    st.session_state["gladiator_error"] = None
    clear_conflict_widget_state()


def load_demo_data() -> None:
    st.session_state["collaborator_count"] = len(DEMO_COLLABORATORS)
    st.session_state["board_rows"] = [item.model_dump() for item in DEMO_COLLABORATORS]
    sync_board_widget_state()
    clear_idea_state()


def get_active_idea_result() -> dict | None:
    return st.session_state["resolved_idea_result"] or st.session_state["idea_result"]


def build_resolution_log_entry(conflict: dict, selected_side: str) -> str:
    if selected_side == "right":
        chosen_opinion = conflict["right_opinion"]
        chosen_contributor = conflict["right_contributor"]
        rejected_opinion = conflict["left_opinion"]
        rejected_contributor = conflict["left_contributor"]
    else:
        chosen_opinion = conflict["left_opinion"]
        chosen_contributor = conflict["left_contributor"]
        rejected_opinion = conflict["right_opinion"]
        rejected_contributor = conflict["right_contributor"]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"{timestamp} | {chosen_opinion} ({chosen_contributor}) chosen over "
        f"{rejected_opinion} ({rejected_contributor})"
    )


def sync_conflict_resolution_state() -> None:
    baseline_result = st.session_state["initial_idea_result"]
    if not baseline_result:
        return

    baseline_conflicts = baseline_result["analyzer"]["conflicts"]
    current_resolutions = dict(st.session_state["conflict_resolutions"])
    next_resolutions = dict(current_resolutions)
    history = list(st.session_state["resolution_history"])
    changed = False

    for conflict in baseline_conflicts:
        widget_key = conflict_radio_key(conflict["id"])
        if widget_key not in st.session_state:
            continue

        selected_side = st.session_state[widget_key]
        previous_side = current_resolutions.get(conflict["id"])
        if selected_side == previous_side:
            continue

        if selected_side in {"left", "right"}:
            next_resolutions[conflict["id"]] = selected_side
            history.append(build_resolution_log_entry(conflict, selected_side))
        else:
            next_resolutions.pop(conflict["id"], None)
        changed = True

    if not changed:
        return

    resolved_result = apply_conflict_resolutions_to_idea_result(
        baseline_result, next_resolutions
    )
    st.session_state["conflict_resolutions"] = next_resolutions
    st.session_state["resolution_history"] = history
    st.session_state["resolved_idea_result"] = resolved_result
    st.session_state["idea_result"] = resolved_result
    st.session_state["current_mermaid_text"] = resolved_result["cartographer"][
        "mermaid_text"
    ]
    st.session_state["gladiator_result"] = None
    st.session_state["gladiator_error"] = None


def reset_to_original_graph() -> None:
    baseline_result = st.session_state["initial_idea_result"]
    if not baseline_result:
        return

    clear_conflict_widget_state()
    restored_result = deepcopy(baseline_result)
    st.session_state["conflict_resolutions"] = {}
    st.session_state["resolution_history"] = []
    st.session_state["resolved_idea_result"] = restored_result
    st.session_state["idea_result"] = restored_result
    st.session_state["current_mermaid_text"] = restored_result["cartographer"][
        "mermaid_text"
    ]
    st.session_state["gladiator_result"] = None
    st.session_state["gladiator_error"] = None


def main() -> None:
    st.set_page_config(
        page_title="HypothesiX",
        page_icon="HX",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_global_styles()
    initialize_session_state()
    sync_board_rows()

    render_header(has_api_key=bool(OPENAI_GPT_KEY))

    top_actions = st.columns([1, 1, 4])
    with top_actions[0]:
        if st.button(
            "Add Collaborator",
            use_container_width=True,
            disabled=st.session_state["collaborator_count"] >= MAX_COLLABORATORS,
        ):
            st.session_state["collaborator_count"] += 1
            sync_board_rows()
            sync_board_widget_state()
            st.rerun()
    with top_actions[1]:
        if st.button("Load Demo Data", use_container_width=True):
            load_demo_data()
            st.rerun()

    render_stage_divider(
        "Idea Git", "Input -> Mapper -> Conflict & Gap Analyzer -> Cartographer"
    )
    render_collaborator_board()

    merge_clicked = st.button("Merge Ideas", type="primary", use_container_width=True)
    if merge_clicked:
        # st.session_state["gladiator_unlocked"] = False
        st.session_state["gladiator_result"] = None
        st.session_state["gladiator_error"] = None
        try:
            collaborators, warnings = prepare_collaborator_inputs(
                st.session_state["board_rows"]
            )
            if len(collaborators) < 2:
                raise ValueError(
                    "Add at least two collaborator contributions before merging ideas."
                )
            for warning in warnings:
                st.warning(warning)

            pipeline = render_agent_pipeline(
                ["Mapper Agent", "Conflict & Gap Analyzer", "Cartographer Agent"]
            )
            result = runIdeaGitOrchestrator(
                collaborators, progress_callback=pipeline.update
            )
            initialize_idea_resolution_state(result)
            st.session_state["idea_error"] = None
        except Exception as exc:
            clear_idea_state()
            st.session_state["idea_error"] = str(exc)

    if st.session_state["idea_error"]:
        st.error(st.session_state["idea_error"])

    sync_conflict_resolution_state()
    active_idea_result = get_active_idea_result()

    if active_idea_result:
        reset_clicked = render_idea_git_results(
            active_idea_result,
            st.session_state["current_mermaid_text"],
            st.session_state["resolution_history"],
            st.session_state["conflict_resolutions"],
        )
        if reset_clicked:
            reset_to_original_graph()
            st.rerun()

        render_stage_divider(
            "Gladiator Arena",
            "Optional stress test for the current consolidated idea state.",
            intense=True,
        )

        if st.button("Run Gladiator Arena", type="primary", use_container_width=True):
            st.session_state["gladiator_result"] = None
            st.session_state["gladiator_error"] = None
            try:
                pipeline = render_agent_pipeline(
                    ["Skeptic Agent", "Execution Realist Agent", "Judge Agent"],
                    intense=True,
                )
                result = runGladiatorOrchestrator(
                    active_idea_result,
                    progress_callback=pipeline.update,
                )
                st.session_state["gladiator_result"] = result
                st.session_state["gladiator_error"] = None
            except Exception as exc:
                st.session_state["gladiator_result"] = None
                st.session_state["gladiator_error"] = str(exc)

    if st.session_state["gladiator_error"]:
        st.error(st.session_state["gladiator_error"])

    if st.session_state["gladiator_result"]:
        render_gladiator_results(st.session_state["gladiator_result"])

    if active_idea_result:
        render_export_panel(
            idea_result=active_idea_result,
            gladiator_result=st.session_state["gladiator_result"],
        )


if __name__ == "__main__":
    main()
