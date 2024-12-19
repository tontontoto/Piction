window.onload = function () {
  const canvas = document.getElementById("myCanvas");
  const context = canvas.getContext("2d");
  const dataURL = localStorage.getItem("canvasImage");
  if (dataURL) {
    const img = new Image();
    img.onload = function () {
      context.drawImage(img, 0, 0);
    };
    img.src = dataURL;
  }
};

document.addEventListener("DOMContentLoaded", function () {
  const time = localStorage.getItem("elapsedTime");
  const price = localStorage.getItem("moneyValue");

  if (time) {
    document.querySelector(".timerResult p2").textContent = time;
  }

  if (price) {
    document.querySelector(".moneyResult p2").textContent = price;
  }
});

document.addEventListener("DOMContentLoaded", () => {
  // 要素を取得
  const close = document.querySelector(".modalClose");
  const container = document.querySelector(".modalContainer");
  const open = document.getElementById("openModal");

  // openボタンをクリックしたらモーダルウィンドウを表示する
  open.addEventListener("click", () => {
    container.classList.add("active"); // クラスを追加
  });

  // closeボタンをクリックしたらモーダルウィンドウを閉じる
  close.addEventListener("click", () => {
    container.classList.remove("active"); // クラスを削除
  });

  // モーダルウィンドウの外側をクリックしたら閉じる
  container.addEventListener("click", (e) => {
    if (
      !e.target.closest(".modalBody") &&
      container.classList.contains("active")
    ) {
      container.classList.remove("active");
    }
  });
});

//本保存
const download = document.getElementById("download");
download.addEventListener("click", () => {
  const time = localStorage.getItem("elapsedTime");
  const price = localStorage.getItem("moneyValue");
  const title = document.getElementById("title").value;
  const dataURL = canvas.toDataURL("image/png"); // 画像をBase64に変換

  localStorage.removeItem("canvasImage");
  localStorage.removeItem("timerValue");
  localStorage.removeItem("elapsedTime");
  localStorage.removeItem("moneyValue");

  fetch("/add_sale", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      title, 
      image: dataURL, 
      time: time, 
      price: price 
    }),
  })
    .then((response) => {
      // 画像保存の結果を表示 デバック用
      if (response.ok) {
        alert("正常に保存されました。");
      } else {
        alert("保存に失敗しました。");
      }
    })
    .then((title) => {
      console.log(title);
    });
});