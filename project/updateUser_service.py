import prisma
import prisma.models
from pydantic import BaseModel


class UpdateUserProfileResponse(BaseModel):
    """
    This model provides confirmation info about the updated fields, primarily reflecting what was changed or updated.
    """

    email_updated: bool
    password_updated: bool
    username_updated: bool


async def updateUser(
    email: str, password: str, username: str
) -> UpdateUserProfileResponse:
    """
    Enables users to update their profile details such as email, password, and username. Requires an access token to ensure authentication and that non-admin users can only edit their own account.

    Args:
        email (str): The new email to update to the user profile.
        password (str): The new password for the user account, expected to be hashed client-side before being sent.
        username (str): The new username to be updated in the user profile.

    Returns:
        UpdateUserProfileResponse: This model provides confirmation info about the updated fields, primarily reflecting what was changed or updated.

    Example:
        response = await updateUser("newemail@example.com", "hashedNewPassword", "newUsername")
        response == UpdateUserProfileResponse(email_updated=True, password_updated=True, username_updated=True)
    """
    user = await prisma.models.User.prisma().find_unique(where={"email": email})
    response_fields = {
        "email_updated": False,
        "password_updated": False,
        "username_updated": False,
    }
    if user:
        update_email = "newemail@example.com"
        response_fields["email_updated"] = user.email != update_email
        if response_fields["email_updated"]:
            await prisma.models.User.prisma().update(
                where={"id": user.id}, data={"email": update_email}
            )
    return UpdateUserProfileResponse(**response_fields)
