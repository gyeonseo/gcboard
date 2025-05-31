from flask import Blueprint, request, jsonify
from models import db, Comment, Post, User
from flask_login import login_required, current_user
from sqlalchemy import desc

comment_bp = Blueprint('comment', __name__)

# 댓글 목록 조회
@comment_bp.route('/list', methods=['GET'])
def comment_list():
    post_id = request.args.get('id')
    limit_num = int(request.args.get('limit_num', -1))
    article_info = request.args.get('articleInfo', 'false').lower() == 'true'
    q = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc())
    comments = q.all() if limit_num == -1 else q.limit(limit_num).all()
    result = []
    for c in comments:
        user = User.query.get(c.user_id)
        result.append({
            'comment_id': c.comment_id,
            'content': c.content,
            'is_anonymous': c.is_anonymous,
            'anonymous_index': c.anonymous_index,
            'created_at': c.created_at,
            'user': {
                'user_id': user.user_id if not c.is_anonymous else None,
                'nickname': user.nickname if not c.is_anonymous else f"익명{c.anonymous_index}" if c.anonymous_index else "익명"
            }
        })
    resp = {'comments': result}
    if article_info:
        post = Post.query.get(post_id)
        if post:
            resp['post'] = {
                'post_id': post.post_id,
                'title': post.title,
                'content': post.content,
                'like_count': post.like_count,
                'comment_count': post.comment_count,
                'created_at': post.created_at
            }
    return jsonify(resp)

# 댓글 작성
@comment_bp.route('/add', methods=['POST'])
@login_required
def comment_add():
    post_id = request.form.get('post_id')
    content = request.form.get('content')
    is_anonym = request.form.get('is_anonym') == '1'
    
    if is_anonym:
        # 같은 사용자의 이전 익명 댓글 번호 찾기
        prev_comment = Comment.query.filter_by(
            post_id=post_id,
            user_id=current_user.user_id,
            is_anonymous=True
        ).order_by(Comment.created_at.desc()).first()
        
        if prev_comment and prev_comment.anonymous_index:
            anonymous_index = prev_comment.anonymous_index
        else:
            # 새로운 익명 번호 할당
            max_idx = db.session.query(db.func.max(Comment.anonymous_index)).filter_by(post_id=post_id).scalar() or 0
            anonymous_index = max_idx + 1
    else:
        anonymous_index = None
        
    comment = Comment(
        content=content,
        is_anonymous=is_anonym,
        anonymous_index=anonymous_index,
        user_id=current_user.user_id,
        post_id=post_id
    )
    db.session.add(comment)
    # 댓글 수 업데이트
    post = Post.query.get(post_id)
    post.comment_count += 1
    db.session.commit()
    return jsonify({'result': 'success', 'comment_id': comment.comment_id})

# 댓글 삭제 (작성자/관리자)
@comment_bp.route('/remove', methods=['POST'])
@login_required
def comment_remove():
    comment_id = request.form.get('comment_id')
    comment = Comment.query.get(comment_id)
    if not comment or (comment.user_id != current_user.user_id and current_user.role != "admin"):
        return jsonify({'result': 'fail', 'reason': 'Permission denied'}), 403
    post = Post.query.get(comment.post_id)
    db.session.delete(comment)
    if post and post.comment_count > 0:
        post.comment_count -= 1
    db.session.commit()
    return jsonify({'result': 'success'})
