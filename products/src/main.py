import strawberry
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter

from api.graphql.resolvers import Mutation, Query
from api.rest.product.views import products_router
from api.rest.views import users_router
from dependencies import context_dependency

app = FastAPI()



api_v1_router = APIRouter(prefix="/v1/api")
api_v1_router.include_router(products_router)
api_v1_router.include_router(users_router)
app.include_router(api_v1_router)


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=context_dependency, multipart_uploads_enabled=True)

app.include_router(graphql_app, prefix="/v1/graphql")
app.mount("/media", StaticFiles(directory="media"), name="media")