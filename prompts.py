# prompts.py

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