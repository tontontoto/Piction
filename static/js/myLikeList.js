function submitSortOrder() {
    const sortOrder = document.getElementById("productSortSelect").value;

    // サーバーに並び順を送信
    fetch(`/sort_products?order=${sortOrder}`)
        .then(response => response.json())
        .then(data => {
            // 商品情報の更新
            updateProductList(data);
        })
        .catch(error => console.error('Error:', error));
}

function updateProductList(products) {
    const productList = document.getElementById("myLikeListContainer");
    productList.innerHTML = '';  // 既存のリストをクリア

    // 取得した商品情報をリストに追加
    products.forEach(sale => {
        const row = document.createElement('tr');
        row.classList.add('likeList_item');

        const imageUrl = sale.filePath;  // Flask側でフルURLが生成されているため、そのまま使う
        console.log(imageUrl);  // 正しいURLを確認する

        row.innerHTML = `
            <td class="likeList_itemCulumn">
                <img src="${imageUrl}" alt="saleImage" id="uploadImg">
            </td>
            <td class="likeList_itemCulumn">${sale.title}</td>
            <td class="likeList_itemCulumn">￥${sale.currentPrice}</td>
            <td class="likeList_itemCulumn">xxx</td>
            <td class="likeList_itemCulumn">xx:xx</td>
        `;

        productList.appendChild(row);
    });
}