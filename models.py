from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey, UniqueConstraint
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
    permissions = Column(String())

    # 1 to Many relationship: 1 Role have Many User
    users = relationship('User', backref='roles')
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(255), unique=True, nullable=True)
    email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    role_id = Column(Integer, ForeignKey('role.role_id'))

    # 1 to Many relationship: 1 User can make Many Posts
    posts  =relationship('Post', backref='user', lazy='dynamic')
    # 1 to Many relationship: 1 User can make Many Comment
    comments = relationship('Comments', backref='user', lazy='dynamic')
    # 1 to Many relationship: 1 User can rate Many posts
    post_ratings = relationship('PostRating', backref='user', lazy='dynamic')
    # 1 to Many relatioship: 1 User can rate Many comments
    comment_ratings = relationship('CommentRating', backref='user', lazy='dynamic')

class Category(db.Model):
    __tablename__ = 'categories'
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(255))

    # 1 to Many relationship: 1 Category Have Many SubCategory
    subcategories = relationship('SubCategory', backref='category', lazy=True)
class SubCategory(db.Model):
    __tablename__ = 'subcategories'
    sub_category_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.category_id'))

    # 1 to Many relationship: 1 SubCategory Have Many Posts
    posts = relationship('Post', backref='sub_category', lazy=True) 

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

    # 1 to Many relationship: 1 Post has Many Comments
    comments = relationship('Comments', backref='post', lazy='dynamic')
    # 1 to 1 ralationship: 1 Post Have 1 Rating
    rating = relationship('PostRating', back_populates='post', uselist=False)


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

    # 1 to 1 relationship: 1 Rating belongs to 1 Post
    post = relationship('Post', back_populates='rating')
    # 1 to 1 Relationship: 1 Rating belongs to 1 User
    user = relationship('User', back_populates='post_ratings')

    # Ensure each user can rate each post only once
    __table_args__ = (UniqueConstraint('post_id', 'user_id'),)

class CommentRating(db.Model):
    __tablename__ = 'commentratings'
    comment_rating_id = Column(Integer, primary_key=True)
    comment_id = Column(Integer, ForeignKey('comments.comment_id'))
    like = Column(Boolean)
    dislike = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.user_id'))

    comment = relationship('Comments', backref='ratings')
    user = relationship('User', backref='comment_ratings')