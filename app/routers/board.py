from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/boards",
    tags=["Boards"]
)

@router.post("/", response_model=schemas.BoardResponse)
def create_board(board: schemas.BoardCreate, db: Session = Depends(get_db)):

    owner_id = 1   

    new_board = models.Board(
        title=board.title,
        description=board.description,
        owner_id=owner_id
    )

    db.add(new_board)
    db.commit()
    db.refresh(new_board)

    owner_member = models.BoardMember(
        board_id=new_board.id,
        user_id=owner_id,
        role="owner"
    )

    db.add(owner_member)
    db.commit()

    return new_board

@router.get("/", response_model=list[schemas.BoardResponse])
def get_all_boards(db: Session = Depends(get_db)):

    user_id = 1

    boards = (
        db.query(models.Board)
        .join(models.BoardMember, models.Board.id == models.BoardMember.board_id)
        .filter(models.BoardMember.user_id == user_id)
        .all()
    )
    return boards


@router.get("/{board_id}", response_model=schemas.BoardResponse)
def get_board(board_id: int, db: Session = Depends(get_db)):

    board = db.query(models.Board).filter(models.Board.id == board_id).first()

    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    return board

@router.put("/{board_id}", response_model=schemas.BoardResponse)
def update_board(
    board_id: int,
    updated_data: schemas.BoardUpdate,
    db: Session = Depends(get_db),
):

    board = db.query(models.Board).filter(models.Board.id == board_id).first()

    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    if updated_data.title:
        board.title = updated_data.title

    if updated_data.description:
        board.description = updated_data.description

    if updated_data.is_archived is not None:
        board.is_archived = updated_data.is_archived

    db.commit()
    db.refresh(board)

    return board

@router.delete("/{board_id}")
def delete_board(board_id: int, db: Session = Depends(get_db)):

    board = db.query(models.Board).filter(models.Board.id == board_id).first()

    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    db.delete(board)
    db.commit()

    return {"message": "Board deleted successfully"}

@router.post("/{board_id}/members")
def add_member(
    board_id: int,
    member: schemas.BoardMemberBase,
    db: Session = Depends(get_db)
):
    board = db.query(models.Board).filter(models.Board.id == board_id).first()

    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    existing_member = (
        db.query(models.BoardMember)
        .filter(
            models.BoardMember.board_id == board_id,
            models.BoardMember.user_id == member.user_id,
        )
        .first()
    )

    if existing_member:
        raise HTTPException(
            status_code=400, detail="User is already a member of this board"
        )

    new_member = models.BoardMember(
        board_id=board_id,
        user_id=member.user_id,
        role=member.role
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return {"message": "Member added successfully"}

@router.get("/{board_id}/details", response_model=schemas.BoardWithListsResponse)
def get_board_with_lists(board_id: int, db: Session = Depends(get_db)):

    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    lists = (
        db.query(models.List)
        .filter(models.List.board_id == board_id)
        .order_by(models.List.position)
        .all()
    )
    return schemas.BoardWithListsResponse(
        id=board.id,
        title=board.title,
        description=board.description,
        owner_id=board.owner_id,
        is_archived=board.is_archived,
        created_at=board.created_at,
        updated_at=board.updated_at,
        lists=lists
    )