"""Account management API endpoints."""

import json
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.database import db
from app.services.gmail import gmail_manager

settings = get_settings()
router = APIRouter(prefix="/accounts", tags=["accounts"])


class AddAccountRequest(BaseModel):
    """Request model for adding an account."""
    email: str
    access_token: str
    refresh_token: str


@router.get("")
async def get_accounts() -> List[Dict[str, Any]]:
    """Get all Gmail accounts."""
    return db.get_gmail_accounts()


@router.get("/active")
async def get_active_accounts() -> List[Dict[str, Any]]:
    """Get only active Gmail accounts."""
    return db.get_active_gmail_accounts()


@router.get("/{account_id}")
async def get_account(account_id: str) -> Dict[str, Any]:
    """Get a specific account."""
    account = db.get_gmail_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post("")
async def add_account(request: AddAccountRequest) -> Dict[str, Any]:
    """Add a new Gmail account."""
    # Check if account already exists
    accounts = db.get_gmail_accounts()
    for acc in accounts:
        if acc.get("email") == request.email:
            raise HTTPException(status_code=400, detail="Account already exists")

    # Check global Gmail client config is set
    if not settings.gmail_client_id or not settings.gmail_client_secret:
        raise HTTPException(
            status_code=400,
            detail="GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET must be set in environment"
        )

    # Build OAuth credentials with global client config
    oauth_credentials = {
        "access_token": request.access_token,
        "refresh_token": request.refresh_token,
        "client_id": settings.gmail_client_id,
        "client_secret": settings.gmail_client_secret,
    }

    # Add to database
    new_account = db.add_gmail_account(
        email=request.email,
        oauth_credentials=oauth_credentials,
        status="active",
    )

    # Add to Gmail manager
    gmail_manager.add_account(
        account_id=str(new_account.get("id", "")),
        email=request.email,
        oauth_credentials=oauth_credentials,
    )

    return new_account


@router.post("/{account_id}/pause")
async def pause_account(account_id: str) -> Dict[str, Any]:
    """Pause a Gmail account."""
    account = db.get_gmail_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    updated = db.update_gmail_account(account_id, {"status": "paused"})
    return updated


@router.post("/{account_id}/resume")
async def resume_account(account_id: str) -> Dict[str, Any]:
    """Resume a Gmail account."""
    account = db.get_gmail_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    updated = db.update_gmail_account(account_id, {"status": "active"})
    return updated


@router.delete("/{account_id}")
async def delete_account(account_id: str) -> Dict[str, str]:
    """Delete a Gmail account."""
    account = db.get_gmail_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Remove from manager
    gmail_manager.remove_account(account_id)

    # Delete from database
    db.delete_gmail_account(account_id)

    return {"status": "deleted", "account_id": account_id}


@router.post("/{account_id}/reset-daily")
async def reset_daily_count(account_id: str) -> Dict[str, Any]:
    """Reset daily sent count for an account."""
    account = db.get_gmail_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    updated = db.update_gmail_account(account_id, {"daily_sent_count": 0})
    return updated


@router.post("/{account_id}/reset-hourly")
async def reset_hourly_count(account_id: str) -> Dict[str, Any]:
    """Reset hourly sent count for an account."""
    account = db.get_gmail_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    updated = db.update_gmail_account(account_id, {"hourly_sent_count": 0})
    return updated