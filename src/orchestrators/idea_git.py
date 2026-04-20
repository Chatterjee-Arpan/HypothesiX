from typing import Callable

from langgraph.graph import END, START, StateGraph

from src.agents.idea_git_agents import (
    run_cartographer_agent,
    run_conflict_gap_agent,
    run_mapper_agent,
)
from src.schemas import CollaboratorInput, IdeaGitState


# Idea Git orchestrator starts here.
def runIdeaGitOrchestrator(
    inputs: list[CollaboratorInput],
    progress_callback: Callable[[str, str], None] | None = None,
) -> dict:
    def signal(agent_name: str, status: str) -> None:
        if progress_callback:
            progress_callback(agent_name, status)

    def mapper_node(state: IdeaGitState) -> IdeaGitState:
        signal("Mapper Agent", "running")
        mapper_output = run_mapper_agent(state["collaborators"])
        signal("Mapper Agent", "completed")
        return {"mapper_output": mapper_output}

    def analyzer_node(state: IdeaGitState) -> IdeaGitState:
        signal("Conflict & Gap Analyzer", "running")
        analyzer_output = run_conflict_gap_agent(
            state["collaborators"], state["mapper_output"]
        )
        signal("Conflict & Gap Analyzer", "completed")
        return {"analyzer_output": analyzer_output}

    def cartographer_node(state: IdeaGitState) -> IdeaGitState:
        signal("Cartographer Agent", "running")
        cartographer_output = run_cartographer_agent(
            state["mapper_output"], state["analyzer_output"]
        )
        signal("Cartographer Agent", "completed")
        return {"cartographer_output": cartographer_output}

    graph = StateGraph(IdeaGitState)
    graph.add_node("mapper", mapper_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("cartographer", cartographer_node)
    graph.add_edge(START, "mapper")
    graph.add_edge("mapper", "analyzer")
    graph.add_edge("analyzer", "cartographer")
    graph.add_edge("cartographer", END)

    app = graph.compile()
    result = app.invoke({"collaborators": inputs, "errors": []})

    return {
        "inputs": [item.model_dump() for item in inputs],
        "mapper": result["mapper_output"].model_dump(),
        "analyzer": result["analyzer_output"].model_dump(),
        "cartographer": result["cartographer_output"].model_dump(),
    }


# Idea Git orchestrator ends here.
