from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timezone

from .models import TokenBlackList


async def token_to_blacklist(db: AsyncSession, jti: str, user_id: int, expires_at: datetime):
    blacklisted_token = TokenBlackList(jti=jti, user_id=user_id, expires_at=expires_at)
    db.add(blacklisted_token)
    await db.commit()


async def is_token_blacklisted(db: AsyncSession, jti: str) -> bool:
    stmt = select(TokenBlackList).where(TokenBlackList.jti == jti)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def cleanup_blacklist(db: AsyncSession):
    stmt = delete(TokenBlackList).where(TokenBlackList.expires_at < datetime.now(timezone.utc))
    await db.execute(stmt)
    await db.commit()