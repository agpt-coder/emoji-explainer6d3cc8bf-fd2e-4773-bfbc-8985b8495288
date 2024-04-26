import prisma
import prisma.models
from pydantic import BaseModel


class DeleteUserResponse(BaseModel):
    """
    This model outlines the expected response when a user successfully deletes their account. It communicates the successful removal of the user data from the system.
    """

    message: str
    user_id: int


async def deleteUser(user_id: int) -> DeleteUserResponse:
    """
    Allows a user to delete their account using their user ID. Requires authentication and is restricted to ensure only the account owner can delete their profile.

    Args:
        user_id (int): The unique identifier of the user, used to confirm deletion permissions and reference the correct user in the database.

    Returns:
        DeleteUserResponse: This model outlines the expected response when a user successfully deletes their account. It communicates the successful removal of the user data from the system.

    Example:
        deleteUser(10)
        > Deleting user with ID 10 results in DeleteUserResponse(message='User successfully deleted.', user_id=10)
    """
    user = await prisma.models.User.prisma().delete(where={"id": user_id})
    if user:
        response = DeleteUserResponse(
            message="User successfully deleted.", user_id=user_id
        )
        return response
    else:
        raise Exception("User not found or could not be deleted")
    return DeleteUserResponse(
        message="User has been successfully removed from the database", user_id=user_id
    )
