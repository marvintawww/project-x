import aio_pika
import json
import asyncio
import os
from sqlalchemy import select

from .database import AsyncSessionLocal, engine, Base
from .models import User
from .schemas import EventData

async def message_proccess(message: aio_pika.IncomingMessage):
    async with message.process():
        data = json.loads(message.body.decode())
        event = EventData(**data)
    
    async with AsyncSessionLocal() as db:
        if event.event_type == 'Register':
            user = User(
                id=event.auth_id,
                display_name=event.display_name
                )    
            
            db.add(user)
            
        elif event.event_type == 'Account Deactivate':
            stmt = select(User).where(User.id == event.auth_id)
            user = (await db.execute(stmt)).scalar_one_or_none()
            
            if user:
                user.is_active = False
                
        await db.commit()


async def start_consumer():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    connection = await aio_pika.connect_robust(f"amqp://guest:guest@{rabbitmq_host}/")
    
    async with connection:
        channel = await connection.channel()
        
        queue = await channel.declare_queue("user_info", durable=True)
        
        await queue.consume(message_proccess)
        
        await asyncio.Future()
        
