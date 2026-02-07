from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from .database import Base, get_db, engine
from .crud import create_user, authenticate_user, deactivate_user, get_user_by_id
from .schemas import AuthResponseSchema, RegisterSchema, RefreshTokenSchema, AuthInfo, LoginSchema, TokenResponseSchema
from .sender import send_event
from .jwt import refresh_access_token, get_current_user, required_role


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
    
    send_event({
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
async def refresh_token_pair(data: RefreshTokenSchema):
    try:
        token_pair = refresh_access_token(refresh_token=data.refresh_token)
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
    send_event({
        'event_type': 'Account Deactivate',
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
    send_event({
        'event_type': 'Account Deactivate',
        'user_id': user_id,
        'is_active': False
    })
    
    return await deactivate_user(db=db, user_id=user_id)