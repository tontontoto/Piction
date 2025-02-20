// 即時実行関数でスコープを分離
(() => {
    console.log("Initializing top page...");

    // 定数定義
    const API_ENDPOINTS = {
        LIKE: '/like',
        UPDATE_RANKING: '/update_ranking'
    };

    const REFRESH_INTERVAL = 10000; // 3秒

    // いいね処理のメイン関数
    function likeSale(saleId, userId, event) {
        event.preventDefault();
        event.stopPropagation();
        
        $.ajax({
            url: API_ENDPOINTS.LIKE,
            type: 'POST',
            data: { saleId, userId },
            success: (data) => {
                updateLikeUI(saleId, data);
                updateRanking();
            },
            error: (jqXHR, textStatus, errorThrown) => {
                console.error('いいね処理エラー:', textStatus, errorThrown);
            }
        });
    }

    // いいねUIの更新
    function updateLikeUI(saleId, data) {
        // いいね数の更新
        updateLikeCount(saleId, data.likeCount);
        // ハートアイコンの更新
        updateHeartIcon(saleId, data.action === 'added');
    }

    // いいね数表示の更新
    function updateLikeCount(saleId, count) {
        document.querySelectorAll(`.like-count-${saleId}`).forEach(element => {
            element.textContent = count;
        });
    }

    // ハートアイコンの更新
    function updateHeartIcon(saleId, isLiked) {
        document.querySelectorAll(`#heart-path-${saleId}`).forEach(path => {
            const attributes = isLiked 
                ? { fill: '#f03eb5', stroke: '#f03eb5' }
                : { fill: '#fff', stroke: '#000' };
            
            Object.entries(attributes).forEach(([attr, value]) => {
                path.setAttribute(attr, value);
            });
        });
    }

    // ランキングの更新
    function updateRanking() {
        $.ajax({
            url: API_ENDPOINTS.UPDATE_RANKING,
            type: 'GET',
            success: (data) => {
                const rankingContainer = document.querySelector('.saleRanking');
                if (rankingContainer) {
                    rankingContainer.innerHTML = data.html;
                    console.log('ランキング更新完了');
                }
            },
            error: (jqXHR, textStatus, errorThrown) => {
                console.error('ランキング更新エラー:', textStatus, errorThrown);
            }
        });
    }

    // グローバルスコープに必要な関数を公開
    window.likeSale = likeSale;

    // 定期的なランキング更新を開始
    setInterval(updateRanking, REFRESH_INTERVAL);
})();