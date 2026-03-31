from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/lists",
    tags=["Lists"]
)

@router.post("/", response_model=schemas.ListResponse)
def create_list(list_data: schemas.ListCreate, db: Session = Depends(get_db)):

    # Check if board exists
    board = db.query(models.Board).filter(models.Board.id == list_data.board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    new_list = models.List(
        title=list_data.title,
        position=list_data.position,
        board_id=list_data.board_id
    )

    db.add(new_list)
    db.commit()
    db.refresh(new_list)

    return new_list


@router.get("/board/{board_id}", response_model=list[schemas.ListResponse])
def get_lists_by_board(board_id: int, db: Session = Depends(get_db)):

    # Check if board exists
    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    lists = db.query(models.List).filter(models.List.board_id == board_id).all()

    return lists

@router.get("/{list_id}", response_model=schemas.ListResponse)
def get_list(list_id: int, db: Session = Depends(get_db)):

    list_item = db.query(models.List).filter(models.List.id == list_id).first()

    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")

    return list_item

@router.put("/{list_id}", response_model=schemas.ListResponse)
def update_list(
    list_id: int,
    updated_data: schemas.ListUpdate,
    db: Session = Depends(get_db)
):

    list_item = db.query(models.List).filter(models.List.id == list_id).first()

    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")

    if updated_data.title is not None:
        list_item.title = updated_data.title

    if updated_data.position is not None:
        list_item.position = updated_data.position

    if updated_data.is_archived is not None:
        list_item.is_archived = updated_data.is_archived

    db.commit()
    db.refresh(list_item)

    return list_item


@router.delete("/{list_id}")
def delete_list(list_id: int, db: Session = Depends(get_db)):

    list_item = db.query(models.List).filter(models.List.id == list_id).first()

    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")

    db.delete(list_item)
    db.commit()

    return {"message": "List deleted successfully"}

@router.get("/{list_id}/details", response_model=schemas.ListWithCardsResponse)
def get_list_with_cards(list_id: int, db: Session = Depends(get_db)):

    list_item = db.query(models.List).filter(models.List.id == list_id).first()
    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")

    cards = db.query(models.Card).filter(models.Card.list_id == list_id).all()

    return schemas.ListWithCardsResponse(
        id=list_item.id,
        title=list_item.title,
        position=list_item.position,
        is_archived=list_item.is_archived,
        cards=cards
    )