from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, MetaData
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from flask_login import UserMixin
from app import db


class Posts(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(255))
    date_posted: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    date_updated: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now(),
                                                             onupdate=func.current_timestamp())
    slug: Mapped[str] = mapped_column(String(255))

    # create string
    def __repr__(self):
        return "<Title %r>" % self.title

class Users(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    favorite_color: Mapped[str] = mapped_column(String(100), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(250), nullable=False)
    date_added: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now())

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create string
    def __repr__(self):
        return "<Name %r>" % self.name

