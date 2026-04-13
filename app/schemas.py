import datetime
from typing import List, Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True
        from_attributes = True


class BoardBase(BaseModel):
    title: str
    description: str


class BoardCreate(BoardBase):
    pass


class BoardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class BoardResponse(BoardBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True


class BoardMemberBase(BaseModel):
    user_id: int
    role: str


class ListBase(BaseModel):
    title: str
    position: int


class ListCreate(ListBase):
    board_id: int


class ListUpdate(BaseModel):
    title: Optional[str] = None
    position: Optional[int] = None

class ListResponse(ListBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True

class ListMove(BaseModel):
    position: int

class BoardWithListsResponse(BoardResponse):
    lists: List[ListResponse] = []

    class Config:
        orm_mode = True
        from_attributes = True


class CardBase(BaseModel):
    title: str
    description: Optional[str] = None
    position: int
    due_date: Optional[datetime.datetime] = None

class CardCreate(CardBase):
    list_id: int


class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[int] = None
    list_id: Optional[int] = None
    due_date: Optional[datetime.datetime] = None
  


class CardMove(BaseModel):
    list_id: int
    position: int


class CardResponse(CardBase):
    id: int
    list_id: int

    class Config:
        orm_mode = True
        from_attributes = True

class ListWithCardsResponse(ListResponse):
    cards: List[CardResponse] = []

    class Config:
        orm_mode = True
        from_attributes = True

"""
class LabelCreate(BaseModel):
    name: str
    color: str
    board_id: int


class LabelResponse(BaseModel):
    id: int
    name: str
    color: str
    board_id: int

    class Config:
        orm_mode = True
        from_attributes = True


class CardLabelBase(BaseModel):
    card_id: int
    label_id: int


class CardWithLabelsResponse(CardResponse):
    labels: List[LabelResponse] = []

    class Config:
        orm_mode = True
        from_attributes = True

"""
class CommentCreate(BaseModel):
    content: str
    card_id: int


class CommentResponse(BaseModel):
    id: int
    content: str
    card_id: int
    user_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True
        from_attributes = True



class ActivityResponse(BaseModel):
    id: int
    action: str
    user_id: int
    card_id: Optional[int]
    created_at: datetime.datetime

    class Config:
        orm_mode = True
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str