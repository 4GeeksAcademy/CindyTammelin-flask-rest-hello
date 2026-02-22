from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    profile_pic: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow)

    posts = relationship('Post', back_populates='user',
                         cascade='all, delete-orphan')
    comments = relationship(
        'Comment', back_populates='user', cascade='all, delete-orphan')
    likes = relationship('Like', back_populates='user',
                         cascade='all, delete-orphan')
    followers = relationship('Follow', foreign_keys='Follow.followed_id',
                             back_populates='followed', cascade='all, delete-orphan')
    following = relationship('Follow', foreign_keys='Follow.follower_id',
                             back_populates='follower', cascade='all, delete-orphan')


def serialize(self):
    return {
        "id": self.id,
        "username": self.username,
        "email": self.email,
        # do not serialize the password, its a security breach
        "full_name": self.full_name,
        "bio": self.bio,
        "profile_pic": self.profile_pic,
        "is_active": self.is_active,
        "created_at": self.created_at.isoformat() if self.created_at else None,
        "posts_count": len(self.posts) if self.posts else 0,
        "followers_count": len(self.followers) if self.followers else 0,
        "following_count": len(self.following) if self.following else 0
    }


class Post(db.Model):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    caption: Mapped[str] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow)

    user = relationship('User', back_populates='posts')
    comments = relationship(
        'Comment', back_populates='post', cascade='all, delete-orphan')
    likes = relationship('Like', back_populates='post',
                         cascade='all, delete-orphan')

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "image_url": self.image_url,
            "caption": self.caption,
            "location": self.location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "comments_count": len(self.comments) if self.comments else 0,
            "likes_count": len(self.likes) if self.likes else 0
        }


class Comment(db.Model):
    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow)

    user = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "post_id": self.post_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Like(db.Model):
    __tablename__ = 'like'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow)

    user = relationship('User', back_populates='likes')
    post = relationship('Post', back_populates='likes')

    __table_args__ = (db.UniqueConstraint(
        'user_id', 'post_id', name='unique_user_post_like'),)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "post_id": self.post_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Follow(db.Model):
    __tablename__ = 'follow'

    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey(
        'user.id'), nullable=False)  # The user who follows
    followed_id: Mapped[int] = mapped_column(ForeignKey(
        'user.id'), nullable=False)  # The user being followed
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow)

    follower = relationship('User', foreign_keys=[
                            follower_id], back_populates='following')
    followed = relationship('User', foreign_keys=[
                            followed_id], back_populates='followers')

    __table_args__ = (db.UniqueConstraint(
        'follower_id', 'followed_id', name='unique_follower_followed'),)

    def serialize(self):
        return {
            "id": self.id,
            "follower_id": self.follower_id,
            "follower_username": self.follower.username if self.follower else None,
            "followed_id": self.followed_id,
            "followed_username": self.followed.username if self.followed else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
