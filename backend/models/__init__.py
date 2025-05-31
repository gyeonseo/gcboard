from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User, EmailVerification, Notification
from .board import Board
from .post import Post
from .comment import Comment
from .like import Like
