console.log("hello!");
function likeSale(saleId) {
    console.log('いいねされたSaleId:', saleId);
    // AJAXリクエストを使ってサーバーに「いいね」の情報を送信
    fetch('/like/' + SaleId, {
        method: 'POST',  // HTTPメソッドをPOSTに設定
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())  // サーバーからのレスポンスをJSONとして受け取る
    .then(data => {
        // サーバーから返された新しいいいね数を更新
        document.getElementById('like-count-' + SaleId).innerText = data.like_count + ' いいね';
    })
    .catch(error => {
        console.error('Error:', error);
    });
}