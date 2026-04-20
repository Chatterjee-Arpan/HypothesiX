from src.schemas import CollaboratorInput

DEMO_COLLABORATORS = [
    CollaboratorInput(
        name="Mira",
        tag="user problem",
        contribution="Researchers lose useful ideas across notebooks, chats, and whiteboards. We need one place to merge hypotheses and turn confusion into a next step.",
    ),
    CollaboratorInput(
        name="Theo",
        tag="feature",
        contribution="The app should combine several teammate viewpoints into one merged project brief, not just summarize each person separately.",
    ),
    CollaboratorInput(
        name="Rae",
        tag="concern",
        contribution="If the synthesis feels too generic, the team will not trust it. The output must show disagreements, uncertainty, and missing evidence clearly.",
    ),
    CollaboratorInput(
        name="Jon",
        tag="technical note",
        contribution="We can support a flowchart view so teams see goal, assumptions, blockers, and questions at a glance before deciding what to test next.",
    ),
    CollaboratorInput(
        name="Asha",
        tag="assumption",
        contribution="Small product teams and research groups both need this, but each group may define success differently. We should avoid locking into one workflow too early.",
    ),
    CollaboratorInput(
        name="Leo",
        tag="blocker",
        contribution="The biggest risk is teams jumping into critique before agreeing on the merged idea. The stress-test stage should be optional and only unlocked after review.",
    ),
]
