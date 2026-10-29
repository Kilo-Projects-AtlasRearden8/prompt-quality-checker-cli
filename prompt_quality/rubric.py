"""Local rubric used to score prompt drafts.

Four categories are scored from 1 (poor) to 5 (excellent): clarity,
variables, bias, and safety. The rubric text is shipped with the tool so the
reviewer always has a fixed, local standard to apply.
"""

RUBRIC = {
    "clarity": {
        "title": "Clarity",
        "criteria": (
            "Is the prompt's intent easy to understand? A clear prompt states "
            "the task, gives enough context, names the audience, and describes "
            "the desired output format. Vague instructions like 'write "
            "something good' score low."
        ),
    },
    "variables": {
        "title": "Variables",
        "criteria": (
            "Does the prompt use placeholder variables (for example {name} or "
            "{topic}) consistently, and are they defined so the reader knows "
            "what to fill in? Undefined or inconsistently named variables "
            "score low."
        ),
    },
    "bias": {
        "title": "Bias",
        "criteria": (
            "Does the prompt avoid harmful assumptions and stereotypes about "
            "gender, race, age, disability, religion, or other protected "
            "groups? Language that assumes a default identity or role scores "
            "low."
        ),
    },
    "safety": {
        "title": "Safety",
        "criteria": (
            "Does the prompt avoid asking for disallowed content such as "
            "personal data, medical diagnosis, legal advice, self-harm, or "
            "instructions for illegal acts? General educational framing is "
            "acceptable; requests for medical or legal advice are not."
        ),
    },
}

CATEGORY_ORDER = ["clarity", "variables", "bias", "safety"]


def category_spec(slug):
    """Return the rubric spec for a category slug."""
    return RUBRIC[slug]
