from flask import Blueprint, request, jsonify
from backend.models import db, Like, Post
from flask_login import login_required, current_user

like_bp = Blueprint('like', __name__)

# 게시글 좋아요
@like_bp.route('/article/vote', methods=['POST'])
@login_required
def article_vote():
    post_id = request.form.get('id')
    vote = int(request.form.get('vote', 1))
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'response': -1})
    # 중복 체크
    like = Like.query.filter_by(user_id=current_user.user_id, post_id=post_id).first()
    if like:
        return jsonify({'response': -1})
    new_like = Like(user_id=current_user.user_id, post_id=post_id)
    db.session.add(new_like)
    post.like_count += 1
    db.session.commit()
    return jsonify({'response': post.like_count})
