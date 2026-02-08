from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)

def check_hash(pw: str, hash_pw: str) -> bool:
    return pwd_context.verify(pw, hash_pw)
