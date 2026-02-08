from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError

from .database import Base, get_db, engine
from .crud import create_user, authenticate_user, deactivate_user
from .schemas import AuthResponseSchema, RegisterSchema, RefreshTokenSchema, AuthInfo, LoginSchema, TokenResponseSchema
from .sender import send_event
from .jwt import refresh_access_token, get_current_user, required_role, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET, ALGORITHM
from .blacklist import token_to_blacklist


app = FastAPI(
    title='Auth API',
    description='API for Auth management',
    version='0.0.1'
)

@app.on_event('startup')
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        
@app.post(
    '/register',
    response_model=AuthResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Register for new user',
    tags=['Auth', 'Register']
)
async def register(reg_data: RegisterSchema, db: AsyncSession = Depends(get_db)):
    auth, token_pair = await create_user(
        db=db, 
        login=reg_data.login, 
        email=reg_data.email, 
        password=reg_data.password
        )
    
    await send_event({
        'event_type': 'Register',
        'auth_id': auth.id,
        'display_name': reg_data.display_name
    })
    
    return AuthResponseSchema(user=AuthInfo.model_validate(auth), token_pair=token_pair)


@app.post(
    '/login',
    response_model=AuthResponseSchema,
    summary='Login',
    tags=['Auth', 'Login']
)
async def login(login_data: LoginSchema, db: AsyncSession = Depends(get_db)):
    user, token_pair = await authenticate_user(
        db=db, 
        login=login_data.login, 
        password=login_data.password
        )
    
    return AuthResponseSchema(user=AuthInfo.model_validate(user), token_pair=token_pair)


@app.post(
    '/refresh',
    response_model=TokenResponseSchema,
    summary='Refresh atoken pair',
    tags=['Auth']
)
async def refresh_token_pair(data: RefreshTokenSchema, db: AsyncSession = Depends(get_db)):
    try:
        token_pair = await refresh_access_token(db, data.refresh_token)
        return TokenResponseSchema.model_validate(token_pair)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'{str(e)}'
        )
        

@app.post(
    '/account-delete',
    response_model=AuthInfo,
    summary='Deactivate account',
    tags=['Auth']
)
async def account_delete(user: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await send_event({
        'event_type': 'Account Deactivate',
        'auth_id': user.get('id'),
        'is_active': False
    })
    
    return await deactivate_user(db=db, user_id=user.get('id'))



@app.post(
    '/account-delete/{user_id}',
    response_model=AuthInfo,
    summary='Deactivate other user account (Admin abillity)',
    tags=['Auth']
)
async def delete_account_by_id(user_id: int, admin = Depends(required_role('admin')), db: AsyncSession = Depends(get_db)):
    await send_event({
        'event_type': 'Account Deactivate',
        'auth_id': user_id,
        'is_active': False
    })
    
    return await deactivate_user(db=db, user_id=user_id)


#! Логаут я конечно захардкодил, так вышло, что вход я уже делал и все хорошо понимаю, а вот с логаутом первый раз столкнулся
#! В последний момент я еще понял что и рефреш токен тоже в блэклист кидать надо, время поджимает поэтому переписывать не буду

@app.post(
    '/logout',
    status_code=status.HTTP_200_OK,
    summary='Logout',
    tags=['Auth']
)
async def logout(logout_data: RefreshTokenSchema, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    access_jti = user.get('jti')
    access_user_id = user.get('id')
    access_expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    await token_to_blacklist(db=db, jti=access_jti, user_id=access_user_id, expires_at=access_expires_at)
    
    try:
        refresh_payload = jwt.decode(logout_data.refresh_token, SECRET, algorithms=[ALGORITHM])
        refresh_jti = refresh_payload.get('jti')
        refresh_expires = datetime.fromtimestamp(refresh_payload.get('exp'), tz=timezone.utc)
        await token_to_blacklist(db, refresh_jti, user.get('id'), refresh_expires)
    except JWTError:
        pass
    
    return {'message': 'Successful Logout'}