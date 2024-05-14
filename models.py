from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()


### DB  MODEL DEFINITION
