from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.login import get_current_user
from app import models, schemas

router = APIRouter(prefix="/boards", tags=["Boards"])

@router.post("/", response_model=schemas.BoardResponse)
def create_board(
    board_data: schemas.BoardCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    new_board = models.Board(
        title=board_data.title,
        description=board_data.description,
        owner_id=current_user_id
    )

    db.add(new_board)
    db.commit()
    db.refresh(new_board)

    board_member = models.BoardMember(
        board_id=new_board.id,
        user_id=current_user_id,
        role="owner"
    )

    db.add(board_member)
    db.add(models.ActivityLog(
        action="Created board",
        user_id=current_user_id
    ))
    db.commit()

    return new_board


@router.get("/", response_model=list[schemas.BoardResponse])
def get_boards(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    boards = (
        db.query(models.Board)
        .join(models.BoardMember)
        .filter(models.BoardMember.user_id == current_user_id)
        .all()
    )
    return boards


@router.get("/{board_id}", response_model=schemas.BoardResponse)
def get_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    board = (
        db.query(models.Board)
        .join(models.BoardMember)
        .filter(
            models.Board.id == board_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    return board


@router.put("/{board_id}", response_model=schemas.BoardResponse)
def update_board(
    board_id: int,
    board_data: schemas.BoardUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    board = db.query(models.Board).filter(
        models.Board.id == board_id,
        models.Board.owner_id == current_user_id
    ).first()

    if not board:
        raise HTTPException(status_code=403, detail="Not authorized to update board")

    if board_data.title is not None:
        board.title = board_data.title

    if board_data.description is not None:
        board.description = board_data.description

    if board_data.is_archived is not None:
        board.is_archived = board_data.is_archived

    db.add(models.ActivityLog(
        action="Updated board",
        user_id=current_user_id
    ))
    db.commit()
    db.refresh(board)

    return board


@router.delete("/{board_id}")
def delete_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    board = db.query(models.Board).filter(
        models.Board.id == board_id,
        models.Board.owner_id == current_user_id
    ).first()

    if not board:
        raise HTTPException(status_code=403, detail="Not authorized to delete board")

    db.delete(board)
    db.add(models.ActivityLog(
        action="Deleted board",
        user_id=current_user_id
    ))
    db.commit()

    return {"message": "Board deleted successfully"}


@router.post("/{board_id}/members")
def add_board_member(
    board_id: int,
    member_data: schemas.BoardMemberBase,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    board = db.query(models.Board).filter(
        models.Board.id == board_id,
        models.Board.owner_id == current_user_id
    ).first()

    if not board:
        raise HTTPException(status_code=403, detail="Only board owner can add members")

    existing_member = db.query(models.BoardMember).filter(
        models.BoardMember.board_id == board_id,
        models.BoardMember.user_id == member_data.user_id
    ).first()

    if existing_member:
        raise HTTPException(status_code=400, detail="User already a member")

    new_member = models.BoardMember(
        board_id=board_id,
        user_id=member_data.user_id,
        role=member_data.role
    )

    db.add(new_member)
    db.add(models.ActivityLog(
        action="Added board member",
        user_id=current_user_id
    ))
    db.commit()

    return {"message": "Member added successfully"}


@router.get("/{board_id}/details", response_model=schemas.BoardWithListsResponse)
def get_board_with_lists(
    board_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    board = (
        db.query(models.Board)
        .join(models.BoardMember)
        .filter(
            models.Board.id == board_id,
            models.BoardMember.user_id == current_user_id
        )
        .first()
    )

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

@router.patch("/{board_id}/lists/reorder")
def reorder_lists(
    board_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    list_ids = data.get("list_ids")

    if not list_ids:
        raise HTTPException(status_code=400, detail="list_ids required")

    lists = (
        db.query(models.List)
        .filter(models.List.board_id == board_id)
        .all()
    )

    list_map = {l.id: l for l in lists}

    for index, list_id in enumerate(list_ids):
        if list_id in list_map:
            list_map[list_id].position = index + 1

    db.commit()
    return {"message": "Lists reordered successfully"}