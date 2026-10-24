from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = (
    "mssql+pyodbc://@ASUS_VIVOBOOK/Table"
    "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    gmail = Column(String(150))
    age = Column(Integer)

class UserCreate(BaseModel):
    name: str
    gmail: str
    age: int


app = FastAPI(
    title="Мое приложение",
    description="Приложение для работы с базой данных SQL Server",
    docs_url="/docs",
    swagger_ui_parameters={"locale": "ru"}
)


@app.get("/users")
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users

@app.get("/users/{user_id}")
def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    if not user:
        return {"error": "Not found"}
    return user

@app.post("/users")
def create_user(user: UserCreate):
    db = SessionLocal()
    new_user = User(name=user.name, gmail=user.gmail, age=user.age)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return new_user

@app.patch("/users/{user_id}")
def update_user(user_id: int, user: UserCreate):
    db = SessionLocal()
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.name = user.name
        db_user.gmail = user.gmail
        db_user.age = user.age
        db.commit()
        db.refresh(db_user)
    db.close()
    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    db = SessionLocal()
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    db.close()
    return {"message": "Deleted"}
