from langchain_core.messages import HumanMessage, SystemMessage

from src.models import get_chat_model
from src.prompts import (
    SYSTEM_STYLE,
    execution_realist_prompt,
    judge_prompt,
    skeptic_prompt,
)
from src.schemas import ExecutionRealistOutput, JudgeOutput, SkepticOutput


def run_skeptic_agent(merged_state: dict) -> SkepticOutput:
    model = get_chat_model("skeptic").with_structured_output(SkepticOutput)
    return model.invoke(
        [
            SystemMessage(content=SYSTEM_STYLE),
            HumanMessage(content=skeptic_prompt(merged_state)),
        ]
    )


def run_execution_realist_agent(merged_state: dict) -> ExecutionRealistOutput:
    model = get_chat_model("execution_realist").with_structured_output(
        ExecutionRealistOutput
    )
    return model.invoke(
        [
            SystemMessage(content=SYSTEM_STYLE),
            HumanMessage(content=execution_realist_prompt(merged_state)),
        ]
    )


def run_judge_agent(
    merged_state: dict,
    skeptic_output: SkepticOutput,
    execution_output: ExecutionRealistOutput,
) -> JudgeOutput:
    model = get_chat_model("judge").with_structured_output(JudgeOutput)
    return model.invoke(
        [
            SystemMessage(content=SYSTEM_STYLE),
            HumanMessage(
                content=judge_prompt(
                    merged_state,
                    skeptic_output.model_dump(),
                    execution_output.model_dump(),
                )
            ),
        ]
    )
