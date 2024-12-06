// ハートクリック処理　(白 <==> ピンク)
// document.getElementById('heart-icon').addEventListener('click', function () {
//     // パスの色を変更
//     const path = document.getElementById('heart-path');
//     if (path.getAttribute('fill') === '#f03eb5') {
//         path.setAttribute('fill', '#fff');
//         path.setAttribute('stroke', '#000');
//     } else {
//         path.setAttribute('fill', '#f03eb5');
//         path.setAttribute('stroke', '#f03eb5');
//     }
// });


console.log("hello!");

function likeSale(saleId, userId) {
    fetch('/like', {
        method: 'POST',
        body: new URLSearchParams({
            'saleId': saleId,
            'userId': userId
        })
    })
        .then(response => response.json())
        .then(data => {
            // 「いいね」数を更新
            const likeCountElement = document.getElementById(`like-count-${saleId}`);
            likeCountElement.textContent = data.likeCount;

            // ハートアイコンの色を変更（いいね状態に応じて）
            const heartIconPath = document.getElementById(`heart-path-${saleId}`);
            if (heartIconPath) {
                if (data.action === 'added') {
                    heartIconPath.setAttribute('fill', 'pink');
                    heartIconPath.setAttribute('stroke', 'pink');
                } else {
                    heartIconPath.setAttribute('fill', '#fff');
                    heartIconPath.setAttribute('stroke', '#000');
                }
            }
        })
        .catch(error => console.error('Error:', error));
}