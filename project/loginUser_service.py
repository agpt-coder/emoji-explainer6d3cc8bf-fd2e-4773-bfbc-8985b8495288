from datetime import datetime, timedelta

import bcrypt
import jwt
import prisma
import prisma.models
from pydantic import BaseModel


class LoginResponse(BaseModel):
    """
    Response model for a successful login attempt. This contains the access token required for authenticated access.
    """

    access_token: str
    token_type: str


async def loginUser(email: str, password: str) -> LoginResponse:
    """
    Allows a user to log in by providing an email and password. If credentials are valid, it returns an access token,
    which is required for making authenticated requests to protected routes.

    Args:
        email (str): Registered email of the user trying to log in.
        password (str): Password for the account associated with the email. Should be handled securely.

    Returns:
        LoginResponse: Response model for a successful login attempt. This contains the access token required for authenticated access.

    Raises:
        ValueError: If the user is not found or password does not match.
    """
    user = await prisma.models.User.prisma().find_unique(where={"email": email})
    if user is None or not hasattr(user, "hashed_password"):
        raise ValueError("User not found or no password set for this user.")
    password_bytes = password.encode("utf-8")
    stored_password_hash = user.hashed_password.encode(
        "utf-8"
    )  # TODO(autogpt): Cannot access attribute "hashed_password" for class "User"
    #     Attribute "hashed_password" is unknown. reportAttributeAccessIssue
    if bcrypt.checkpw(password_bytes, stored_password_hash):
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=6),
        }
        secret_key = "YOUR_SECRET_KEY"
        access_token = jwt.encode(token_data, secret_key, algorithm="HS256")
        await prisma.models.Request.prisma().create(
            data={"userId": user.id, "requestedAt": datetime.utcnow()}
        )
        return LoginResponse(access_token=access_token, token_type="Bearer")
    else:
        raise ValueError("Invalid password.")
