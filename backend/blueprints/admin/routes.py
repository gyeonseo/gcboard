from flask import Blueprint, request, jsonify, flash, redirect, url_for
from backend.models import db, User, Post, Comment, Board, Like
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from backend.utils.email import send_email
import secrets
import string

admin_bp = Blueprint('admin', __name__)

def generate_random_password(length=12):
    """랜덤 비밀번호 생성"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

# 통계 정보
@admin_bp.route('/stats', methods=['GET'])
@login_required
def stats():
    if current_user.role != "admin":
        return jsonify({'result': 'fail', 'reason': 'Permission denied'}), 403
    user_count = User.query.count()
    post_count = Post.query.count()
    comment_count = Comment.query.count()
    board_count = Board.query.count()
    return jsonify({
        'user_count': user_count,
        'post_count': post_count,
        'comment_count': comment_count,
        'board_count': board_count
    })

# 사용자 제재(정지/해제)
@admin_bp.route('/ban_user', methods=['POST'])
@login_required
def ban_user():
    if current_user.role != 'admin':
        flash('권한이 없습니다.')
        return redirect(url_for('web.index'))
    
    user_id = request.form.get('user_id')
    ban = request.form.get('ban') == '1'
    role = request.form.get('role')
    
    user = User.query.get_or_404(user_id)
    
    if role:
        user.role = role
    
    user.is_banned = ban
    db.session.commit()
    
    flash('사용자 상태가 변경되었습니다.')
    return redirect(url_for('web.admin'))

@admin_bp.route('/reset_password', methods=['POST'])
@login_required
def reset_password():
    if current_user.role != 'admin':
        flash('권한이 없습니다.')
        return redirect(url_for('web.index'))
    
    user_id = request.form.get('user_id')
    user = User.query.get_or_404(user_id)
    
    # 랜덤 비밀번호 생성
    new_password = generate_random_password()
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    # 이메일 발송
    send_email(
        subject='비밀번호가 초기화되었습니다',
        recipients=[user.email],
        text_body=f'새로운 비밀번호: {new_password}\n로그인 후 비밀번호를 변경해주세요.',
        html_body=f'<p>새로운 비밀번호: <strong>{new_password}</strong></p><p>로그인 후 비밀번호를 변경해주세요.</p>'
    )
    
    flash('비밀번호가 초기화되었습니다.')
    return redirect(url_for('web.admin'))

@admin_bp.route('/users/<int:user_id>', methods=['POST', 'DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403

    # method override 처리
    if request.method == 'POST' and request.form.get('_method') != 'DELETE':
        return jsonify({'error': '잘못된 요청입니다.'}), 400

    user = User.query.get_or_404(user_id)
    if user.email in ['admin@example.com', 'unknown@example.com']:
        return jsonify({'error': '이 계정은 삭제할 수 없습니다.'}), 400

    # '알 수 없음' 사용자 찾기 또는 생성
    unknown_user = User.query.filter_by(nickname='알 수 없음').first()
    if not unknown_user:
        unknown_user = User(
            email='unknown@example.com',
            nickname='알 수 없음',
            password_hash=generate_password_hash('unknown'),
            is_authenticated=True,
            is_banned=False,
            role='user'
        )
        db.session.add(unknown_user)
        db.session.commit()

    # 게시글, 댓글, 추천의 user_id를 unknown으로 변경
    Post.query.filter_by(user_id=user_id).update({'user_id': unknown_user.user_id})
    Comment.query.filter_by(user_id=user_id).update({'user_id': unknown_user.user_id})
    Like.query.filter_by(user_id=user_id).update({'user_id': unknown_user.user_id})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': '사용자가 삭제되었습니다. (작성글/댓글/추천은 알 수 없음으로 이전됨)'})

@admin_bp.route('/post/delete', methods=['POST'])
@login_required
def delete_post():
    if current_user.role != 'admin':
        flash('권한이 없습니다.')
        return redirect(url_for('web.index'))
    
    post_id = request.form.get('post_id')
    post = Post.query.get_or_404(post_id)
    
    # 게시물의 댓글 삭제
    Comment.query.filter_by(post_id=post_id).delete()
    
    # 게시물 삭제
    db.session.delete(post)
    db.session.commit()
    
    flash('게시물이 삭제되었습니다.')
    return redirect(url_for('web.admin'))

@admin_bp.route('/posts/search')
@login_required
def search_posts():
    if current_user.role != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    query = request.args.get('q', '')
    posts = Post.query.join(Board).join(User).filter(
        (Post.title.ilike(f'%{query}%')) |
        (Post.content.ilike(f'%{query}%')) |
        (User.nickname.ilike(f'%{query}%'))
    ).order_by(Post.created_at.desc()).limit(50).all()
    
    return jsonify({
        'posts': [{
            'post_id': post.post_id,
            'title': post.title,
            'author': post.author.nickname if not post.is_anonymous else f'익명{post.anonymous_index}',
            'board_name': post.board.name,
            'created_at': post.created_at.isoformat()
        } for post in posts]
    })

@admin_bp.route('/users/<int:user_id>/force_verify', methods=['POST'])
@login_required
def force_verify_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403
    user = User.query.get_or_404(user_id)
    user.is_authenticated = True
    db.session.commit()
    return redirect(url_for('web.admin'))
