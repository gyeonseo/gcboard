from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from backend.models import db, Board, Post, User, Like
from flask_login import login_required, current_user
from sqlalchemy import desc

board_bp = Blueprint('board', __name__)

# 게시판 목록 조회
@board_bp.route('/list', methods=['GET'])
def board_list():
    boards = Board.query.order_by(Board.board_id.asc()).all()
    return jsonify([{'board_id': b.board_id, 'name': b.name, 'description': b.description} for b in boards])

# 게시판 생성/수정/삭제 (관리자)
@board_bp.route('/manage', methods=['POST', 'PUT', 'DELETE'])
@login_required
def board_manage():
    if current_user.role != "admin":
        return jsonify({'result': 'fail', 'reason': 'Permission denied'}), 403
    
    if request.method == 'POST':
        # JSON 또는 폼 데이터 처리
        if request.is_json:
            data = request.get_json()
            name = data.get('name')
            description = data.get('description', '')
        else:
            name = request.form.get('name')
            description = request.form.get('description', '')
            action = request.form.get('action')
            
            # 삭제 요청 처리
            if action == 'delete':
                board_id = request.form.get('board_id')
                board = Board.query.get_or_404(board_id)
                db.session.delete(board)
                db.session.commit()
                flash('게시판이 삭제되었습니다.')
                return redirect(url_for('web.admin'))
        
        if not name:
            return jsonify({'result': 'fail', 'reason': 'Name is required'}), 400
            
        board = Board(name=name, description=description)
        db.session.add(board)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'result': 'success', 'board_id': board.board_id})
        else:
            flash('게시판이 생성되었습니다.')
            return redirect(url_for('web.admin'))
            
    elif request.method == 'PUT':
        data = request.get_json()
        board = Board.query.get(data['board_id'])
        if not board:
            return jsonify({'result': 'fail', 'reason': 'No such board'}), 404
        board.name = data['name']
        board.description = data.get('description', board.description)
        db.session.commit()
        return jsonify({'result': 'success'})
        
    elif request.method == 'DELETE':
        data = request.get_json()
        board = Board.query.get(data['board_id'])
        if not board:
            return jsonify({'result': 'fail', 'reason': 'No such board'}), 404
        db.session.delete(board)
        db.session.commit()
        return jsonify({'result': 'success'})

# 게시글 작성/수정
@board_bp.route('/article', methods=['POST'])
@login_required
def article():
    board_id = request.form.get('id')
    title = request.form.get('title')
    text = request.form.get('text')
    is_anonym = request.form.get('is_anonym') == '1'
    article_id = request.form.get('article_id')
    if not (board_id and title and text):
        return jsonify({'result': 'fail', 'reason': 'Missing required fields'}), 400

    if article_id:
        post = Post.query.get(article_id)
        if not post or (post.user_id != current_user.user_id and current_user.role != "admin"):
            return jsonify({'result': 'fail', 'reason': 'Permission denied'}), 403
        post.title = title
        post.content = text
        post.is_anonymous = is_anonym
        db.session.commit()
        return jsonify({'result': 'success', 'post_id': post.post_id})
    else:
        # 익명 인덱스 할당
        if is_anonym:
            max_idx = db.session.query(db.func.max(Post.anonymous_index)).filter_by(board_id=board_id).scalar() or 0
            anonymous_index = max_idx + 1
        else:
            anonymous_index = None
        post = Post(
            title=title,
            content=text,
            is_anonymous=is_anonym,
            anonymous_index=anonymous_index,
            user_id=current_user.user_id,
            board_id=board_id
        )
        db.session.add(post)
        db.session.commit()
        return jsonify({'result': 'success', 'post_id': post.post_id})

# 게시글 삭제
@board_bp.route('/article/remove', methods=['POST'])
@login_required
def article_remove():
    post_id = request.form.get('id')
    post = Post.query.get(post_id)
    if not post or (post.user_id != current_user.user_id and current_user.role != "admin"):
        return jsonify({'result': 'fail', 'reason': 'Permission denied'}), 403
    
    # 관련된 좋아요 데이터 삭제
    Like.query.filter_by(post_id=post_id).delete()
    
    # 게시글 삭제
    db.session.delete(post)
    db.session.commit()
    return jsonify({'result': 'success'})

# 게시글 목록 조회 (페이징, 최신순)
@board_bp.route('/article/list', methods=['GET'])
def article_list():
    board_id = request.args.get('id')
    limit_num = int(request.args.get('limit_num', 20))
    start_num = int(request.args.get('start_num', 0))
    q = Post.query.filter_by(board_id=board_id).order_by(desc(Post.created_at))
    total = q.count()
    posts = q.offset(start_num).limit(limit_num).all()
    result = []
    for post in posts:
        user = User.query.get(post.user_id)
        result.append({
            'post_id': post.post_id,
            'title': post.title,
            'content': post.content,
            'is_anonymous': post.is_anonymous,
            'anonymous_index': post.anonymous_index,
            'like_count': post.like_count,
            'comment_count': post.comment_count,
            'created_at': post.created_at,
            'user': {
                'user_id': user.user_id if not post.is_anonymous else None,
                'nickname': user.nickname if not post.is_anonymous else f"익명{post.anonymous_index}" if post.anonymous_index else "익명"
            }
        })
    return jsonify({'total': total, 'posts': result})

# 게시판 상세 페이지
@board_bp.route('/<int:board_id>', methods=['GET'])
def board_detail(board_id):
    board = Board.query.get_or_404(board_id)
    posts = Post.query.filter_by(board_id=board_id).order_by(desc(Post.created_at)).limit(20).all()
    return render_template('board_detail.html', board=board, posts=posts)

# 게시글 상세 페이지
@board_bp.route('/post/<int:post_id>', methods=['GET'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

# 게시글 작성 페이지
@board_bp.route('/write/<int:board_id>', methods=['GET'])
@login_required
def write_post(board_id):
    board = Board.query.get_or_404(board_id)
    return render_template('write_post.html', board=board)
