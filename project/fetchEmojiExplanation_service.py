import openai
import prisma
import prisma.models
from pydantic import BaseModel


class EmojiExplanationResponse(BaseModel):
    """
    A response model that pairs an emoji with its corresponding explanation.
    """

    emoji_character: str
    explanation: str


async def fetchEmojiExplanation(emoji_character: str) -> EmojiExplanationResponse:
    """
    Fetches an explanation for a given emoji character using the LLaMA model from OpenAI through GPT-3.

    Args:
        emoji_character (str): The emoji character for which an explanation is requested.

    Returns:
        EmojiExplanationResponse: A model containing the emoji character and its explanation.

    Example:
        emoji_character = '🚀'
        response = fetchEmojiExplanation(emoji_character)
        print(response)
        > EmojiExplanationResponse(emoji_character='🚀', explanation='A rocket, representing space travel or speed.')
    """
    emoji_record = await prisma.models.Emoji.prisma().find_unique(
        where={"character": emoji_character}, include={"explanations": True}
    )
    if emoji_record and emoji_record.explanations:
        explanation = emoji_record.explanations[-1].text
    else:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Explain the emoji {emoji_character}",
            max_tokens=150,
        )  # TODO(autogpt): "Completion" is not a known attribute of module "openai". reportAttributeAccessIssue
        explanation = response["choices"][0]["text"].strip()
        if not emoji_record:
            emoji_record = await prisma.models.Emoji.prisma().create(
                {"character": emoji_character}
            )
        await prisma.models.Explanation.prisma().create(
            {"text": explanation, "emojiId": emoji_record.id}
        )
    return EmojiExplanationResponse(
        emoji_character=emoji_character, explanation=explanation
    )
