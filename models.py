from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
import uuid
import datetime

db = SQLAlchemy()

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey(
                           'users.user_id'), primary_key=True),
                       db.Column('role_id', db.Integer, db.ForeignKey(
                           'role.id'), primary_key=True)
                       )


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    permissions = Column(String())


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(255), unique=True, nullable=True)
    email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    created_at = Column(DateTime())
    fs_uniquifier = Column(String(255), unique=True,
                           nullable=False, default=lambda: str(uuid.uuid4()))
    active = Column(Boolean, default=True)

    roles = relationship('Role', secondary=roles_users,
                         backref=backref('users', lazy='dynamic'))
    created_posts = relationship('Post', back_populates='user')
    created_comments = relationship('Comments', back_populates='user')
    post_ratings = relationship('PostRating', back_populates='user')
    comment_ratings = relationship('CommentRating', back_populates='user')


class Category(db.Model):
    __tablename__ = 'categories'
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(255))

    subcategories = relationship('SubCategory', back_populates='category')


class SubCategory(db.Model):
    __tablename__ = 'subcategories'
    sub_category_id = Column(Integer, primary_key=True)
    sub_category_name = Column(String(255))
    category_id = Column(Integer, ForeignKey('categories.category_id'))

    category = relationship('Category', back_populates='subcategories')
    related_posts = relationship('Post', back_populates='sub_category')


class Post(db.Model):
    __tablename__ = 'posts'
    post_id = Column(Integer, primary_key=True)
    post_title = Column(String(255))
    post_body = Column(String(255))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    sub_cat_id = Column(Integer, ForeignKey('subcategories.sub_category_id'))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    visibility = Column(String)

    user = relationship('User', back_populates='created_posts')
    sub_category = relationship('SubCategory', back_populates='related_posts')
    related_comments = relationship('Comments', back_populates='related_post')
    post_rating = relationship(
        'PostRating', back_populates='rated_post', uselist=False)
    files_attached = relationship(
        'FileAttachment', back_populates='attached_post')


class Comments(db.Model):
    __tablename__ = 'comments'
    comment_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    parent_comment_id = Column(Integer, ForeignKey('comments.comment_id'), nullable=True)
    comment_text = Column(String(255))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())

    user = relationship('User', back_populates='created_comments')
    related_post = relationship('Post', back_populates='related_comments')
    comment_rating = relationship('CommentRating', back_populates='rated_comments', uselist=False)
    parent_comment = relationship('Comments', remote_side=[comment_id], backref='child_comments')


class Tags(db.Model):
    __tablename__ = 'tags'
    tag_id = Column(Integer, primary_key=True)
    tag_name = Column(String(255))


class FileAttachment(db.Model):
    __tablename__ = 'fileattachments'
    file_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    file_name = Column(String(255))
    file_url = Column(String(255))
    file_type = Column(String(50))

    # 1 to Many relationship: 1 Post can have many Files attached to it
    attached_post = relationship('Post', back_populates='files_attached')

class PostRating(db.Model):
    __tablename__ = 'postratings'
    post_rating_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    like = Column(Boolean)
    dislike = Column(Boolean)

    rated_post = relationship(
        'Post', back_populates='post_rating', uselist=False)
    user = relationship('User', back_populates='post_ratings')

    __table_args__ = (UniqueConstraint('post_id', 'user_id'),)


class CommentRating(db.Model):
    __tablename__ = 'commentratings'
    comment_rating_id = Column(Integer, primary_key=True)
    comment_id = Column(Integer, ForeignKey('comments.comment_id'))
    like = Column(Boolean)
    dislike = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    rated_comments = relationship(
        'Comments', back_populates='comment_rating', uselist=False)
    user = relationship('User', back_populates='comment_ratings')

    __table_args__ = (UniqueConstraint('comment_id', 'user_id'),)
