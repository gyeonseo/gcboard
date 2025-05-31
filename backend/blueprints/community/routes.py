from flask import Blueprint, request, jsonify, Response
from models import db, Board, Post, User
from sqlalchemy import desc

community_bp = Blueprint('community', __name__)

# 메인 화면: 각 게시판별 최신 게시글 (XML)
@community_bp.route('/web', methods=['GET'])
def community_web():
    boards = Board.query.all()
    xml = '<?xml version="1.0" encoding="UTF-8"?><response>'
    for board in boards:
        xml += f'<board id="{board.board_id}" name="{board.name}" type="list">'
        posts = Post.query.filter_by(board_id=board.board_id).order_by(desc(Post.created_at)).limit(10).all()
        for post in posts:
            xml += f'<article id="{post.post_id}" text="{post.content}" createdAt="{post.created_at}" posvote="{post.like_count}" commentCount="{post.comment_count}" title="{post.title}" />'
        xml += '</board>'
    xml += '</response>'
    return Response(xml, mimetype='application/xml')

# 실시간 인기글 (추천수 10개 이상, 최신순)
@community_bp.route('/popular', methods=['GET'])
def popular():
    posts = Post.query.filter(Post.like_count >= 10).order_by(desc(Post.like_count), desc(Post.created_at)).limit(10).all()
    result = []
    for post in posts:
        user = User.query.get(post.user_id)
        result.append({
            'post_id': post.post_id,
            'title': post.title,
            'content': post.content,
            'like_count': post.like_count,
            'comment_count': post.comment_count,
            'created_at': post.created_at,
            'user': {
                'user_id': user.user_id if not post.is_anonymous else None,
                'nickname': user.nickname if not post.is_anonymous else f"익명{post.anonymous_index}" if post.anonymous_index else "익명"
            }
        })
    return jsonify({'popular_articles': result})

# 게시글/사용자 검색
@community_bp.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('q', '')
    board_id = request.args.get('board_id', None)
    q = Post.query
    if board_id:
        q = q.filter_by(board_id=board_id)
    if keyword:
        q = q.filter(Post.title.contains(keyword) | Post.content.contains(keyword))
    posts = q.order_by(desc(Post.created_at)).limit(50).all()
    result = []
    for post in posts:
        user = User.query.get(post.user_id)
        result.append({
            'post_id': post.post_id,
            'title': post.title,
            'content': post.content,
            'like_count': post.like_count,
            'comment_count': post.comment_count,
            'created_at': post.created_at,
            'user': {
                'user_id': user.user_id if not post.is_anonymous else None,
                'nickname': user.nickname if not post.is_anonymous else f"익명{post.anonymous_index}" if post.anonymous_index else "익명"
            }
        })
    return jsonify({'results': result})
