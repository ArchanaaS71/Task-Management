from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.login import get_current_user
from app import models, schemas

router = APIRouter(prefix="/cards", tags=["Cards"])

@router.post("/", response_model=schemas.CardResponse)
def create_card(
    card_data: schemas.CardCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    list_item = (
        db.query(models.List)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.List.id == card_data.list_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not list_item:
        raise HTTPException(status_code=403, detail="Not authorized to create card")

    new_card = models.Card(
        title=card_data.title,
        description=card_data.description,
        position=card_data.position,
        due_date=card_data.due_date,
        reminder_date=card_data.reminder_date,
        list_id=card_data.list_id
    )

    db.add(new_card)
    db.commit()
    db.refresh(new_card)

    db.add(models.ActivityLog(
        action="Created card",
        card_id=new_card.id,
        user_id=current_user_id
    ))
    db.commit()

    return new_card

@router.get("/list/{list_id}", response_model=list[schemas.CardResponse])
def get_cards_by_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    list_item = (
        db.query(models.List)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.List.id == list_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not list_item:
        raise HTTPException(status_code=403, detail="Not authorized to view cards")

    cards = (
        db.query(models.Card)
        .filter(models.Card.list_id == list_id)
        .order_by(models.Card.position)
        .all()
    )

    return cards

@router.get("/{card_id}", response_model=schemas.CardResponse)
def get_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    card = (
        db.query(models.Card)
        .join(models.List, models.Card.list_id == models.List.id)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.Card.id == card_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    return card

@router.put("/{card_id}", response_model=schemas.CardResponse)
def update_card(
    card_id: int,
    card_data: schemas.CardUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    card = (
        db.query(models.Card)
        .join(models.List, models.Card.list_id == models.List.id)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.Card.id == card_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not card:
        raise HTTPException(status_code=403, detail="Not authorized to update card")

    if card_data.title is not None:
        card.title = card_data.title

    if card_data.description is not None:
        card.description = card_data.description

    if card_data.position is not None:
        card.position = card_data.position

    if card_data.due_date is not None:
        card.due_date = card_data.due_date

    if card_data.reminder_date is not None:
        card.reminder_date = card_data.reminder_date

    if card_data.list_id is not None:
        new_list = (
            db.query(models.List)
            .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
            .filter(
                models.List.id == card_data.list_id,
                models.BoardMember.user_id == current_user_id
            )
            .first()
        )

        if not new_list:
            raise HTTPException(status_code=403, detail="Not authorized to move card")

        card.list_id = card_data.list_id

    db.add(models.ActivityLog(
        action="Updated card",
        card_id=card.id,
        user_id=current_user_id
    ))
    db.commit()
    db.refresh(card)

    return card

@router.patch("/{card_id}/move", response_model=schemas.CardResponse)
def move_card(
    card_id: int,
    move_data: schemas.CardMove,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    card = (
        db.query(models.Card)
        .join(models.List, models.Card.list_id == models.List.id)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.Card.id == card_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not card:
        raise HTTPException(status_code=403, detail="Not authorized to move card")

    target_list = (
        db.query(models.List)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.List.id == move_data.list_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not target_list:
        raise HTTPException(status_code=403, detail="Target list not accessible")

    card.list_id = move_data.list_id
    card.position = move_data.position

    db.add(models.ActivityLog(
        action="Moved card",
        card_id=card.id,
        user_id=current_user_id
    ))
    db.commit()
    db.refresh(card)

    return card

@router.delete("/{card_id}")
def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    card = (
        db.query(models.Card)
        .join(models.List, models.Card.list_id == models.List.id)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.Card.id == card_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not card:
        raise HTTPException(status_code=403, detail="Not authorized to delete card")

    db.delete(card)
    db.add(models.ActivityLog(
        action="Deleted card",
        card_id=card.id,
        user_id=current_user_id
    ))
    db.commit()

    return {"message": "Card deleted successfully"}

@router.patch("/{card_id}/description")
def update_card_description(
    card_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    card = (
        db.query(models.Card)
        .join(models.List, models.Card.list_id == models.List.id)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.Card.id == card_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not card:
        raise HTTPException(status_code=403, detail="Not authorized")

    card.description = data.get("description")
    db.commit()

    db.add(
        models.ActivityLog(
            action="Updated description",
            card_id=card_id,
            user_id=current_user_id
        )
    )
    db.commit()

    return {"message": "Description updated"}


@router.patch("/{card_id}/due-date")
def update_card_due_date(
    card_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    card = (
        db.query(models.Card)
        .join(models.List, models.Card.list_id == models.List.id)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.Card.id == card_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not card:
        raise HTTPException(status_code=403, detail="Not authorized")

    due_date_str = data.get("due_date")

    if due_date_str:
        card.due_date = datetime.fromisoformat(due_date_str)
    else:
        card.due_date = None

    db.add(card)
    db.commit()
    db.refresh(card)

    db.add(
        models.ActivityLog(
            action="Updated due date",
            card_id=card_id,
            user_id=current_user_id
        )
    )
    db.commit()

    return card