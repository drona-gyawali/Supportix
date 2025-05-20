import logging

import openai

logger = logging.getLogger(__name__)

ALLOWED_TAGS = {
    "billing",
    "login",
    "technical",
    "network",
    "auth",
    "account",
    "email",
    "payment",
    "error",
    "bug",
    "support",
    "debug",
    "slow",
    "feature",
    "urgent",
}
MAX_TAGS = 3


def generate_tags(issue_title: str, issue_desc: str | None) -> list[str]:
    """
    Generate up to MAX_TAGS tags for a ticket using LLM.
    If any of the allowed tags apply, use only from them.
    Otherwise, suggest your own meaningful one-word tags.
    """
    ticket_text = f"{issue_title.strip()}\n{issue_desc or ''}".strip()

    prompt = f"""
You are an intelligent ticket tagging assistant.

Based on the following ticket content, suggest up to {MAX_TAGS} lowercase, comma-separated, one-word tags.

- If any of the following tags apply, choose ONLY from them: {', '.join(sorted(ALLOWED_TAGS))}
- If none apply, you MAY generate your own relevant one-word tags.

Ticket:
\"\"\"
{ticket_text}
\"\"\"

Tags:
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = response.choices[0].message.content.strip()
        tags = [tag.strip().lower() for tag in content.split(",") if tag.strip()]
        return tags[:MAX_TAGS]
    except Exception as e:
        logger.exception(f"LLM tag generation failed: {str(e)}")
        return []
