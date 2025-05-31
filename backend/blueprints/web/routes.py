from flask import Blueprint, render_template, redirect, url_for, flash, request
from backend.models import Board, Post, User, db, EmailVerification, Comment
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from backend.utils.email import send_verification_email
import datetime
import secrets

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    boards = Board.query.all()
    # 최신 게시물 10개
    latest_posts = Post.query.order_by(desc(Post.created_at)).limit(10).all()
    # 추천 수가 많은 게시물 10개
    popular_posts = Post.query.order_by(desc(Post.like_count), desc(Post.created_at)).limit(10).all()
    return render_template('index.html', boards=boards, latest_posts=latest_posts, popular_posts=popular_posts)

@web_bp.route('/board/<int:board_id>')
def board_detail(board_id):
    board = Board.query.get_or_404(board_id)
    posts = Post.query.filter_by(board_id=board_id).order_by(desc(Post.created_at)).limit(20).all()
    return render_template('board_detail.html', board=board, posts=posts)

@web_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    # 익명 댓글 번호 매핑
    anon_map = {}
    anon_counter = 1
    for c in comments:
        if c.is_anonymous:
            if c.user_id not in anon_map:
                anon_map[c.user_id] = anon_counter
                anon_counter += 1
            c.anon_number = anon_map[c.user_id]
        else:
            c.anon_number = None
    return render_template('post_detail.html', post=post, comments=comments)

@web_bp.route('/write/<int:board_id>', methods=['GET', 'POST'])
@login_required
def write_post(board_id):
    board = Board.query.get_or_404(board_id)
    post_id = request.args.get('post_id', type=int)
    post = None
    
    if post_id:
        post = Post.query.get_or_404(post_id)
        if post.user_id != current_user.user_id and current_user.role != 'admin':
            flash('수정 권한이 없습니다.')
            return redirect(url_for('web.post_detail', post_id=post_id))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_anonym = request.form.get('is_anonym') == '1'
        
        if not (title and content):
            flash('제목과 내용을 모두 입력해주세요.')
            return render_template('write_post.html', board=board, post=post)
        
        if post:  # 수정
            post.title = title
            post.content = content
            post.is_anonymous = is_anonym
            if is_anonym and not post.anonymous_index:
                max_idx = db.session.query(db.func.max(Post.anonymous_index)).filter_by(board_id=board_id).scalar() or 0
                post.anonymous_index = max_idx + 1
            db.session.commit()
            flash('글이 수정되었습니다.')
        else:  # 새 글 작성
            # 익명 인덱스 할당
            if is_anonym:
                max_idx = db.session.query(db.func.max(Post.anonymous_index)).filter_by(board_id=board_id).scalar() or 0
                anonymous_index = max_idx + 1
            else:
                anonymous_index = None
                
            post = Post(
                title=title,
                content=content,
                is_anonymous=is_anonym,
                anonymous_index=anonymous_index,
                user_id=current_user.user_id,
                board_id=board_id
            )
            db.session.add(post)
            db.session.commit()
            flash('글이 작성되었습니다.')
        
        return redirect(url_for('web.post_detail', post_id=post.post_id))
    
    return render_template('write_post.html', board=board, post=post)

# 인증 관련 라우트
@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.is_banned:
                flash('정지된 사용자입니다. 관리자에게 문의하세요.')
                return render_template('login.html')
            if not user.is_authenticated:
                flash('이메일 인증이 필요합니다. 이메일을 확인해주세요.')
                return render_template('login.html')
            login_user(user)
            flash('로그인되었습니다.')
            return redirect(url_for('web.index'))
        else:
            flash('이메일 또는 비밀번호가 올바르지 않습니다.')
    
    return render_template('login.html')

@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('web.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        nickname = request.form.get('nickname')
        
        if User.query.filter_by(email=email).first():
            flash('이미 등록된 이메일입니다.')
            return render_template('register.html')
        
        # 이메일 인증 토큰 생성
        token = secrets.token_urlsafe(32)
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        
        # 임시 사용자 생성 (인증 전까지는 is_authenticated=False)
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            nickname=nickname,
            is_authenticated=False
        )
        db.session.add(user)
        db.session.flush()  # user_id 생성
        
        # 이메일 인증 정보 저장
        verification = EmailVerification(
            user_id=user.user_id,
            token=token,
            expiration_time=expiration_time
        )
        db.session.add(verification)
        db.session.commit()
        
        # 이메일 발송
        send_verification_email(email, token)
        
        flash('회원가입이 완료되었습니다. 이메일을 확인하여 인증을 완료해주세요.')
        return redirect(url_for('web.login'))
    
    return render_template('register.html')

@web_bp.route('/verify-email/<token>')
def verify_email(token):
    verification = EmailVerification.query.filter_by(token=token).first()
    
    if not verification:
        flash('유효하지 않은 인증 링크입니다.')
        return redirect(url_for('web.login'))
    
    if verification.expiration_time < datetime.datetime.utcnow():
        flash('인증 링크가 만료되었습니다.')
        return redirect(url_for('web.login'))
    
    if verification.is_verified:
        flash('이미 인증이 완료된 계정입니다.')
        return redirect(url_for('web.login'))
    
    user = User.query.get(verification.user_id)
    user.is_authenticated = True
    verification.is_verified = True
    db.session.commit()
    
    flash('이메일 인증이 완료되었습니다. 로그인해주세요.')
    return redirect(url_for('web.login'))

@web_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # 닉네임 변경
        if nickname and nickname != current_user.nickname:
            current_user.nickname = nickname
            flash('닉네임이 변경되었습니다.')
        
        # 비밀번호 변경
        if current_password and new_password and confirm_password:
            if not check_password_hash(current_user.password_hash, current_password):
                flash('현재 비밀번호가 올바르지 않습니다.')
            elif new_password != confirm_password:
                flash('새 비밀번호가 일치하지 않습니다.')
            else:
                current_user.password_hash = generate_password_hash(new_password)
                flash('비밀번호가 변경되었습니다.')
        
        db.session.commit()
        return redirect(url_for('web.profile'))
    
    return render_template('profile.html')

@web_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다.')
    return redirect(url_for('web.index'))

@web_bp.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('관리자만 접근할 수 있습니다.')
        return redirect(url_for('web.index'))
    
    # 통계 정보 가져오기
    stats = {
        'user_count': User.query.count(),
        'post_count': Post.query.count(),
        'comment_count': Comment.query.count(),
        'board_count': Board.query.count()
    }
    
    # 사용자 목록 가져오기
    users = User.query.order_by(User.created_at.desc()).all()
    
    # 게시판 목록 가져오기
    boards = Board.query.order_by(Board.board_id.asc()).all()
    
    return render_template('admin.html', stats=stats, users=users, boards=boards)

@web_bp.route('/board_list')
def board_list():
    boards = Board.query.order_by(Board.board_id.asc()).all()
    return render_template('board_list.html', boards=boards) 