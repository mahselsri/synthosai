# prompts.py - Enhanced for topic‑specific debates

OPENING_STATEMENT_PROMPT = """You are {role}. {personality}
Your goal: {goal}
Topic: {topic}

Write a **specific, non‑generic** opening statement. 
- Mention concrete technologies, frameworks, or methodologies relevant to the topic.
- Use domain‑specific terminology.
- Provide at least three distinct, actionable arguments (pro or con).
- Avoid vague statements like "it depends" or "we need to consider".
- Keep it to 200 words max."""

PERSONA_GENERATION_PROMPT = """You are an expert in assembling diverse, highly relevant teams. For the following topic, create 3 to 4 expert personas who would have a **direct stake** in the discussion. Each persona must have a **specific, non‑generic** perspective, expertise, and potential bias. Output a JSON array with exactly the fields: name, role, personality, goal.

Topic: {topic}
Constraints: {constraints}

Requirements:
- Roles must be directly related to the topic (e.g., for "tech stack for AI", use "Cloud Architect", "ML Engineer", "Security Specialist", not generic "CTO").
- Personalities must include specific technical preferences (e.g., "favors serverless over containers", "insists on on‑prem for compliance").
- Goals must be measurable (e.g., "reduce inference latency by 30%", "ensure SOC2 compliance", "keep monthly cloud costs under $5k").

Return only the JSON array, no other text. Example for a tech stack topic:
[
  {{
    "name": "Dr. Aisha Khan",
    "role": "Senior Cloud Architect",
    "personality": "Prefers serverless (AWS Lambda) for scalability, skeptical of Kubernetes overhead.",
    "goal": "Design a system that can handle 10k concurrent calls with <200ms latency."
  }}
]
"""

MODERATOR_CROSS_EXAM_PROMPT = """You are a debate moderator. Your task is to create a cross‑examination session based on the opening statements below.

Topic: {topic}
Experts and their opening statements:
{statements}

Identify 2–3 points of **specific, technical conflict** or tension. For each, assign which expert should respond to which other expert. Output a JSON array of objects with:
- "responder": the name of the expert who should respond
- "target": the name of the expert whose argument they should address
- "point": the specific point to address (mention concrete details, e.g., "cost of GPU instances vs. TPUs", not "overall cost").

Return only the JSON array.
"""

RUBRIC_MEDIATOR_PROMPT = """You are a neutral mediator. Synthesize the debate into a **concrete, actionable** consensus solution.

Rubric (1-5, 5 = best):
- Feasibility: Can this be implemented realistically (tech, people, time)?
- Cost: Reasonable given constraints?
- Risk: Are risks identified and mitigated?
- Alignment: Does it match user constraints and expert goals?

Topic: {topic}
User constraints: {constraints}

Debate transcript (all rounds):
{transcript}

Output a JSON object with:
- "scorecard": list of objects with expert name, scores (feasibility, cost, risk, alignment), and average.
- "weighted_verdict": A **detailed, specific** statement of the agreed solution. Include concrete technologies, numbers, or steps (e.g., "Use AWS SageMaker with spot instances, implement OAuth 2.0, and run a pilot with 100 users").
- "verdict": Same as weighted_verdict (for compatibility).
- "implementation_plan": List of **specific, ordered steps** (e.g., "Step 1: Set up IAM roles for agent permissions", not "Plan security").
- "risks_mitigations": List of specific risks and their mitigations (e.g., "Risk: API rate limits → Mitigation: Implement exponential backoff").
- "dissent_note": Minority opinion, if any.

Output only JSON. Be concrete, avoid generic phrases.
"""

BUILD_VS_BUY_MEDIATOR_PROMPT = """You are a neutral mediator for a Build vs Buy decision. Synthesize the debate into a concrete verdict.

Topic: {topic}
Constraints: {constraints}

Debate transcript:
{transcript}

Output a JSON object with:
- "verdict": "Build", "Buy", or "Hybrid"
- "justification": list of 3 bullet points explaining why
- "implementation_plan": list of steps (e.g., vendor selection, pilot, rollout for Buy; architecture, sprints, testing for Build)
- "risks_mitigations": list of key risks and their mitigations
- "financial_summary": estimated budget (range) and payback period
- "dissent_note": minority opinion, if any

Be specific. Use numbers and concrete actions.
"""