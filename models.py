from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin, AsaList

db = SQLAlchemy()


### DB  MODEL DEFINITION
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    roleid = Column(Integer,primary_key=True)
    rolename = Column(String(64), unique=True)
    permissons = Column(String())

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    userid = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=True)
    email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    roles = relationship('Role', backref='user', lazy='dynamic')

class Category(db.Model):
    __tablename__ = 'categories'
    catid = Column(Integer, primary_key=True)
    catname = Column(String(255))
    subcategories = relationship('SubCategory', backref='category', lazy=True)

class SubCategory(db.Model):
    __tablename__ = 'subcategories'
    subcatid = Column(Integer, primary_key=True)
    catid = Column(Integer, ForeignKey('categories.catid'))

class Post(db.Model):
    __tablename__ = 'posts'
    postid = Column(Integer, primary_key=True)
    posttitle = Column(String(255))
    postbody = Column(String(255))
    userid = Column(Integer, ForeignKey('users.userid'))
    subcatid = Column(Integer, ForeignKey('subcategories.subcatid'))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    visibility = Column(String)

    user = relationship('User', backref='posts')
class Comments(db.Model):
    __tablename__ = 'comments'
    commentid = Column(Integer, primary_key=True)
    postid = Column(Integer, ForeignKey('posts.postid'))
    userid = Column(Integer, ForeignKey('users.userid'))
    cmttext = Column(String(255))
    created_at = Column(DateTime())
    updated_at = Column(DateTime())

class Tags(db.Model):
    __tablename__ = 'tags'
    tagid = Column(Integer, primary_key=True)
    tagname = Column(String(255))

class FileAttachment(db.Model):
    __tablename__ = 'fileattachments'
    fileid = Column(Integer, primary_key=True)
    postid = Column(Integer, ForeignKey('posts.postid'))
    filename = Column(String(255))
    file_url = Column(String(255))

    post = relationship('Post', backref='attachments')

class PostRating(db.Model):
    __tablename__ = 'postratings'
    prid = Column(Integer, primary_key=True)
    postid = Column(Integer, ForeignKey('posts.postid'))
    userID = Column(Integer, ForeignKey('users.userid'))
    like = Column(Boolean)
    dislike = Column(Boolean)

    post = relationship('Post', backref='ratings')
    user = relationship('User', backref='post_ratings')

class CommentRating(db.Model):
    __tablename__ = 'commentratings'
    crid = Column(Integer, primary_key=True)
    commentid = Column(Integer, ForeignKey('comments.commentid'))
    like = Column(Boolean)
    dislike = Column(Boolean)

    comment = relationship('Comment', backref='ratings')
    user = relationship('User', backref='comment_ratings')