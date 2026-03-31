from fastapi import FastAPI,status, HTTPException

from .routers import board, card, lists, login, user
from .import schemas
from .import models
from fastapi.params import Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .database import engine, SessionLocal, get_db

app = FastAPI(title="Task Management API",
              description="This API allows you to manage tasks, boards, lists, cards, labels, and comments in a task management application.",
              terms_of_service="http://example.com/terms/",
              contact={"name":"Archanaa",
                       "website":"https://archanaa.com",
                       "email":"archanaa@example.com"
                        },
              license_info=
              {
                  'name':'mit license',
                  'url':'https://choosealicense.com/licenses/mit/'

              },
            #docs_url="/documentation",redoc_url=None

)

app.include_router(board.router)
app.include_router(card.router)
app.include_router(lists.router)
app.include_router(user.router)
#app.include_router(login.router)
models.Base.metadata.create_all(engine)

