from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.login import get_current_user
from app import models, schemas

router = APIRouter(prefix="/lists", tags=["Lists"])

@router.post("/", response_model=schemas.ListResponse)
def create_list(
    list_data: schemas.ListCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    member = db.query(models.BoardMember).filter(
        models.BoardMember.board_id == list_data.board_id,
        models.BoardMember.user_id == current_user_id
    ).first()

    if not member:
        raise HTTPException(status_code=403, detail="Not authorized to create list")

    new_list = models.List(
        title=list_data.title,
        position=list_data.position,
        board_id=list_data.board_id
    )

    db.add(new_list)
    db.commit()
    db.refresh(new_list)

    db.add(models.ActivityLog(
        action="Created list",
        user_id=current_user_id
    ))
    db.commit()

    return new_list

@router.get("/board/{board_id}", response_model=list[schemas.ListResponse])
def get_lists_by_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    member = db.query(models.BoardMember).filter(
        models.BoardMember.board_id == board_id,
        models.BoardMember.user_id == current_user_id
    ).first()

    if not member:
        raise HTTPException(status_code=403, detail="Not authorized to view lists")

    lists = db.query(models.List).filter(
        models.List.board_id == board_id
    ).order_by(models.List.position).all()

    return lists

@router.get("/{list_id}", response_model=schemas.ListResponse)
def get_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    list_item = (
        db.query(models.List)
        .join(models.Board, models.List.board_id == models.Board.id)
        .join(models.BoardMember, models.Board.id == models.BoardMember.board_id)
        .filter(
            models.List.id == list_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")

    return list_item

@router.put("/{list_id}", response_model=schemas.ListResponse)
def update_list(
    list_id: int,
    list_data: schemas.ListUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    list_item = (
        db.query(models.List)
        .join(models.Board, models.List.board_id == models.Board.id)
        .join(models.BoardMember, models.Board.id == models.BoardMember.board_id)
        .filter(
            models.List.id == list_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not list_item:
        raise HTTPException(status_code=403, detail="Not authorized to update list")

    if list_data.title is not None:
        list_item.title = list_data.title

    if list_data.position is not None:
        list_item.position = list_data.position

    if list_data.is_archived is not None:
        list_item.is_archived = list_data.is_archived

    db.add(models.ActivityLog(
        action="Updated list",
        user_id=current_user_id
    ))
    db.commit()
    db.refresh(list_item)

    return list_item

@router.delete("/{list_id}")
def delete_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    list_item = (
        db.query(models.List)
        .join(models.Board, models.List.board_id == models.Board.id)
        .join(models.BoardMember, models.Board.id == models.BoardMember.board_id)
        .filter(
            models.List.id == list_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not list_item:
        raise HTTPException(status_code=403, detail="Not authorized to delete list")

    db.delete(list_item)
    db.add(models.ActivityLog(
        action="Deleted list",
        user_id=current_user_id
    ))
    db.commit()

    return {"message": "List deleted successfully"}

@router.get("/{list_id}/details", response_model=schemas.ListWithCardsResponse)
def get_list_with_cards(
    list_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    list_item = (
        db.query(models.List)
        .join(models.Board, models.List.board_id == models.Board.id)
        .join(models.BoardMember, models.Board.id == models.BoardMember.board_id)
        .filter(
            models.List.id == list_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not list_item:
        raise HTTPException(status_code=404, detail="List not found")

    cards = db.query(models.Card).filter(
        models.Card.list_id == list_id
    ).order_by(models.Card.position).all()

    return schemas.ListWithCardsResponse(
        id=list_item.id,
        title=list_item.title,
        position=list_item.position,
        is_archived=list_item.is_archived,
        cards=cards
    )


@router.patch("/{list_id}/move")
def move_list(
    list_id: int,
    data: schemas.ListMove,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    list_obj = db.query(models.List).filter(
        models.List.id == list_id
    ).first()

    if not list_obj:
        raise HTTPException(status_code=404, detail="List not found")

    list_obj.position = data.position
    db.commit()

    return {"message": "List reordered successfully"}
