from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)

CURRENT_USER_ID = 1  

@router.post("/", response_model=schemas.CommentResponse)
def add_comment(comment_data: schemas.CommentCreate, db: Session = Depends(get_db)):

    card = db.query(models.Card).filter(models.Card.id == comment_data.card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    user = db.query(models.User).filter(models.User.id == comment_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_comment = models.Comment(
        content=comment_data.content,
        card_id=comment_data.card_id,
        user_id=comment_data.user_id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    log_entry = models.ActivityLog(
        action=f"Added a comment: \"{comment_data.content}\"",
        card_id=comment_data.card_id,
        user_id=comment_data.user_id  
    )
    db.add(log_entry)
    db.commit()

    return new_comment


@router.get("/card/{card_id}", response_model=list[schemas.CommentResponse])
def get_comments_for_card(card_id: int, db: Session = Depends(get_db)):

    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    comments = (
        db.query(models.Comment)
        .filter(models.Comment.card_id == card_id)
        .order_by(models.Comment.created_at.asc())
        .all()
    )

    return comments


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    card_id = comment.card_id
    content = comment.content
    user_id = comment.user_id

    db.delete(comment)
    db.commit()

    log_entry = models.ActivityLog(
        action=f"Deleted a comment: \"{content}\"",
        card_id=card_id,
        user_id=user_id
    )
    db.add(log_entry)
    db.commit()

    return {"message": "Comment deleted successfully"}