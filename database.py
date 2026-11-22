import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, MetaData,
    String, Table, Text, create_engine, event, func, select
)

load_dotenv()
db_path = Path(os.getenv("DATABASE_PATH", str(Path(__file__).parent / "shanyraq.db")))
db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{db_path}")
md = MetaData()
users = Table(
    "users", md,
    Column("user_id", Integer, primary_key=True),
    Column("username", String(100), nullable=False, unique=True),
    Column("phone", String(20), nullable=False),
    Column("hashed_password", String(255), nullable=False),
    Column("name", String(100), nullable=False),
    Column("city", String(100), nullable=False)
)
shanyraks = Table(
    "shanyraks", md,
    Column("shanyrak_id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.user_id"), nullable=False),
    Column("type", String(20), nullable=False),
    Column("price", Integer, nullable=False),
    Column("address", String(255), nullable=False),
    Column("area", Float, nullable=False),
    Column("rooms_count", Integer, nullable=False),
    Column("description", Text, nullable=False)
)
comments = Table(
    "comments", md,
    Column("comment_id", Integer, primary_key=True),
    Column("shanyrak_id", Integer,
           ForeignKey("shanyraks.shanyrak_id", ondelete="CASCADE"), nullable=False),
    Column("author_id", Integer, ForeignKey("users.user_id"), nullable=False),
    Column("content", Text, nullable=False),
    Column("created_at", DateTime, nullable=False,
           server_default=func.current_timestamp())
)
def initialize_db():
    with engine.begin() as conn:
        md.create_all(conn)


def register_user(username: str, phone: str, hashed_password: str,
                  name: str, city: str):
    with engine.begin() as conn:
        result = conn.execute(users.insert().values(
            username=username, phone=phone, hashed_password=hashed_password,
            name=name, city=city
        ))
    return result.inserted_primary_key[0]

def get_user(username: str):
    with engine.connect() as conn:
        return conn.execute(select(users).where(users.c.username == username)).first()

def get_user_by_id(user_id: int):
    with engine.connect() as conn:
        return conn.execute(select(users).where(users.c.user_id == user_id)).first()

def update_user(user_id: int, changes: dict):
    with engine.begin() as conn:
        conn.execute(users.update().where(users.c.user_id == user_id).values(**changes))
    return get_user_by_id(user_id)

def create_shanyrak(user_id: int, data: dict):
    with engine.begin() as conn:
        result = conn.execute(shanyraks.insert().values(user_id=user_id, **data))
    return result.inserted_primary_key[0]

def get_shanyrak(shanyrak_id: int):
    query = (
        select(shanyraks, func.count(comments.c.comment_id).label("total_comments"))
        .outerjoin(comments, comments.c.shanyrak_id == shanyraks.c.shanyrak_id)
        .where(shanyraks.c.shanyrak_id == shanyrak_id)
        .group_by(shanyraks.c.shanyrak_id)
    )
    with engine.connect() as conn:
        row = conn.execute(query).first()
        return dict(row._mapping) if row else None

def get_all_shanyraks():
    with engine.connect() as conn:
        rows = conn.execute(select(shanyraks).order_by(shanyraks.c.shanyrak_id.desc()))
        return [dict(row._mapping) for row in rows]

def update_shanyrak(shanyrak_id: int, changes: dict):
    with engine.begin() as conn:
        conn.execute(shanyraks.update().where(
            shanyraks.c.shanyrak_id == shanyrak_id
        ).values(**changes))
    return get_shanyrak(shanyrak_id)


def delete_shanyrak(shanyrak_id: int):
    with engine.begin() as conn:
        conn.execute(
            comments.delete().where(comments.c.shanyrak_id == shanyrak_id)
        )
        result = conn.execute(
            shanyraks.delete().where(shanyraks.c.shanyrak_id == shanyrak_id)
        )
    return result.rowcount > 0


def create_comment(shanyrak_id: int, author_id: int, content: str):
    with engine.begin() as conn:
        result = conn.execute(comments.insert().values(
            shanyrak_id=shanyrak_id, author_id=author_id, content=content
        ))
    return result.inserted_primary_key[0]

def get_comments(shanyrak_id: int):
    with engine.connect() as conn:
        rows = conn.execute(
            select(comments.c.comment_id.label("id"), comments.c.content,
                   comments.c.created_at, comments.c.author_id)
            .where(comments.c.shanyrak_id == shanyrak_id)
            .order_by(comments.c.comment_id)
        )
        return [dict(row._mapping) for row in rows]

def get_comment(shanyrak_id: int, comment_id: int):
    with engine.connect() as conn:
        row = conn.execute(select(comments).where(
            (comments.c.comment_id == comment_id) &
            (comments.c.shanyrak_id == shanyrak_id)
        )).first()
        return dict(row._mapping) if row else None

def update_comment(shanyrak_id: int, comment_id: int, content: str):
    with engine.begin() as conn:
        conn.execute(comments.update().where(
            (comments.c.comment_id == comment_id) &
            (comments.c.shanyrak_id == shanyrak_id)
        ).values(content=content))
    return get_comment(shanyrak_id, comment_id)

def delete_comment(shanyrak_id: int, comment_id: int):
    with engine.begin() as conn:
        result = conn.execute(comments.delete().where(
            (comments.c.comment_id == comment_id) &
            (comments.c.shanyrak_id == shanyrak_id)
        ))
    return result.rowcount > 0
