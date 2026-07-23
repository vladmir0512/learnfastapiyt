from datetime import timedelta

import strawberry
from strawberry import Info
from strawberry.file_uploads import Upload

from api.graphql.decorators import require_authentication, paginate
from api.graphql.user.schemas import User, Token, UserPage
from core.services import UserService, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, user_service


@strawberry.type
class UserMutation:


    @strawberry.mutation
    async def register(self, username: str, password: str, email: str) -> User:
        await user_service.create(username=username, password=password, email=email)
        return User(username=username, email=email)

    @strawberry.mutation
    async def login(self, email: str, password: str) -> Token:
        user = await user_service.authenticate_user(email, password)
        if not user:
            raise ValueError("Incorrect username or password")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

        access_token = await UserService.create_token(data={"sub": email, "type": "access"},
                                                expires_delta=access_token_expires)
        refresh_token = await UserService.create_token(data={"sub": email, "type": "refresh"},
                                                 expires_delta=refresh_token_expires)

        return Token(access_token=access_token, refresh_token=refresh_token)


@strawberry.type
class FileMutation:

    @strawberry.mutation
    async def upload_file(self, file: Upload) -> str:
        content = await file.read()
        filename = file.filename
        with open(f"media/uploaded_{filename}", "wb") as f:
            f.write(content)
        return f"File {filename} was successfully uploaded!"


@strawberry.type
class UserQuery:

    @strawberry.field
    @require_authentication
    @paginate
    def all_users(self, info: Info, limit: int, offset: int) -> UserPage:
        return UserService.get_all()
