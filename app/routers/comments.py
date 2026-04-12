from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.login import get_current_user
from app import models, schemas

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/", response_model=schemas.CommentResponse)
def add_comment(
    comment_data: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    card = (
        db.query(models.Card)
        .join(models.List, models.Card.list_id == models.List.id)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.Card.id == comment_data.card_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not card:
        raise HTTPException(status_code=403, detail="Not authorized to add comment")

    new_comment = models.Comment(
        content=comment_data.content,
        card_id=comment_data.card_id,
        user_id=current_user_id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    db.add(
        models.ActivityLog(
            action="Added comment",
            card_id=comment_data.card_id,
            user_id=current_user_id
        )
    )
    db.commit()

    return new_comment


@router.get("/card/{card_id}", response_model=list[schemas.CommentResponse])
def get_comments_for_card(
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
        raise HTTPException(status_code=403, detail="Not authorized to view comments")

    comments = (
        db.query(models.Comment)
        .filter(models.Comment.card_id == card_id)
        .order_by(models.Comment.created_at.desc())
        .all()
    )

    return comments


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    comment = (
        db.query(models.Comment)
        .join(models.Card, models.Comment.card_id == models.Card.id)
        .join(models.List, models.Card.list_id == models.List.id)
        .join(models.BoardMember, models.List.board_id == models.BoardMember.board_id)
        .filter(
            models.Comment.id == comment_id,
            models.Comment.user_id == current_user_id
        )
        .first()
    )

    if not comment:
        raise HTTPException(status_code=403, detail="Not authorized to delete comment")

    card_id = comment.card_id

    db.delete(comment)
    db.commit()

    db.add(
        models.ActivityLog(
            action="Deleted comment",
            card_id=card_id,
            user_id=current_user_id
        )
    )
    db.commit()

    return {"message": "Comment deleted successfully"}