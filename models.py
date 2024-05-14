from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()


### DB  MODEL DEFINITION
class Roles(db.Model):
    __tablename__ = 'roles'
    roleid = Column(Integer,primary_key=True)
    rolename = Column(String(64), unique=True)  

class User(db.Model):
    __tablename__ = 'user'
    userid = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=True)
    email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    
class Category(db.Model):
    __tablename__ = 'category'
    catid = Column()
    catname = Column()

class SubCategory(db.Model):
    __tablename__ = 'subcategory'
    subcatid = Column()
    catid = db.Column(db.Integer, db.ForeingKey('category.id', name='fk_subcategory_category_catid'))

class Post(db.Model):
    __tablename__ = 'post'
    postid = Column()
    posttitle = Column()
    postbody = Column()
    userid = db.Column()
    subcatid = db.Column()
    created_at = Column(DateTime())
    updated_at = Column(DateTime())
    visibility = Column()

class Comments(db.Model):
    __tablename__ = 'comments'
    commentid = Column()
    postid = db.Column()
    userid = db.column()
    cmttext = Column()
    created_at = Column(DateTime())
    updated_at = Column(DateTime())

class Tags(db.Model):
    __tablename__ = 'tags'
    tagid = Column()
    tagname = Column()

class FileAttachment(db.Model):
    __tablename__ = 'fileattachment'
    fileid = Column()
    postid = db.Column()
    filename = Column()
    file_url = Column()

class PostRating(db.Model):
    __tablename__ = 'postrating'
    prid = Column()
    postid = db.Column()
    userID = db.Column()
    like = Column()
    dislike = Column()

class CommentRating(db.Model):
    __tablename__ = 'commentrating'
    crid = Column()
    commentid = db.Model()
    like = Column()
    dislike = Column()