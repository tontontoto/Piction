function submitSortOrder() {
    const sortOrder = document.getElementById("productSortSelect").value;
    const container = document.querySelector('.likes-grid');

    // サーバーに並び順を送信
    fetch(`/sort_products?order=${sortOrder}`)
        .then(response => response.json())
        .then(data => {
            console.log('並び替え結果:', data);
            // 既存のコンテンツをクリア
            container.innerHTML = '';
            
            // 新しいコンテンツを追加
            data.forEach(sale => {
                const card = document.createElement('a');
                card.href = `/saleDetail/${sale.id}`;
                card.className = 'like-card';
                
                card.innerHTML = `
                    <div class="card-image">
                        <img src="${sale.filePath}" alt="${sale.title}">
                    </div>
                    <div class="card-content">
                        <h2>${sale.title}</h2>
                        <div class="card-info">
                            <div class="price">¥${sale.currentPrice.toLocaleString()}</div>
                            <div class="bid-count">入札 ${sale.bidCount}</div>
                            <div class="remaining-time">${sale.remainingTime}</div>
                        </div>
                    </div>
                `;
                
                container.appendChild(card);
            });
        })
        .catch(error => console.error('Error:', error));
}

// セレクトボックスの変更イベントを監視
document.addEventListener('DOMContentLoaded', () => {
    const sortSelect = document.getElementById('productSortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', submitSortOrder);
    }
});