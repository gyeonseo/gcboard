import os
from datetime import timedelta

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Flask 기본 설정
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    ENV = os.getenv("FLASK_ENV", "development")

    # 데이터베이스 (SQLite, 확장시 PostgreSQL/MySQL 등)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///community.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 이메일 인증 (Flask-Mail)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # 이메일 인증 토큰 만료 (초 단위, 24시간)
    EMAIL_TOKEN_EXPIRATION = int(os.getenv("EMAIL_TOKEN_EXPIRATION", 60 * 60 * 24))

    # JWT 인증 (토큰 기반 API 접근시, 선택)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_secret_key_for_api")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 60 * 60 * 2))  # 2시간

    # 사용자 역할/권한
    USER_ROLES = ["user", "moderator", "admin"]
    ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "admin@yourdomain.com").split(",")

    # Flask-Login 설정
    REMEMBER_COOKIE_DURATION = int(os.getenv("REMEMBER_COOKIE_DURATION", 60 * 60 * 24 * 7))  # 7일

    # CSRF 방지
    WTF_CSRF_ENABLED = True

    # RESTful API 문서화 (Swagger 등)
    SWAGGER_UI_DOC_EXPANSION = "list"
    RESTX_MASK_SWAGGER = False
    API_TITLE = "Community API"
    API_VERSION = "1.0"

    # 페이징 기본값
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", 20))

    # 게시글/댓글 익명 닉네임 패턴
    ANON_NICKNAME_PREFIX = "익명"

    # 보안 관련
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # 운영 환경에서는 True(HTTPS)
    SESSION_PROTECTION = "strong"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # 관리자 기능 활성화
    ADMIN_ENABLED = True

    # 알림(Notification) 기능
    NOTIFICATION_ENABLED = True
    NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "no-reply@yourdomain.com")

    # 검색/필터
    SEARCH_ENABLED = True

    # 세션 설정
    PERMANENT_SESSION_LIFETIME = timedelta(days=3)

    # 이메일 인증 설정
    EMAIL_VERIFICATION_EXPIRATION = timedelta(hours=12)
    EMAIL_VERIFICATION_URL = os.environ.get('EMAIL_VERIFICATION_URL', 'http://127.0.0.1:5000/verify-email/{}')

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    def __init__(self):
        super().__init__()
        if not os.getenv("SECRET_KEY"):
            raise ValueError("프로덕션 환경에서는 SECRET_KEY를 설정해야 합니다.")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# 환경에 따른 설정 선택
def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
        'default': DevelopmentConfig
    }.get(env, DevelopmentConfig)

# 현재 환경에 맞는 설정 객체 생성
config = get_config()
