# tests/conftest.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

import pytest
from backend.app import create_app
from backend.models import db, User, Board
from werkzeug.security import generate_password_hash

@pytest.fixture
def setup_user_and_board(app):
    with app.app_context():
        # 유저 생성
        user = User.query.filter_by(email="test@naver.com").first()
        if not user:
            user = User(
                email="test@naver.com",
                password_hash=generate_password_hash("test1234"),
                nickname="테스터",
                is_authenticated=True  # ✅ 이메일 인증된 상태로 만듦
            )
            db.session.add(user)

        # 게시판 생성
        board = Board.query.first()
        if not board:
            board = Board(name="테스트게시판", description="테스트용")
            db.session.add(board)

        db.session.commit()

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # ✅ 테스트용 인메모리 DB
        "SECRET_KEY": "test-secret",                      # ✅ .env 없이도 실행되게
        "WTF_CSRF_ENABLED": False,
        "EMAIL_TOKEN_EXPIRATION": 3600,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
