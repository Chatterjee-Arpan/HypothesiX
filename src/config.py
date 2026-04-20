import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_GPT_KEY = os.getenv("OPENAI_GPT_KEY")

MODEL_ROUTING = {
    "mapper": "gpt-4.1",
    "conflict_gap": "gpt-4.1",
    "cartographer": "gpt-4.1-mini",
    "skeptic": "gpt-4.1",
    "execution_realist": "gpt-4.1",
    "judge": "gpt-4.1",
}

DEFAULT_TEMPERATURE = 0.2
APP_TITLE = "HypothesiX"
MAX_COLLABORATORS = 8
DEFAULT_COLLABORATORS = 6
