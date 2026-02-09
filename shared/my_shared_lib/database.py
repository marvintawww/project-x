from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

def create_database_connection(database_url: str, echo: bool = True):
    
    engine = create_async_engine(database_url, echo=echo)
    
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    Base = declarative_base()
    
    async def get_db():
        async with AsyncSessionLocal() as session:
            yield session
            
    return engine, AsyncSessionLocal, Base, get_db