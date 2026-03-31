from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/cards",
    tags=["Cards"]
)

@router.post("/", response_model=schemas.CardResponse)
def create_card(card_data: schemas.CardCreate, db: Session = Depends(get_db)):

    list_obj = db.query(models.List).filter(models.List.id == card_data.list_id).first()
    if not list_obj:
        raise HTTPException(status_code=404, detail="List not found")

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

    return new_card

@router.get("/list/{list_id}", response_model=list[schemas.CardResponse])
def get_cards_by_list(list_id: int, db: Session = Depends(get_db)):

    list_obj = db.query(models.List).filter(models.List.id == list_id).first()
    if not list_obj:
        raise HTTPException(status_code=404, detail="List not found")

    cards = db.query(models.Card).filter(models.Card.list_id == list_id).order_by(models.Card.position).all()
    return cards


@router.get("/{card_id}", response_model=schemas.CardResponse)
def get_card(card_id: int, db: Session = Depends(get_db)):

    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    return card

@router.put("/{card_id}", response_model=schemas.CardResponse)
def update_card(
    card_id: int,
    update_data: schemas.CardUpdate,
    db: Session = Depends(get_db)
):

    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    if update_data.title is not None:
        card.title = update_data.title

    if update_data.description is not None:
        card.description = update_data.description

    if update_data.position is not None:
        card.position = update_data.position

    if update_data.due_date is not None:
        card.due_date = update_data.due_date

    if update_data.reminder_date is not None:
        card.reminder_date = update_data.reminder_date


    if update_data.list_id is not None:
        new_list = db.query(models.List).filter(models.List.id == update_data.list_id).first()
        if not new_list:
            raise HTTPException(status_code=404, detail="New list not found")
        card.list_id = update_data.list_id

    db.commit()
    db.refresh(card)

    return card

@router.delete("/{card_id}")
def delete_card(card_id: int, db: Session = Depends(get_db)):

    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    db.delete(card)
    db.commit()

    return {"message": "Card deleted successfully"}