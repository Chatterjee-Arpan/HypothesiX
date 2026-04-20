from typing import Callable

from langgraph.graph import END, START, StateGraph

from src.agents.gladiator_agents import (
    run_execution_realist_agent,
    run_judge_agent,
    run_skeptic_agent,
)
from src.schemas import GladiatorState


# Gladiator orchestrator starts here.
def runGladiatorOrchestrator(
    mergedIdeaState: dict,
    progress_callback: Callable[[str, str], None] | None = None,
) -> dict:
    def signal(agent_name: str, status: str) -> None:
        if progress_callback:
            progress_callback(agent_name, status)

    def skeptic_node(state: GladiatorState) -> GladiatorState:
        signal("Skeptic Agent", "running")
        skeptic_output = run_skeptic_agent(state["merged_state"])
        signal("Skeptic Agent", "completed")
        return {"skeptic_output": skeptic_output}

    def execution_node(state: GladiatorState) -> GladiatorState:
        signal("Execution Realist Agent", "running")
        execution_output = run_execution_realist_agent(state["merged_state"])
        signal("Execution Realist Agent", "completed")
        return {"execution_output": execution_output}

    def judge_node(state: GladiatorState) -> GladiatorState:
        signal("Judge Agent", "running")
        judge_output = run_judge_agent(
            state["merged_state"],
            state["skeptic_output"],
            state["execution_output"],
        )
        signal("Judge Agent", "completed")
        return {"judge_output": judge_output}

    graph = StateGraph(GladiatorState)
    graph.add_node("skeptic", skeptic_node)
    graph.add_node("execution", execution_node)
    graph.add_node("judge", judge_node)
    graph.add_edge(START, "skeptic")
    graph.add_edge("skeptic", "execution")
    graph.add_edge("execution", "judge")
    graph.add_edge("judge", END)

    app = graph.compile()
    result = app.invoke({"merged_state": mergedIdeaState, "errors": []})

    return {
        "skeptic": result["skeptic_output"].model_dump(),
        "execution_realist": result["execution_output"].model_dump(),
        "judge": result["judge_output"].model_dump(),
    }


# Gladiator orchestrator ends here.
