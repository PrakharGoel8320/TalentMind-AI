"""Recruitment session persistence for agent context memory."""
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.recruitment_session import RecruitmentSession


async def get_or_create_session(
    db: AsyncSession,
    job_id: str,
    session_id: Optional[str] = None,
) -> RecruitmentSession:
    if session_id:
        try:
            sid = uuid.UUID(session_id)
        except ValueError:
            sid = None
        if sid:
            result = await db.execute(select(RecruitmentSession).filter(RecruitmentSession.id == sid))
            existing = result.scalars().first()
            if existing:
                return existing

    result = await db.execute(
        select(RecruitmentSession)
        .filter(RecruitmentSession.job_id == uuid.UUID(job_id))
        .order_by(RecruitmentSession.updated_at.desc())
    )
    latest = result.scalars().first()
    if latest:
        return latest

    session = RecruitmentSession(
        job_id=uuid.UUID(job_id),
        state_json={},
        events_json=[],
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def save_session_state(
    db: AsyncSession,
    session: RecruitmentSession,
    state_updates: Dict[str, Any],
    new_events: Optional[List[Dict[str, Any]]] = None,
) -> RecruitmentSession:
    current_state = dict(session.state_json or {})
    current_state.update(state_updates)
    session.state_json = current_state

    if new_events:
        events = list(session.events_json or [])
        events.extend(new_events)
        session.events_json = events

    await db.commit()
    await db.refresh(session)
    return session
