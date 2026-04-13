
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.login import get_current_user
from app import models, schemas
"""
router = APIRouter(prefix="/labels", tags=["Labels"])

@router.post("/", response_model=schemas.LabelResponse)
def create_label(
    label_data: schemas.LabelCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    member = db.query(models.BoardMember).filter(
        models.BoardMember.board_id == label_data.board_id,
        models.BoardMember.user_id == current_user_id
    ).first()

    if not member:
        raise HTTPException(status_code=403, detail="Not authorized to create label")

    new_label = models.Label(
        name=label_data.name,
        color=label_data.color,
        board_id=label_data.board_id
    )

    db.add(new_label)
    db.commit()
    db.refresh(new_label)

    db.add(models.ActivityLog(
        action="Created label",
        user_id=current_user_id
    ))
    db.commit()

    return new_label

@router.get("/board/{board_id}", response_model=list[schemas.LabelResponse])
def get_labels_for_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    member = db.query(models.BoardMember).filter(
        models.BoardMember.board_id == board_id,
        models.BoardMember.user_id == current_user_id
    ).first()

    if not member:
        raise HTTPException(status_code=403, detail="Not authorized to view labels")

    labels = db.query(models.Label).filter(
        models.Label.board_id == board_id
    ).all()

    return labels

@router.post("/assign")
def assign_label_to_card(
    data: schemas.CardLabelBase,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    card = (
        db.query(models.Card)
        .join(models.List, models.Card.list_id == models.List.id)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.Card.id == data.card_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not card:
        raise HTTPException(status_code=403, detail="Not authorized to assign label")

    existing = db.query(models.CardLabel).filter(
        models.CardLabel.card_id == data.card_id,
        models.CardLabel.label_id == data.label_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Label already assigned")

    new_mapping = models.CardLabel(
        card_id=data.card_id,
        label_id=data.label_id
    )

    db.add(new_mapping)
    db.add(models.ActivityLog(
        action="Assigned label",
        card_id=data.card_id,
        user_id=current_user_id
    ))
    db.commit()

    return {"message": "Label assigned successfully"}

@router.delete("/remove")
def remove_label_from_card(
    data: schemas.CardLabelBase,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    mapping = (
        db.query(models.CardLabel)
        .join(models.Card, models.CardLabel.card_id == models.Card.id)
        .join(models.List, models.Card.list_id == models.List.id)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.CardLabel.card_id == data.card_id,
            models.CardLabel.label_id == data.label_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not mapping:
        raise HTTPException(status_code=404, detail="Label assignment not found")

    db.delete(mapping)
    db.add(models.ActivityLog(
        action="Removed label",
        card_id=data.card_id,
        user_id=current_user_id
    ))
    db.commit()

    return {"message": "Label removed successfully"}

@router.delete("/{label_id}")
def delete_label(
    label_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    label = (
        db.query(models.Label)
        .join(models.Board, models.Label.board_id == models.Board.id)
        .join(models.BoardMember, models.Board.id == models.BoardMember.board_id)
        .filter(
            models.Label.id == label_id,
            models.BoardMember.user_id == current_user_id,
            models.BoardMember.role == "owner"
        )
        .first()
    )

    if not label:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete label"
        )

    db.query(models.CardLabel).filter(
        models.CardLabel.label_id == label_id
    ).delete()

    db.delete(label)
    db.commit()

    return {"message": "Label deleted successfully"}


@router.get("/{card_id}/details", response_model=schemas.CardWithLabelsResponse)
def get_card_with_labels(
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

    mappings = db.query(models.CardLabel).filter(
        models.CardLabel.card_id == card_id
    ).all()

    label_ids = [m.label_id for m in mappings]

    labels = []
    if label_ids:
        labels = db.query(models.Label).filter(
            models.Label.id.in_(label_ids)
        ).all()

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
"""