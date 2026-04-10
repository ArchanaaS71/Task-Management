from fastapi import FastAPI

from app.database import engine
from app import models
from app.routers import (
    board,
    lists,
    card,
    comments,
    labels,
    activity_log,
    login,
    user
)

app = FastAPI(
    title="Task Management API",
    description="This API allows you to manage tasks, boards, lists, cards, labels, and comments in a task management application.",
    version="1.0.0",
    contact={"name":"Archanaa",
                       "website":"https://archanaa.com",
                       "email":"archanaa@example.com"
                        }
)

app.include_router(login.router)
app.include_router(user.router)
app.include_router(board.router)
app.include_router(lists.router)
app.include_router(card.router)
app.include_router(comments.router)
app.include_router(labels.router)
app.include_router(activity_log.router)

models.Base.metadata.create_all(bind=engine)