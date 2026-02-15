from fastapi import HTTPException

def require_admin_token(expected: str, provided: str | None):
    if not provided or provided != expected:
        raise HTTPException(status_code=403, detail="admin token invalid")