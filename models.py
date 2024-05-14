from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin, AsaList

db = SQLAlchemy()


### DB  MODEL DEFINITION
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    role_id = Column(Integer,primary_key=True)
    role_name = Column(String(64), unique=True)
    permissons = Column(String())

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(255), unique=True, nullable=True)
    email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    roles = relationship('Role', backref='user', lazy='dynamic')

class Category(db.Model):
    __tablename__ = 'categories'
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(255))
    subcategories = relationship('SubCategory', backref='category', lazy=True)

class SubCategory(db.Model):
    __tablename__ = 'subcategories'
    sub_category_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.category_id'))

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

    user = relationship('User', backref='posts')
class Comments(db.Model):
    __tablename__ = 'comments'
    comment_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    comment_text = Column(String(255))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())

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

    post = relationship('Post', backref='attachments')

class PostRating(db.Model):
    __tablename__ = 'postratings'
    post_rating_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    like = Column(Boolean)
    dislike = Column(Boolean)

    post = relationship('Post', backref='ratings')
    user = relationship('User', backref='post_ratings')

class CommentRating(db.Model):
    __tablename__ = 'commentratings'
    comment_rating_id = Column(Integer, primary_key=True)
    comment_id = Column(Integer, ForeignKey('comments.comment_id'))
    like = Column(Boolean)
    dislike = Column(Boolean)

    comment = relationship('Comment', backref='ratings')
    user = relationship('User', backref='comment_ratings')