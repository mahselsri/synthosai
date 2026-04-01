import os
import sys
from engine import SynthosEngine
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()
def main():
    # Get API key from environment
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not set.")
        sys.exit(1)

    # Optional: allow model override via env
    model = os.getenv("SYNTHOS_MODEL", "llama-3.3-70b-versatile")

    # Initialize engine with Groq
    engine = SynthosEngine(api_key=api_key, model=model, provider="groq")

    # Get input
    topic = input("Enter topic: ").strip()
    if not topic:
        print("Error: Topic cannot be empty.")
        sys.exit(1)

    constraints = input("Enter constraints (optional): ").strip()

    # Run and display output
    result = engine.run(topic, constraints)
    print(result)

if __name__ == "__main__":
    main()