// static/js/main.js

document.addEventListener('DOMContentLoaded', function () {
    // 게시글 좋아요(추천) 비동기 처리
    const likeForm = document.getElementById('like-form');
    if (likeForm) {
        likeForm.addEventListener('submit', function (e) {
            e.preventDefault();
            fetch(likeForm.action, {
                method: 'POST',
                body: new FormData(likeForm),
                credentials: 'same-origin'
            })
            .then(res => res.json())
            .then(data => {
                if (data.response == -1) {
                    alert('이미 추천하셨습니다.');
                } else {
                    document.getElementById('like-count').innerText = data.response;
                }
            });
        });
    }

    // 게시글 삭제 비동기 처리
    const postDeleteForms = document.querySelectorAll('form[action$="article/remove"]');
    postDeleteForms.forEach(function(form){
        form.addEventListener('submit', function(e){
            e.preventDefault();
            if (!confirm('정말 삭제하시겠습니까?')) return;
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                credentials: 'same-origin'
            })
            .then(res => res.json())
            .then(data => {
                if (data.result === 'success') {
                    window.location.href = '/';
                } else {
                    alert('삭제 실패: ' + (data.reason || ''));
                }
            });
        });
    });

    // 댓글 삭제 비동기 처리
    const commentDeleteForms = document.querySelectorAll('form[action$="comment/remove"]');
    commentDeleteForms.forEach(function(form){
        form.addEventListener('submit', function(e){
            e.preventDefault();
            if (!confirm('댓글을 삭제하시겠습니까?')) return;
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                credentials: 'same-origin'
            })
            .then(res => res.json())
            .then(data => {
                if (data.result === 'success') {
                    window.location.reload();
                } else {
                    alert('삭제 실패: ' + (data.reason || ''));
                }
            });
        });
    });

    // 댓글 비동기 작성 (선택)
    const commentForm = document.querySelector('form[action$="comment/add"]');
    if (commentForm) {
        commentForm.addEventListener('submit', function(e){
            e.preventDefault();
            const formData = new FormData(commentForm);
            fetch(commentForm.action, {
                method: 'POST',
                body: formData,
                credentials: 'same-origin'
            })
            .then(res => res.json())
            .then(data => {
                if (data.result === 'success') {
                    window.location.reload();
                } else {
                    alert('댓글 작성 실패');
                }
            });
        });
    }

    // 게시글/댓글 폼 중복 제출 방지
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form){
        form.addEventListener('submit', function(e){
            const btn = form.querySelector('button[type="submit"]');
            if (btn) btn.disabled = true;
            setTimeout(() => { if (btn) btn.disabled = false; }, 2000);
        });
    });

    // 알림 읽음 처리 (예시)
    const notificationItems = document.querySelectorAll('.notification-item');
    notificationItems.forEach(function(item){
        item.addEventListener('click', function(){
            const notificationId = item.dataset.id;
            fetch(`/api/notification/read`, {
                method: 'POST',
                body: JSON.stringify({ notification_id: notificationId }),
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin'
            }).then(() => {
                item.classList.add('read');
            });
        });
    });

    // 관리자 통계 새로고침 (예시)
    const statsRefreshBtn = document.getElementById('admin-stats-refresh');
    if (statsRefreshBtn) {
        statsRefreshBtn.addEventListener('click', function(){
            fetch('/api/admin/stats')
            .then(res => res.json())
            .then(data => {
                document.getElementById('user-count').innerText = data.user_count;
                document.getElementById('post-count').innerText = data.post_count;
                document.getElementById('comment-count').innerText = data.comment_count;
                document.getElementById('board-count').innerText = data.board_count;
            });
        });
    }
});
