from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/labels",
    tags=["Labels"]
)

@router.post("/", response_model=schemas.LabelResponse)
def create_label(label_data: schemas.LabelCreate, db: Session = Depends(get_db)):

    board = db.query(models.Board).filter(models.Board.id == label_data.board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    new_label = models.Label(
        name=label_data.name,
        color=label_data.color,
        board_id=label_data.board_id
    )

    db.add(new_label)
    db.commit()
    db.refresh(new_label)

    return new_label

@router.get("/board/{board_id}", response_model=list[schemas.LabelResponse])
def get_labels_for_board(board_id: int, db: Session = Depends(get_db)):

    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    labels = db.query(models.Label).filter(models.Label.board_id == board_id).all()

    return labels

@router.post("/assign")
def assign_label_to_card(
    data: schemas.CardLabelBase,
    db: Session = Depends(get_db)
):
    card = db.query(models.Card).filter(models.Card.id == data.card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    label = db.query(models.Label).filter(models.Label.id == data.label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    existing = (
        db.query(models.CardLabel)
        .filter(
            models.CardLabel.card_id == data.card_id,
            models.CardLabel.label_id == data.label_id
        ).first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Label already assigned to card")

    new_mapping = models.CardLabel(
        card_id=data.card_id,
        label_id=data.label_id
    )

    db.add(new_mapping)
    db.commit()

    return {"message": "Label assigned to card successfully"}

@router.delete("/remove")
def remove_label_from_card(
    data: schemas.CardLabelBase,
    db: Session = Depends(get_db)
):

    mapping = (
        db.query(models.CardLabel)
        .filter(
            models.CardLabel.card_id == data.card_id,
            models.CardLabel.label_id == data.label_id
        )
        .first()
    )

    if not mapping:
        raise HTTPException(status_code=404, detail="Label assignment not found")

    db.delete(mapping)
    db.commit()

    return {"message": "Label removed from card successfully"}

@router.delete("/{label_id}")
def delete_label(label_id: int, db: Session = Depends(get_db)):

    label = db.query(models.Label).filter(models.Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    db.query(models.CardLabel).filter(models.CardLabel.label_id == label_id).delete()

    db.delete(label)
    db.commit()

    return {"message": "Label deleted successfully"}

@router.get("/{card_id}/details", response_model=schemas.CardWithLabelsResponse)
def get_card_with_labels(card_id: int, db: Session = Depends(get_db)):

    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    mappings = db.query(models.CardLabel).filter(models.CardLabel.card_id == card_id).all()

    label_ids = [m.label_id for m in mappings]
    labels = db.query(models.Label).filter(models.Label.id.in_(label_ids)).all() if label_ids else []

    return schemas.CardWithLabelsResponse(
        id=card.id,
        title=card.title,
        description=card.description,
        position=card.position,
        list_id=card.list_id,
        due_date=card.due_date,
        reminder_date=card.reminder_date,
        labels=labels
    )