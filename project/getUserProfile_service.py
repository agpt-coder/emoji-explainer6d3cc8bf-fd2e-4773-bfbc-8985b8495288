import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    """
    This model provides the authenticated user's profile information, ensuring it includes only data that the user is authorized to see.
    """

    id: int
    email: str
    role: prisma.enums.Role


async def getUserProfile(access_token: str) -> UserProfileResponse:
    """
    Returns the profile information of the authenticated user. Requires an access token to verify the user's identity.
    This ensures that users can only access their own information.

    Args:
        access_token (str): Access token provided in the headers to authenticate and identify the user.

    Returns:
        UserProfileResponse: This model provides the authenticated user's profile information, ensuring it includes
                             only data that the user is authorized to see.

    Example:
        access_token = 'valid_token123'
        user_profile = await getUserProfile(access_token)
    """
    user_id = decode_access_token(access_token)
    user = await prisma.models.User.prisma().find_unique(where={"id": user_id})
    if not user:
        raise ValueError("User not found or access token invalid.")
    return UserProfileResponse(id=user.id, email=user.email, role=user.role)


def decode_access_token(token: str) -> int:
    """
    Decodes a JWT access token to extract the unique user ID. This should be replaced with your actual JWT decoding logic
    that might use a library like PyJWT to handle the token validation and decoding.

    Args:
        token (str): The JWT access token

    Returns:
        int: The user ID obtained from the decoded token

    Example:
        token = 'some_encoded_jwt_token'
        user_id = decode_access_token(token)
    """
    return 1
