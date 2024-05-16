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
    users = relationship('User', back_populates='roles')

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(255), unique=True, nullable=True)
    email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    role_id = Column(Integer, ForeignKey('role.role_id'))

    # 1 to Many relationship: 1 Role have Many User
    roles = relationship('Role', back_populates='users')
    # 1 to Many relationship: 1 User can make Many Posts
    created_posts  = relationship('Post', back_populates='user')
    # 1 to Many relationship: 1 User can make Many Comment
    created_comments = relationship('Comments', back_populates='user')
    # 1 to Many relationship: 1 User can rate Many posts
    post_ratings = relationship('PostRating', back_populates='user')
    # 1 to Many relatioship: 1 User can rate Many comments
    comment_ratings = relationship('CommentRating', back_populates='user')

class Category(db.Model):
    __tablename__ = 'categories'
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(255))

    # 1 to Many relationship: 1 Category Have Many SubCategory
    subcategories = relationship('SubCategory', back_populates='category')

class SubCategory(db.Model):
    __tablename__ = 'subcategories'
    sub_category_id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.category_id'))

    # 1 to Many relationship: 1 Category Have Many SubCategory
    category = relationship('Category', back_populates='subcategories')
    # 1 to Many relationship: 1 SubCategory Have Many Posts
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

    # 1 to Many relationship: 1 User can make Many Posts
    user = relationship('User', back_populates='created_posts')
    # 1 to Many relationship: 1 SubCategory Have Many Posts
    sub_category = relationship('SubCategory', back_populates='related_posts') 
    # 1 to Many relationship: 1 Post has Many Comments
    related_comments = relationship('Comments', back_populates='related_post')
    # 1 to 1 relationship: 1 Post Have 1 Rating
    post_rating = relationship('PostRating', back_populates='rated_post', uselist=False)
    # 1 to Many relationship: 1 Post can have many Files attached to it
    files_attached = relationship('FileAttachment', back_populates='attached_post')


class Comments(db.Model):
    __tablename__ = 'comments'
    comment_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    # Column for self-referential relationship (comments can be made to comments)
    parent_comment_id = Column(Integer, ForeignKey('comments.comment_id'))
    comment_text = Column(String(255))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())

    # 1 to Many relationship: 1 User can make Many Comment
    user = relationship('User', back_populates='created_comments')
    # 1 to Many relationship: 1 Post has Many Comments
    related_post = relationship('Post', back_populates='related_comments')
    # 1 to 1 relationship: 1 Comment have 1 Rating
    comment_rating = relationship('CommentRating', back_populates='rated_comments', uselist=False)
    # Self-referential relationship for nested comments
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

    # 1 to Many relationship: 1 Post can have many Files attached to it
    attached_post = relationship('Post', back_populates='files_attached')


class PostRating(db.Model):
    __tablename__ = 'postratings'
    post_rating_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    like = Column(Boolean)
    dislike = Column(Boolean)

    # 1 to 1 relationship: 1 Post have 1 Rating
    rated_post = relationship('Post', back_populates='post_rating', uselist=False)
    # 1 to Many relationship: 1 User can rate Many posts
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

    # 1 to 1 relationship: 1 Comment have 1 Rating
    rated_comments = relationship('Comments', back_populates='comment_rating', uselist=False)
    # 1 to Many relatioship: 1 User can rate Many comments
    user = relationship('User', back_populates='comment_ratings')
    
    # Ensure each user can rate each post only once
    __table_args__ = (UniqueConstraint('comment_id', 'user_id'),)