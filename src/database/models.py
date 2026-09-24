import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime,Table, ForeignKey, func
from src.database.db import Base
from sqlalchemy.orm import relationship

class Role(enum.Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    role = Column(Enum(Role), default=Role.user)
    is_active = Column(Boolean, default=True) 
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

photo_m2m_tag = Table(
    'photo_m2m_tag',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('photo_id', Integer, ForeignKey('photos.id', ondelete="CASCADE")),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE")),
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)  
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", backref="photos")
    
    tags = relationship("Tag", secondary=photo_m2m_tag, backref="photos", lazy="selectin")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    photo_id = Column(Integer, ForeignKey("photos.id", ondelete="CASCADE"))
    user = relationship("User", backref="comments")
    photo = relationship("Photo", backref="comments")