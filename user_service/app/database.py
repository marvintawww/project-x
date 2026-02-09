from my_shared_lib.database import create_database_connection

DATABASE_URL = 'sqlite+aiosqlite:///./user-service.db'

engine, AsyncSessionLocal, Base, get_db = create_database_connection(DATABASE_URL)