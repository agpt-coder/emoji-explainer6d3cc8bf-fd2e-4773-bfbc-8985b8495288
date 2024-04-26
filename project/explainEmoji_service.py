import httpx
import prisma
import prisma.models
from pydantic import BaseModel


class EmojiExplanationResponse(BaseModel):
    """
    A response model that pairs an emoji with its corresponding explanation.
    """

    emoji_character: str
    explanation: str


async def explainEmoji(emoji: str) -> EmojiExplanationResponse:
    """
    Retrieves or creates emoji details in the database, queries for an explanation using an external service, and returns the explanation for the given emoji character.

    Args:
        emoji (str): The emoji character submitted by the user.

    Returns:
        EmojiExplanationResponse: A response model that pairs an emoji with its corresponding explanation.

    Example:
        explainEmoji('😊')
        > EmojiExplanationResponse(emoji_character='😊', explanation='A smiling face to express happiness.')
    """
    emoji_record = await prisma.models.Emoji.prisma().find_unique(
        where={"character": emoji}, include={"explanations": True}
    )
    if not emoji_record:
        emoji_record = await prisma.models.Emoji.prisma().create(
            data={"character": emoji}
        )
    if emoji_record.explanations:
        recent_explanation = max(
            emoji_record.explanations, key=lambda exp: exp.createdAt
        )
        explanation_text = recent_explanation.text
    else:
        explanation_text = await fetch_explanation_from_external_service(emoji)
        await prisma.models.Explanation.prisma().create(
            data={"text": explanation_text, "emojiId": emoji_record.id}
        )
    return EmojiExplanationResponse(emoji_character=emoji, explanation=explanation_text)


async def fetch_explanation_from_external_service(emoji: str) -> str:
    """
    Queries an external service to fetch an emoji explanation.

    Args:
        emoji (str): The emoji character for which an explanation is needed.

    Returns:
        str: Explanation returned by the external service.

    Example:
        fetch_explanation_from_external_service('😊')
        > 'A smiling face to express happiness.'
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.llama3.groq.it/explain", json={"emoji": emoji}
        )
        if response.status_code == 200:
            return response.json()["explanation"]
        return "Explanation not found."
