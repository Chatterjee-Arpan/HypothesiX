# HypothesiX

HypothesiX is a polished Streamlit app for merging multiple collaborator viewpoints into one clear project state, surfacing conflicts and gaps, visualizing the idea in Mermaid, and optionally stress-testing the merged idea inside a second-stage Gladiator Arena.

## What the app does

1. Collects 6 to 8 collaborator inputs on a workshop-style board.
2. Runs the Idea Git orchestrator to merge perspectives, expose disagreement, and build a flowchart-ready idea map.
3. Requires the user to review the merged idea state before unlocking the Gladiator Arena.
4. Runs the Gladiator orchestrator only after explicit opt-in.
5. Exposes copy-friendly exports for the merged summary, Mermaid graph text, and Gladiator verdict.

## Architecture

The app uses exactly two orchestrators implemented with LangGraph:

### 1. Idea Git orchestrator

Function: `runIdeaGitOrchestrator(inputs)`

Internal agents:
- Mapper Agent (`gpt-4.1`)
- Conflict & Gap Analyzer Agent (`gpt-4.1`)
- Cartographer Agent (`gpt-4.1-mini`)

Outputs:
- merged idea state
- conflict map
- gap map
- open questions
- Mermaid flowchart text

### 2. Gladiator orchestrator

Function: `runGladiatorOrchestrator(mergedIdeaState)`

Internal agents:
- Skeptic Agent (`gpt-4.1`)
- Execution Realist Agent (`gpt-4.1`)
- Judge Agent (`gpt-4.1`)

Outputs:
- critical risks
- dangerous assumptions
- smallest validation step
- final verdict

## Model routing strategy

Centralized model routing lives in `src/config.py`.

- Higher-reasoning synthesis agents use `gpt-4.1`
- Lower-latency graphing agent uses `gpt-4.1-mini`

## Project structure

```text
app.py
requirements.txt
.env
.env.example
src/
  config.py
  models.py
  prompts.py
  schemas.py
  demo_data.py
  agents/
    idea_git_agents.py
    gladiator_agents.py
  orchestrators/
    idea_git.py
    gladiator.py
  ui/
    styles.py
    components.py
  utils/
    mermaid.py
    parsing.py
```

## Environment setup

Create or edit `.env` and add your OpenAI key:

```env
OPENAI_GPT_KEY=your_real_key_here
```

The app loads environment variables with `load_dotenv()` and reads the key using `os.getenv("OPENAI_GPT_KEY")`.

## Run locally

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run app.py
```

## Mermaid rendering

Mermaid rendering helpers live in `src/utils/mermaid.py`.

- `ensure_mermaid_flowchart()` normalizes model output into safe Mermaid flowchart text.
- `mermaid_html()` renders the chart inside a Streamlit HTML component.

If Mermaid text is malformed, the app still exposes a plain-text export view instead of breaking the UI.

## Demo data

Seed collaborator inputs live in `src/demo_data.py`.

Use the `Load Demo Data` button to populate the board with a ready-to-run scenario.
