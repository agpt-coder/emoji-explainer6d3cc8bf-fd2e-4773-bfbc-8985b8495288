from datetime import datetime, timedelta

import bcrypt
import jwt
import prisma
import prisma.models
from pydantic import BaseModel


class UserRegistrationResponse(BaseModel):
    """
    Response provided after successful user registration, including the newly created user object and an authentication token.
    """

    user: prisma.models.User
    authToken: str


class User(BaseModel):
    id: int
    email: str
    role: str


async def registerUser(email: str, password: str) -> UserRegistrationResponse:
    """
    This endpoint allows a new user to register. It accepts email and password, and upon successful registration, it returns a user object and an authentication token. The endpoint does not require authentication.

    Args:
        email (str): The email address for the new user account, used for verification and communication.
        password (str): The password for the new user account. This will be hashed and stored securely in the database.

    Returns:
        UserRegistrationResponse: Response provided after successful user registration, including the newly created user object and an authentication token.

    Example:
        response = registerUser('john.doe@example.com', 's3cureP@ssword')
        response.authToken  # DO NOT PRINT OR LOG AUTH TOKENS IN PRODUCTION
    """
    existing_user = await prisma.models.User.prisma().find_unique(
        where={"email": email}
    )
    if existing_user:
        raise Exception("prisma.models.User already exists with this email")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    new_user = await prisma.models.User.prisma().create(
        data={
            "email": email,
            "role": "prisma.models.User",
            "hashed_password": hashed_password.decode("utf-8"),
        }
    )
    expiration_time = datetime.utcnow() + timedelta(hours=1)
    payload = {"user_id": new_user.id, "exp": expiration_time}
    secret_key = "YOUR_SECRET_KEY"
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    user_response = prisma.models.User(
        id=new_user.id, email=new_user.email, role=new_user.role
    )
    response = UserRegistrationResponse(user=user_response, authToken=token)
    return response
