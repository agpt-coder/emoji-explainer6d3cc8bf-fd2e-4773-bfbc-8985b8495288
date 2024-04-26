import logging
from contextlib import asynccontextmanager

import project.createEmojiExplanation_service
import project.deleteUser_service
import project.explainEmoji_service
import project.fetchEmojiExplanation_service
import project.getUserProfile_service
import project.listUsers_service
import project.loginUser_service
import project.processEmojiInput_service
import project.registerUser_service
import project.updateUser_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="emoji-explainer",
    lifespan=lifespan,
    description="create a single endpoint that takes in an emoji and responds with the explaination. Use Groq and specifically llama3 to get the explaination from",
)


@app.delete("/user", response_model=project.deleteUser_service.DeleteUserResponse)
async def api_delete_deleteUser(
    user_id: int,
) -> project.deleteUser_service.DeleteUserResponse | Response:
    """
    Allows a user to delete their account using their user ID. Requires authentication and is restricted to ensure only the account owner can delete their profile.
    """
    try:
        res = await project.deleteUser_service.deleteUser(user_id)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/emoji",
    response_model=project.createEmojiExplanation_service.EmojiExplanationResponseModel,
)
async def api_post_createEmojiExplanation(
    emoji_character: str,
) -> project.createEmojiExplanation_service.EmojiExplanationResponseModel | Response:
    """
    Processes an emoji sent by the user and returns its explanation by leveraging the GROQ query language over the llama3 dataset. Requires authentication to ensure only registered users can access.
    """
    try:
        res = await project.createEmojiExplanation_service.createEmojiExplanation(
            emoji_character
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put("/user", response_model=project.updateUser_service.UpdateUserProfileResponse)
async def api_put_updateUser(
    email: str, password: str, username: str
) -> project.updateUser_service.UpdateUserProfileResponse | Response:
    """
    Enables users to update their profile details such as email, password, and username. Requires an access token to ensure authentication and that non-admin users can only edit their own account.
    """
    try:
        res = await project.updateUser_service.updateUser(email, password, username)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/explain", response_model=project.explainEmoji_service.EmojiExplanationResponse
)
async def api_post_explainEmoji(
    emoji: str,
) -> project.explainEmoji_service.EmojiExplanationResponse | Response:
    """
    This endpoint accepts a POST request containing a JSON body with an emoji character. It processes the input to extract the emoji and sends it to the Emoji Input Processor module. Upon receiving the processed emoji, it queries the Explanation Generator which uses the Groq and llama3 to fetch an accurate explanation of the emoji. The response will be a JSON object containing the original emoji and its explanation. It ensures that data encoding and transfer are handled efficiently to maintain the request-response cycle's speed.
    """
    try:
        res = await project.explainEmoji_service.explainEmoji(emoji)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/api/emoji/process",
    response_model=project.processEmojiInput_service.EmojiProcessResponse,
)
async def api_post_processEmojiInput(
    emoji_character: str,
) -> project.processEmojiInput_service.EmojiProcessResponse | Response:
    """
    This endpoint accepts an emoji character as input through POST request. It validates the input to ensure it's a proper emoji character. Upon successful validation, it forwards the emoji to the Explanation Generator module which uses llama3 with Groq to fetch the explanation. The client then receives a response with the description of the emoji. If the input is not valid, a 400 error code is generated with a message explaining the error.
    """
    try:
        res = await project.processEmojiInput_service.processEmojiInput(emoji_character)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get("/users", response_model=project.listUsers_service.AdminUserListResponse)
async def api_get_listUsers(
    request: project.listUsers_service.AdminUserListRequest,
) -> project.listUsers_service.AdminUserListResponse | Response:
    """
    Provides a list of all registered users. Restricted to administrators only. Useful for user management and monitoring purposes.
    """
    try:
        res = await project.listUsers_service.listUsers(request)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get("/user", response_model=project.getUserProfile_service.UserProfileResponse)
async def api_get_getUserProfile(
    access_token: str,
) -> project.getUserProfile_service.UserProfileResponse | Response:
    """
    Returns the profile information of thee authenticated user. Requires an access token to verify the user's identity. This ensures that users can only access their own information.
    """
    try:
        res = await project.getUserProfile_service.getUserProfile(access_token)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/register", response_model=project.registerUser_service.UserRegistrationResponse
)
async def api_post_registerUser(
    username: str, email: str, password: str
) -> project.registerUser_service.UserRegistrationResponse | Response:
    """
    This endpoint allows a new user to register. It accepts username, email, and password, and upon successful registration, it returns a user object and an authentication token. The endpoint does not require authentication.
    """
    try:
        res = await project.registerUser_service.registerUser(username, email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/login", response_model=project.loginUser_service.LoginResponse)
async def api_post_loginUser(
    email: str, password: str
) -> project.loginUser_service.LoginResponse | Response:
    """
    Allows a user to log in by providing an email and password. If credentials are valid, it returns an access token, which is required for making authenticated requests to protected routes.
    """
    try:
        res = await project.loginUser_service.loginUser(email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/api/explanation",
    response_model=project.fetchEmojiExplanation_service.EmojiExplanationResponse,
)
async def api_post_fetchEmojiExplanation(
    emoji_character: str,
) -> project.fetchEmojiExplanation_service.EmojiExplanationResponse | Response:
    """
    This endpoint accepts a POST request containing an emoji character in the request body. It utilizes Groq to query the llama3 model to generate an explanation of the emoji. The response includes the original emoji and its explanation. Intermediate processing stages include handling the request data in the Emoji Input Processor, querying the llama3 model, and finally, the Explanation Generator formulates the proper response format before sending it back to the API Gateway.
    """
    try:
        res = await project.fetchEmojiExplanation_service.fetchEmojiExplanation(
            emoji_character
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
