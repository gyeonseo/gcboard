from backend.models import db, Board, User, Post
from flask_login import login_user
import json

def test_login_and_create_post(client, app, setup_user_and_board):
    from backend.models import User, Board

    # 🔹 DB에서 유저와 게시판 정보 가져오기
    with app.app_context():
        user = User.query.filter_by(email="test@naver.com").first()
        board = Board.query.first()
        board_id = board.board_id

    # 🔹 로그인 요청
    res_login = client.post("/api/auth/login", json={
        "email": "test@naver.com",
        "password": "test1234"
    })
    assert res_login.status_code == 200
    print("\n[LOGIN] Response:", res_login.get_json())

    print("\n✅ 게시글 작성 요청 API 테스트")
    title = "통합테스트 제목"
    text = "통합테스트 본문"
    res_post = client.post("/api/board/article", data={
        "id": board_id,
        "title": title,
        "text": text,
        "is_anonym": 1
    })

    print("\n[CREATE POST AFTER LOGIN]")
    print("Response Status:", res_post.status_code)
    print("Response JSON:", res_post.get_json())

    assert res_post.status_code == 200
    post_data = res_post.get_json()

    print("\n[CREATE POST RESPONSE]", post_data)
    assert post_data["result"] == "success"
    created_post_id  = post_data["post_id"]

    res_list = client.get(f"/api/board/article/list?id={board_id}")
    assert res_list.status_code == 200

    res_json = res_list.get_json()
    print("\n[ARTICLE LIST RESPONSE]", res_json)

    posts = res_json["posts"]
    assert isinstance(posts, list)
    assert any(p["post_id"] == created_post_id and p["title"] == title for p in posts)

    print("\n✅ 게시글이 게시판 목록 API에서 정상 확인되었습니다.")

    


def test_get_board_list(client, app, setup_user_and_board):
    # 게시판 리스트 요청
    print("\n✅ 게시판 리스트 요청 API 테스트")
    response = client.get("/api/board/list")
    assert response.status_code == 200

    board_list = response.get_json()
    assert isinstance(board_list, list)
    assert len(board_list) > 0

    first_board = board_list[0]
    assert "board_id" in first_board
    assert "name" in first_board
    assert "description" in first_board

    print("\n[BOARD LIST] Response:", board_list)


