from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.login import get_current_user
from app import models, schemas

router = APIRouter(prefix="/activity", tags=["Activity"])

@router.get("/card/{card_id}", response_model=list[schemas.ActivityResponse])
def get_activity_for_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    card = (
        db.query(models.Card)
        .join(models.List, models.Card.list_id == models.List.id)
        .join(models.Board, models.List.board_id == models.Board.id)
        .join(models.BoardMember, models.Board.id == models.BoardMember.board_id)
        .filter(
            models.Card.id == card_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not card:
        raise HTTPException(status_code=403, detail="Not authorized to view activity")

    logs = (
        db.query(models.ActivityLog)
        .filter(models.ActivityLog.card_id == card_id)
        .order_by(models.ActivityLog.created_at.desc())
        .all()
    )

    return logs
"""
@router.get("/board/{board_id}", response_model=list[schemas.ActivityResponse])
def get_activity_for_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    member = (
        db.query(models.BoardMember)
        .filter(
            models.BoardMember.board_id == board_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not member:
        raise HTTPException(status_code=403, detail="Not authorized to view activity")

    card_ids = (
        db.query(models.Card.id)
        .join(models.List, models.Card.list_id == models.List.id)
        .filter(models.List.board_id == board_id)
        .all()
    )

    card_id_list = [c.id for c in card_ids]

    logs = (
        db.query(models.ActivityLog)
        .filter(models.ActivityLog.card_id.in_(card_id_list))
        .order_by(models.ActivityLog.created_at.desc())
        .all()
    )

    return logs

@router.get("/card/{card_id}")
def get_card_activity(
    card_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    activities = (
        db.query(models.ActivityLog)
        .filter(models.ActivityLog.card_id == card_id)
        .order_by(models.ActivityLog.created_at.desc())
        .all()
    )

    return activities
"""