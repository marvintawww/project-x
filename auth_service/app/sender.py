import aio_pika
import json
import os

async def get_rabbit_connection():
    rabbit_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    return await aio_pika.connect_robust(f'amqp://guest:guest@{rabbit_host}')


async def send_event(event_data: dict):
    connection = await get_rabbit_connection() # Создаем соединение 
    
    async with connection:
        channel = await connection.channel() # Создаем канал
        
        msg_body = json.dumps(event_data).encode() # Превращаем Python объект в JSON
        
        await channel.default_exchange.publish( 
            aio_pika.Message(body=msg_body),        # Ну и тут отправляем в очередь 'user_info'
            routing_key='user_info'
        )