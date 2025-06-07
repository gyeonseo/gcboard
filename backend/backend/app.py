import os
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from backend.models import db, User, Board
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    app.config.from_object('backend.config.Config')

    # ORM, 마이그레이션, 메일, CORS 초기화
    db.init_app(app)
    migrate = Migrate(app, db)
    mail = Mail(app)
    CORS(app, origins=app.config.get("CORS_ORIGINS", "*"))

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # 초기 데이터 생성 커맨드
    @app.cli.command("init-defaults")
    def init_defaults():
        """기본 게시판과 관리자 계정 생성"""
        with app.app_context():
            # DB 초기화
            db.drop_all()
            db.create_all()

            # 탈퇴한 사용자 계정 생성
            if not Board.query.first():
                boards = [
                    Board(name="자유게시판", description="자유롭게 이야기하는 공간"),
                    Board(name="비밀게시판", description="익명으로 소통하는 공간"),
                    Board(name="정보게시판", description="정보 공유 게시판"),
                    Board(name="이벤트게시판", description="이벤트 및 공지"),
                ]
                db.session.add_all(boards)
                print("기본 게시판 생성 완료")

            # 관리자 계정 생성
            if not User.query.filter_by(role="admin").first():
                admin = User(
                    email="admin@example.com",
                    password_hash=generate_password_hash("admin1234"),
                    nickname="관리자",
                    is_authenticated=True,
                    role="admin"
                )
                unk = User(
                    email="unknown@example.com",
                    password_hash=generate_password_hash("unknown1234"),
                    nickname="(탈퇴한 사용자)",
                    is_authenticated=True,
                    role="admin"
                )
                db.session.add(admin)
                db.session.add(unk)
                print("초기 관리자 계정 생성 완료")
                
            db.session.commit()
            print("초기 데이터 삽입 완료")

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # API 블루프린트 등록
    from backend.blueprints.auth.routes import auth_bp
    from backend.blueprints.board.routes import board_bp
    from backend.blueprints.comment.routes import comment_bp
    from backend.blueprints.like.routes import like_bp
    from backend.blueprints.community.routes import community_bp
    from backend.blueprints.admin.routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(board_bp, url_prefix='/api/board')
    app.register_blueprint(comment_bp, url_prefix='/api/comment')
    app.register_blueprint(like_bp, url_prefix='/api/like')
    app.register_blueprint(community_bp, url_prefix='/api/community')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # 웹 페이지 블루프린트 등록
    from backend.blueprints.web.routes import web_bp
    app.register_blueprint(web_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
