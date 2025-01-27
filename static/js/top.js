console.log("hello!");

var xhr = new XMLHttpRequest();
xhr.open('POST', '/like', true);
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
xhr.send('saleId=' + saleId + '&userId=' + userId);
xhr.onload = function() {
    if (xhr.status === 200 && xhr.readyState === 4) {
        console.log(xhr.responseText);
    }
};

function likeSale(saleId, userId, event) {
    event.preventDefault();
    event.stopPropagation();
    
    // jQueryのAjax実装
    //参考URL　https://job-support.ne.jp/blog/javascript/howto-ajax
    $.ajax({
        url: '/like',
        type: 'POST',
        data: {
            'saleId': saleId,
            'userId': userId
        },
        success: function(data) {
            // いいね数とアイコンの更新
            updateLikeUI(saleId, data);
            // ランキングの更新
            updateRanking();
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error('Error:', textStatus, errorThrown);
        }
    });
}

// いいねUIの更新
function updateLikeUI(saleId, data) {
    // すべてのいいね数表示要素を更新
    const likeCountElements = document.querySelectorAll(`.like-count-${saleId}`);
    likeCountElements.forEach(element => {
        element.textContent = data.likeCount;
    });

    // すべてのハートアイコンを更新
    const heartIconPaths = document.querySelectorAll(`#heart-path-${saleId}`);
    heartIconPaths.forEach(path => {
        if (data.action === 'added') {
            path.setAttribute('fill', '#f03eb5');
            path.setAttribute('stroke', '#f03eb5');
        } else {
            path.setAttribute('fill', '#fff');
            path.setAttribute('stroke', '#000');
        }
    });
}

// ランキングの更新
function updateRanking() {
    $.ajax({
        url: '/update_ranking',
        type: 'GET',
        success: function(data) {
            const rankingContainer = document.querySelector('.saleRanking');
            rankingContainer.innerHTML = data.html;
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error('Ranking update error:', textStatus, errorThrown);
        }
    });
}

// 定期的なランキング更新
setInterval(updateRanking, 30000); // 30秒ごとに更新