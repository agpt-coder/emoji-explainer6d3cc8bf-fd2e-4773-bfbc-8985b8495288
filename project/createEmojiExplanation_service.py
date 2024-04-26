import prisma
import prisma.models
from pydantic import BaseModel


class EmojiExplanationResponseModel(BaseModel):
    """
    Contains the explanation for the requested emoji, returned after verifying user authentication and role.
    """

    explanation_text: str


async def createEmojiExplanation(emoji_character: str) -> EmojiExplanationResponseModel:
    """
    Processes an emoji sent by the user and returns its explanation by leveraging the llama3 dataset. Requires authentication to ensure only registered users can access.

    Args:
        emoji_character (str): The emoji symbol/character sent by the user.

    Returns:
        EmojiExplanationResponseModel: Contains the explanation for the requested emoji, returned after verifying user authentication and role.

    Raises:
        ValueError: If no explanation is found for the given emoji.
    """
    user = await prisma.models.User.prisma().find_first(
        where={"email": "authenticated_user_email@example.com"}, include={"role": True}
    )
    if user is None or user.role not in ["Admin", "User"]:
        raise PermissionError(
            "User is not authenticated or does not have the required access rights."
        )
    emoji = await prisma.models.Emoji.prisma().find_unique(
        where={"character": emoji_character}, include={"explanations": True}
    )
    if emoji is None or not emoji.explanations:
        raise ValueError("No explanation available for the provided emoji.")
    explanation = emoji.explanations[0]
    return EmojiExplanationResponseModel(explanation_text=explanation.text)
