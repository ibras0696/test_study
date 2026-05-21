from fastapi import APIRouter

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/{id}")
async def get_id(id: int) -> dict[str, int]:
    return {'ok': id}