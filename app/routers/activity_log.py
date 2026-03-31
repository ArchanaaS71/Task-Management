from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/activity",
    tags=["Activity Log"]
)

@router.post("/", response_model=schemas.ActivityResponse)
def add_log(
    log_data: schemas.ActivityResponse,  
    db: Session = Depends(get_db)
):

    card = db.query(models.Card).filter(models.Card.id == log_data.card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")


    user = db.query(models.User).filter(models.User.id == log_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_log = models.ActivityLog(
        action=log_data.action,
        card_id=log_data.card_id,
        user_id=log_data.user_id
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log


@router.get("/card/{card_id}", response_model=list[schemas.ActivityResponse])
def get_logs_for_card(card_id: int, db: Session = Depends(get_db)):

    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    logs = (
        db.query(models.ActivityLog)
        .filter(models.ActivityLog.card_id == card_id)
        .order_by(models.ActivityLog.created_at.desc())
        .all()
    )

    return logs


@router.get("/board/{board_id}", response_model=list[schemas.ActivityResponse])
def get_logs_for_board(board_id: int, db: Session = Depends(get_db)):

    
    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    lists = db.query(models.List).filter(models.List.board_id == board_id).all()
    list_ids = [lst.id for lst in lists]

    cards = db.query(models.Card).filter(models.Card.list_id.in_(list_ids)).all()
    card_ids = [c.id for c in cards]

    logs = (
        db.query(models.ActivityLog)
        .filter(models.ActivityLog.card_id.in_(card_ids))
        .order_by(models.ActivityLog.created_at.desc())
        .all()
    )

    return logs


@router.delete("/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db)):

    log = db.query(models.ActivityLog).filter(models.ActivityLog.id == log_id).first()

    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")

    db.delete(log)
    db.commit()

    return {"message": "Activity log deleted successfully"}