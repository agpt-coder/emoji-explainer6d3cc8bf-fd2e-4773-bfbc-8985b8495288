from typing import List

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class AdminUserListRequest(BaseModel):
    """
    Request model for fetching all registered users, which is restricted to administrators. It assumes the request context includes necessary authentication and role verification.
    """

    pass


class UserDetail(BaseModel):
    """
    Detailed information about a user, including their role and email.
    """

    id: int
    email: str
    role: prisma.enums.Role


class AdminUserListResponse(BaseModel):
    """
    Provides a list of all registered users with their relevant details. This endpoint is intended for use in administrative user management and monitoring.
    """

    users: List[UserDetail]


async def listUsers(request: AdminUserListRequest) -> AdminUserListResponse:
    """
    Provides a list of all registered users. Restricted to administrators only. Useful for user management and monitoring purposes.

    Args:
        request (AdminUserListRequest): Request model for fetching all registered users, which is restricted to administrators. It assumes the request context includes necessary authentication and role verification.

    Returns:
        AdminUserListResponse: Provides a list of all registered users with their relevant details. This endpoint is intended for use in administrative user management and monitoring.
    """
    users = await prisma.models.User.prisma().find_many(include={"role": True})
    user_details = [
        UserDetail(id=user.id, email=user.email, role=user.role) for user in users
    ]
    return AdminUserListResponse(users=user_details)
