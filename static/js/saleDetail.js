document.addEventListener("DOMContentLoaded", function () {
  const bidButton = document.getElementById("bid");
  const addTenButton = document.getElementById("addTen");
  const addHundredButton = document.getElementById("addHundred");
  const specifyInput = document.getElementById("specify");
  const addAmountButton = document.getElementById("addAmount");
  const minBidPrice = document.getElementById("minBidPrice");

  let currentAmount = parseInt(
    document.getElementById("addAmount").textContent.replace(/[^0-9]/g, ""),
    10
  );

  // 金額を更新する関数
  function updateAmount(amount) {
    currentAmount += amount;
    addAmountButton.textContent = `${currentAmount}`;
  }

  // 金額増加ボタンのイベントリスナー
  addTenButton.addEventListener("click", () => updateAmount(10));
  addHundredButton.addEventListener("click", () => updateAmount(100));

  // 終了時刻を取得
  const finishTimeElement = document.getElementById('finishTime');
  const finishTimeStr = finishTimeElement.dataset.finishTime;
  const finishTime = new Date(finishTimeStr.replace(/\//g, '-'));

  // カウントダウンを更新する関数
  function updateCountdown() {
    const now = new Date();
    const timeDiff = finishTime - now;

    if (timeDiff <= 0) {
      // オークション終了時の処理
      document.getElementById('remainingTime').textContent = 'オークション終了';
      location.reload(); // ページをリロード
      return;
    }

    // 残り時間を計算
    const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

    // 表示をフォーマット
    let timeStr = '';
    if (days > 0) timeStr += `${days}日 `;
    if (hours > 0) timeStr += `${hours}時間 `;
    if (minutes > 0) timeStr += `${minutes}分 `;
    timeStr += `${seconds}秒`;

    document.getElementById('remainingTime').textContent = timeStr;
  }

  // 初回実行
  updateCountdown();

  // 1秒ごとに更新
  setInterval(updateCountdown, 1000);

  // 入札ボタンのイベントリスナー
  bidButton.addEventListener("click", function () {
    const specifiedAmount = parseInt(specifyInput.value, 10) || 0;
    const addAmount = parseInt(addAmountButton.textContent, 10);
    const minBid = parseInt(minBidPrice.textContent, 10);

    let finalAmount = Math.max(specifiedAmount, addAmount);

    if (isNaN(finalAmount) || finalAmount < minBid) {
      alert("有効な金額を入力してください"+"specifiedAmount:"+specifiedAmount+"addAmount:"+addAmount+"minBid:"+minBid);
      return;
    }

    fetch("/bid", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        saleId: document.getElementById("saleId").dataset.saleId,
        amount: finalAmount,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("入札が成功しました");
          location.reload();
        } else {
          alert(data.message || "入札に失敗しました");
      }})
      .catch((error) => {
        console.error("Error:", error);
        alert("入札に失敗しました");
      });
  });
});
