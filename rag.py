from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()                 # loads ANTHROPIC_API_KEY from .env into the environment
client = Anthropic()          # reads that key automatically

def ask_claude(prompt: str, model: str = "claude-sonnet-4-6") -> str:
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

if __name__ == "__main__":
    print(ask_claude("In one sentence, what is a 10-K filing?"))