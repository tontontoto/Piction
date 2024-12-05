window.onload = function() {
  const canvas = document.getElementById('myCanvas');
  const context = canvas.getContext('2d');
  const dataURL = localStorage.getItem('canvasImage');
  if (dataURL) {
      const img = new Image();
      img.onload = function() {
          context.drawImage(img, 0, 0);
      };
      img.src = dataURL;
  }
};

document.addEventListener('DOMContentLoaded', function() {
    const time = localStorage.getItem('timerValue');
    const price = localStorage.getItem('moneyValue');
    
    if (time) {
        document.querySelector('.timerResult p').textContent = `制作時間: ${time}`;
    }
    
    if (price) {
        document.querySelector('.moneyResult p2').textContent = price;
    }
});

//本保存
const download = document.getElementById('download');
download.addEventListener('click', () => {

  const time = localStorage.getItem('timerValue');
  const price = localStorage.getItem('moneyValue');
  const title = document.getElementById('title').value;
  const dataURL = canvas.toDataURL('image/png'); // 画像をBase64に変換
  
  localStorage.removeItem('canvasImage');
  localStorage.removeItem('timerValue');
  localStorage.removeItem('moneyValue');
  
  fetch('/add_sale', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ title, image: dataURL, time: time, price: price}),
    
    }).then(response => {  // 画像保存の結果を表示
      if (response.ok){
        alert('正常に保存されました。');
      } else {
        alert('保存に失敗しました。');
      }
    }).then(title => {
      console.log(title);
    })
  });