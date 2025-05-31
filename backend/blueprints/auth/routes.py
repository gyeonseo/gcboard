from flask import Blueprint, request, jsonify, session, redirect, url_for, current_app
from models import db, User, EmailVerification
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from flask_mail import Message
from datetime import datetime, timedelta
import uuid

auth_bp = Blueprint('auth', __name__)

# 회원가입
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    nickname = data.get('nickname', None)

    # 이메일 형식 검증
    try:
        validate_email(email)
    except EmailNotValidError:
        return jsonify({'result': 'fail', 'reason': 'Invalid email format'}), 400

    # 중복 체크
    if User.query.filter_by(email=email).first():
        return jsonify({'result': 'fail', 'reason': 'Email already exists'}), 409

    # 회원 생성
    password_hash = generate_password_hash(password)
    user = User(email=email, password_hash=password_hash, nickname=nickname)
    db.session.add(user)
    db.session.commit()

    # 이메일 인증 토큰 생성
    token = str(uuid.uuid4())
    expiration_time = datetime.utcnow() + timedelta(seconds=current_app.config['EMAIL_TOKEN_EXPIRATION'])
    verification = EmailVerification(user_id=user.user_id, token=token, expiration_time=expiration_time)
    db.session.add(verification)
    db.session.commit()

    # 인증 메일 발송
    mail = current_app.extensions['mail']
    msg = Message(subject='이메일 인증', recipients=[email])
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    msg.body = f"아래 링크를 클릭해 이메일 인증을 완료하세요: {verify_url}"
    mail.send(msg)

    return jsonify({'result': 'success', 'message': '회원가입 완료. 이메일 인증을 해주세요.'})

# 로그인
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'result': 'fail', 'reason': 'No such user'}), 404
    if not check_password_hash(user.password_hash, password):
        return jsonify({'result': 'fail', 'reason': 'Wrong password'}), 401
    if not user.is_authenticated:
        return jsonify({'result': 'fail', 'reason': 'Email not verified'}), 403
    if user.is_banned:
        return jsonify({'result': 'fail', 'reason': 'User banned'}), 403
    login_user(user)
    return jsonify({'result': 'success', 'user_id': user.user_id, 'nickname': user.nickname})

# 로그아웃
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'result': 'success'})

# 이메일 인증
@auth_bp.route('/verify-email', methods=['GET'])
def verify_email():
    token = request.args.get('token')
    verification = EmailVerification.query.filter_by(token=token).first()
    if not verification:
        return jsonify({'result': 'fail', 'reason': 'Invalid token'}), 404
    if verification.is_verified:
        return jsonify({'result': 'fail', 'reason': 'Already verified'}), 400
    if verification.expiration_time < datetime.utcnow():
        return jsonify({'result': 'fail', 'reason': 'Token expired'}), 400
    verification.is_verified = True
    user = User.query.get(verification.user_id)
    user.is_authenticated = True
    db.session.commit()
    return jsonify({'result': 'success', 'message': '이메일 인증 완료. 로그인하세요.'})

# 사용자 프로필 조회/수정
@auth_bp.route('/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    user = current_user
    if request.method == 'GET':
        return jsonify({
            'user_id': user.user_id,
            'email': user.email,
            'nickname': user.nickname,
            'role': user.role,
            'created_at': user.created_at
        })
    else:
        data = request.get_json()
        user.nickname = data.get('nickname', user.nickname)
        db.session.commit()
        return jsonify({'result': 'success', 'nickname': user.nickname})
