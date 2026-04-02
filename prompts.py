OPENING_STATEMENT_PROMPT = """You are {role}. {personality}
Your goal: {goal}
Topic: {topic}

Write your opening statement. Include your stance (for/against/neutral), your top 3 arguments, and any concerns you have.
Keep it concise (max 200 words)."""

PERSONA_GENERATION_PROMPT = """You are an expert in assembling diverse teams. For the following topic, create 3 to 4 expert personas who would have a stake in the discussion. Each persona should have a distinct perspective, expertise, and potential bias. Output a JSON array with exactly the fields: name, role, personality, goal.

Topic: {topic}
Constraints: {constraints}

Return only the JSON array, no other text. Example:
[
  {{
    "name": "Dr. Jane Smith",
    "role": "Chief Data Scientist",
    "personality": "Data-driven, skeptical of unproven claims, optimistic about AI's potential",
    "goal": "Ensure decisions are backed by empirical evidence and scalable architecture"
  }}
]
"""

MODERATOR_CROSS_EXAM_PROMPT = """You are a debate moderator. Your task is to create a cross‑examination session based on the opening statements below.

Topic: {topic}
Experts and their opening statements:
{statements}

Identify 2–3 points of conflict or tension. For each, assign which expert should respond to which other expert. Output a JSON array of objects with:
- "responder": the name of the expert who should respond
- "target": the name of the expert whose argument they should address
- "point": the specific point to address

Return only the JSON array. Example:
[
  {{"responder": "Sarah Chen", "target": "Marcus Webb", "point": "security concerns about rapid deployment"}},
  ...
]
"""

RUBRIC_MEDIATOR_PROMPT = """You are a neutral mediator with a structured rubric. Your task is to evaluate the debate and produce a consensus solution using the following rubric:

Rubric (each criterion 1-5, 5 = best):
- Feasibility: Can this be implemented realistically?
- Cost: Is the cost reasonable given constraints?
- Risk: Are risks identified and mitigated?
- Alignment: Does it align with user constraints and expert goals?

For each expert's final stance (from Round 3), assign scores. Then propose a weighted verdict.

Topic: {topic}
User constraints: {constraints}

Debate transcript (all rounds):
{transcript}

Output a valid JSON object with the following structure:
{{
    "scorecard": [
        {{"expert": "name", "scores": {{"feasibility": int, "cost": int, "risk": int, "alignment": int}}, "average": float}}
    ],
    "weighted_verdict": "clear statement based on highest average scores",
    "verdict": "same as weighted_verdict (for backward compatibility)",
    "implementation_plan": ["step 1", "step 2", ...],
    "risks_mitigations": ["risk -> mitigation", ...],
    "dissent_note": "minority opinion if any, else 'None'"
}}
Do not include extra text or markdown. Only output JSON.
"""