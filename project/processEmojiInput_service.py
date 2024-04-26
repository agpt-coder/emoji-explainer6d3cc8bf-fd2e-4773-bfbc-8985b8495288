from typing import Optional

import emoji
import prisma
import prisma.models
from pydantic import BaseModel


class EmojiProcessResponse(BaseModel):
    """
    This model describes the response that is sent back to the client after processing the emoji. It includes the original emoji and its explanation, or an error message if the validation fails.
    """

    emoji_character: str
    explanation: str
    error: Optional[str] = None


async def processEmojiInput(emoji_character: str) -> EmojiProcessResponse:
    """
    This function validates an emoji character and fetches its explanation using llama3 service accessed via Groq.

    Args:
        emoji_character (str): A valid emoji character string that needs to be explained.

    Returns:
        EmojiProcessResponse: This model describes the response sent back to the client after processing the emoji.
        It includes the original emoji and its explanation, or an error message if the validation fails.
    """
    if not validate_emoji(emoji_character):
        return EmojiProcessResponse(
            emoji_character=emoji_character,
            explanation="",
            error="Invalid emoji character provided",
        )
    emoji_record = await prisma.models.Emoji.prisma().find_first(
        where={"character": emoji_character}, include={"explanations": True}
    )
    if emoji_record and emoji_record.explanations:
        explanation = emoji_record.explanations[0].text
    else:
        explanation = await fetch_explanation_from_llama3(emoji_character)
        if not emoji_record:
            emoji_record = await prisma.models.Emoji.prisma().create(
                data={"character": emoji_character}
            )
        await prisma.models.Explanation.prisma().create(
            data={"text": explanation, "emojiId": emoji_record.id}
        )
    return EmojiProcessResponse(
        emoji_character=emoji_character, explanation=explanation
    )


def validate_emoji(character: str) -> bool:
    """
    Validates if the given string is a proper UTF-8 encoded emoji.

    Args:
        character (str): The string to validate as an emoji.

    Returns:
        bool: True if the character is a valid emoji, False otherwise.
    """
    emoji_pattern = emoji.get_emoji_regexp()
    return bool(emoji_pattern.fullmatch(character))


async def fetch_explanation_from_llama3(character: str) -> str:
    """
    Simulates fetching an emoji explanation from llama3 using the Groq service.

    Args:
        character (str): Emoji character for which explanation is fetched.

    Returns:
        str: The fetched explanation for the emoji.
    """
    return "Simulated explanation fetched from llama3 for the emoji: " + character
