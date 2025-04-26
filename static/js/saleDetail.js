document.addEventListener("DOMContentLoaded", function () {
  const bidButton = document.getElementById("bid");
  const addTenButton = document.getElementById("addTen");
  const addHundredButton = document.getElementById("addHundred");
  const specifyInput = document.getElementById("specify");
  const minBidPriceElement = document.getElementById("minBidPrice");
  const minBid = parseInt(minBidPriceElement.textContent.replace(/[￥,]/g, ""), 10);
  console.log("最低入札価格:", minBid);
  // 金額を更新する関数
  function updateAmount(amount) {
    let currentValue = parseInt(specifyInput.value, 10) || 0;
    let newValue = currentValue + amount;
    specifyInput.value = newValue;
  }

  // 金額増加ボタンのイベントリスナー
  addTenButton.addEventListener("click", () => updateAmount(10));
  addHundredButton.addEventListener("click", () => updateAmount(100));

  // オークション終了時刻の取得
  const finishTimeElement = document.getElementById("finishTime");
  const finishTimeStr = finishTimeElement.dataset.finishTime;
  const finishTime = new Date(finishTimeStr.replace(/\//g, "-"));

  // カウントダウンを更新する関数
  function updateCountdown() {
    const now = new Date();
    const timeDiff = finishTime - now;

    if (timeDiff <= 0) {
      document.getElementById("remainingTime").textContent = "オークション終了";
      location.reload();
      return;
    }

    const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

    let timeStr = "";
    if (days > 0) timeStr += `${days}日 `;
    if (hours > 0) timeStr += `${hours}時間 `;
    if (minutes > 0) timeStr += `${minutes}分 `;
    timeStr += `${seconds}秒`;

    document.getElementById("remainingTime").textContent = timeStr;
  }

  // 初回実行
  updateCountdown();
  setInterval(updateCountdown, 1000);

  // 入札ボタンのイベントリスナー
  bidButton.addEventListener("click", function () {
    const specifiedAmount = parseInt(specifyInput.value, 10);

    // 入札額が数値でない、マイナス、最低入札金額より低い場合のチェック
    if (isNaN(specifiedAmount)) {
      alert("入札額を入力してください。");
      return;
    }
    if (specifiedAmount < 0) {
      alert(`入札額は最低入札金額（￥${minBid.toLocaleString()}）以上にしてください。`);
      return;
    }
    if (specifiedAmount < minBid) {
      alert(`入札額は最低入札金額（￥${minBid.toLocaleString()}）以上にしてください。`);
      return;
    }

    // 入札処理を実行
    fetch("/bid", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        saleId: document.getElementById("saleId").dataset.saleId,
        amount: specifiedAmount,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("入札が成功しました");
          location.reload();
        } else {
          alert(data.message || "入札に失敗しました");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("入札に失敗しました");
      });
  });
});
