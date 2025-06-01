# tests/test_auth.py

from unittest.mock import MagicMock
from backend.models import User, EmailVerification
from flask import url_for


def test_register_user(client, app):
    with app.app_context():
        mail = app.extensions['mail']
        mail.send = MagicMock()  # 이메일 발송 mock 처리

    payload = {
        "email": "test@naver.com",
        "password": "test1234",
        "nickname": "testuser"
    }
    res = client.post('/api/auth/register', json=payload)

    print("\n[REGISTER USER TEST]")
    print("Request JSON:", payload)
    print("Response Status:", res.status_code)
    print("Response JSON:", res.get_json())

    assert res.status_code == 200


def test_full_auth_flow(client, app):
    with app.app_context():
        mail = app.extensions['mail']
        mail.send = MagicMock()

    # 1. 회원가입
    payload_register = {
        "email": "test@naver.com",
        "password": "test1234",
        "nickname": "testuser"
    }
    res = client.post('/api/auth/register', json=payload_register)

    print("\n[AUTH FLOW - 1. REGISTER]")
    print("Request JSON:", payload_register)
    print("Response Status:", res.status_code)
    print("Response JSON:", res.get_json())
    assert res.status_code == 200

    # 2. 이메일 인증 토큰 추출
    with app.app_context():
        user = User.query.filter_by(email="test@naver.com").first()
        verification = EmailVerification.query.filter_by(user_id=user.user_id).first()
        token = verification.token

    # 3. 이메일 인증
    res_verify = client.get(f'/api/auth/verify-email?token={token}')
    print("\n[AUTH FLOW - 2. VERIFY EMAIL]")
    print("Request URL:", f"/api/auth/verify-email?token={token}")
    print("Response Status:", res_verify.status_code)
    print("Response JSON:", res_verify.get_json())
    assert res_verify.status_code == 200

    # 4. 로그인
    payload_login = {
        "email": "test@naver.com",
        "password": "test1234"
    }
    res_login = client.post('/api/auth/login', json=payload_login)

    print("\n[AUTH FLOW - 3. LOGIN]")
    print("Request JSON:", payload_login)
    print("Response Status:", res_login.status_code)
    print("Response JSON:", res_login.get_json())

    assert res_login.status_code == 200
    data = res_login.get_json()
    assert data['result'] == 'success'
    assert 'user_id' in data
