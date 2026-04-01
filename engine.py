import json
import logging
import re
import time
from typing import List, Dict, Any
from groq import Groq

from prompts import OPENING_STATEMENT_PROMPT
from personas import EXPERT_PERSONAS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SynthosEngine:
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
        provider: str = "groq",
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        if provider == "groq":
            self.client = Groq(api_key=api_key)
        elif provider == "openai":
            import openai
            openai.api_key = api_key
            self.client = openai
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        self.topic = ""
        self.user_constraints = ""
        self.personas = []
        self.debate_history = []
        self.final_consensus = {}

    def _call_llm_with_retry(self, prompt: str) -> str:
        last_exception = None
        delay = self.retry_delay

        for attempt in range(self.max_retries):
            try:
                if self.provider == "groq":
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                    )
                    return response.choices[0].message.content

                elif self.provider == "openai":
                    response = self.client.ChatCompletion.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                    )
                    return response.choices[0].message.content

                else:
                    raise ValueError(f"Unsupported provider: {self.provider}")

            except Exception as e:
                logger.warning(f"LLM call failed (attempt {attempt+1}/{self.max_retries}): {e}")
                last_exception = e
                if attempt < self.max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                else:
                    logger.error("Max retries exceeded.")
                    raise last_exception

    def _call_llm(self, prompt: str) -> str:
        try:
            return self._call_llm_with_retry(prompt)
        except Exception as e:
            logger.error(f"LLM call error: {e}")
            raise RuntimeError(f"LLM call failed: {e}")

    def set_topic(self, topic: str, constraints: str = ""):
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty.")
        self.topic = topic.strip()
        self.user_constraints = constraints.strip() if constraints else ""

    # Phase 1: hardcoded personas
    def generate_personas(self):
        self.personas = EXPERT_PERSONAS.copy()
        logger.info(f"Generated {len(self.personas)} personas (hardcoded)")
        return self.personas

    def round1_opening_statements(self):
        statements = []
        for p in self.personas:
            try:
                prompt = OPENING_STATEMENT_PROMPT.format(
                    role=p["role"],
                    personality=p["personality"],
                    goal=p["goal"],
                    topic=self.topic
                )
                text = self._call_llm(prompt)
                statements.append({"expert": p["name"], "text": text})
                self.debate_history.append({"round": 1, "speaker": p["name"], "text": text})
                logger.info(f"Round 1: {p['name']} completed.")
            except Exception as e:
                logger.error(f"Round 1 failed for {p['name']}: {e}")
                error_text = f"[Error generating opening statement: {e}]"
                statements.append({"expert": p["name"], "text": error_text})
                self.debate_history.append({"round": 1, "speaker": p["name"], "text": error_text})
        return statements

    def round2_cross_examination(self):
        cross_exam = []
        first_statement = ""
        if self.debate_history:
            for h in self.debate_history:
                if h["round"] == 1:
                    first_statement = h["text"]
                    break
        if not first_statement:
            first_statement = "No opening statement available."

        for p in self.personas:
            try:
                prompt = f"""You are {p['role']}. {p['personality']}
Topic: {self.topic}
Another expert said: "{first_statement}"

Write a brief response. Do you agree or disagree? Provide one counterpoint or supporting point.
Keep it to 100 words."""
                text = self._call_llm(prompt)
                cross_exam.append({"expert": p["name"], "text": text})
                self.debate_history.append({"round": 2, "speaker": p["name"], "text": text})
                logger.info(f"Round 2: {p['name']} completed.")
            except Exception as e:
                logger.error(f"Round 2 failed for {p['name']}: {e}")
                error_text = f"[Error generating cross-examination: {e}]"
                cross_exam.append({"expert": p["name"], "text": error_text})
                self.debate_history.append({"round": 2, "speaker": p["name"], "text": error_text})
        return cross_exam

    def round3_refinement(self):
        refinements = []
        history_summary = "\n".join([f"{h['speaker']}: {h['text'][:200]}..." for h in self.debate_history])
        for p in self.personas:
            try:
                prompt = f"""You are {p['role']}. {p['personality']}
Topic: {self.topic}
Debate so far:
{history_summary}

Now, give your refined position. What points do you concede? What do you still stand by? Propose a compromise if possible.
Keep it to 150 words."""
                text = self._call_llm(prompt)
                refinements.append({"expert": p["name"], "text": text})
                self.debate_history.append({"round": 3, "speaker": p["name"], "text": text})
                logger.info(f"Round 3: {p['name']} completed.")
            except Exception as e:
                logger.error(f"Round 3 failed for {p['name']}: {e}")
                error_text = f"[Error generating refinement: {e}]"
                refinements.append({"expert": p["name"], "text": error_text})
                self.debate_history.append({"round": 3, "speaker": p["name"], "text": error_text})
        return refinements

    def _extract_json(self, text: str) -> str:
        """Extract the first valid JSON object from text."""
        # Remove markdown code fences
        text = re.sub(r'```json\s*|\s*```', '', text, flags=re.IGNORECASE)
        # Find the first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end+1]
            try:
                json.loads(candidate)
                return candidate
            except:
                pass
        # Fallback: find JSON-like objects
        matches = re.findall(r'\{[^{}]*\}', text, re.DOTALL)
        for match in matches:
            try:
                json.loads(match)
                return match
            except:
                continue
        # If all fails, return original (will cause JSONDecodeError)
        return text

    def mediate(self):
        transcript = "\n".join([f"Round {h['round']} - {h['speaker']}: {h['text']}" for h in self.debate_history])
        prompt = f"""You are a neutral mediator. Your task is to synthesize the debate below into a consensus solution.

Topic: {self.topic}
User constraints: {self.user_constraints if self.user_constraints else "None"}

Debate transcript:
{transcript}

Output a valid JSON object with exactly the following structure:
{{
    "verdict": "clear statement of the agreed solution",
    "implementation_plan": ["step 1", "step 2", "step 3"],
    "risks_mitigations": ["risk 1 -> mitigation", "risk 2 -> mitigation"],
    "dissent_note": "if any expert disagreed, note their view; otherwise 'None'"
}}
Do not include any other text, explanation, or markdown. Output only the JSON object."""

        try:
            response = self._call_llm(prompt)
            json_str = self._extract_json(response)
            self.final_consensus = json.loads(json_str)
            logger.info("Mediator output parsed successfully.")
        except json.JSONDecodeError as e:
            logger.error(f"Mediator JSON parsing failed: {e}. Raw response: {response}")
            self.final_consensus = {
                "error": "Failed to parse mediator output as JSON",
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Mediator call failed: {e}")
            self.final_consensus = {"error": f"Mediator failed: {e}"}
        return self.final_consensus

    def format_output(self, format_type="markdown"):
        if format_type == "json":
            return {
                "topic": self.topic,
                "user_constraints": self.user_constraints,
                "experts": self.personas,
                "debate_history": self.debate_history,
                "consensus": self.final_consensus
            }
        elif format_type == "markdown":
            md = f"# Synthos Debate: {self.topic}\n\n"
            if self.user_constraints:
                md += f"**Constraints:** {self.user_constraints}\n\n"
            md += "## Experts\n"
            for p in self.personas:
                md += f"- **{p['name']}** ({p['role']}): {p['personality']}\n"
            md += "\n## Debate Transcript\n"
            for h in self.debate_history:
                md += f"### Round {h['round']} - {h['speaker']}\n{h['text']}\n\n"
            md += "## Consensus\n"
            if "error" in self.final_consensus:
                md += f"**Error:** {self.final_consensus['error']}\n\n"
                if "raw_response" in self.final_consensus:
                    md += f"**Raw mediator output:**\n```\n{self.final_consensus['raw_response']}\n```\n"
            else:
                md += f"**Verdict:** {self.final_consensus.get('verdict', '')}\n\n"
                md += "**Implementation Plan:**\n"
                for step in self.final_consensus.get('implementation_plan', []):
                    md += f"- {step}\n"
                md += "\n**Risks & Mitigations:**\n"
                for risk in self.final_consensus.get('risks_mitigations', []):
                    md += f"- {risk}\n"
                md += f"\n**Dissent:** {self.final_consensus.get('dissent_note', 'None')}\n"
            return md
        else:
            return self.final_consensus

    def run(self, topic: str, constraints: str = ""):
        try:
            self.set_topic(topic, constraints)
        except ValueError as e:
            logger.error(f"Invalid topic: {e}")
            return f"Error: {e}"

        self.generate_personas()
        self.round1_opening_statements()
        self.round2_cross_examination()
        self.round3_refinement()
        self.mediate()
        return self.format_output("markdown")