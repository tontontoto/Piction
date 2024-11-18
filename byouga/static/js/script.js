const canvas = document.getElementById("myCanvas");
const context = canvas.getContext("2d");

const size = Math.min(window.innerWidth * 0.8, window.innerHeight * 0.8);
canvas.style.width = `${size}px`; // 見た目のサイズ
canvas.style.height = `${size}px`; // 見た目のサイズ
canvas.width = size; // 描画解像度（内部ピクセル数）
canvas.height = size;

window.addEventListener("resize", () => {
  const size = Math.min(window.innerWidth * 0.8, window.innerHeight * 0.8);
  canvas.style.width = `${size}px`;
  canvas.style.height = `${size}px`;
  canvas.width = size;
  canvas.height = size;

  // 必要なら再描画
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "white";
  context.fillRect(0, 0, canvas.width, canvas.height);
});

context.rect(0, 0, canvas.width, canvas.height);
context.fillStyle = "white";
context.fill();
context.beginPath();
context.lineWidth = 5;
context.strokeStyle = 'black';

let mouse = {x:0, y:0};

canvas.addEventListener("mousemove", function(e) {
  const rect = canvas.getBoundingClientRect();
  mouse.x = e.clientX - rect.left;
  mouse.y = e.clientY - rect.top;
}, false);

canvas.addEventListener("mousedown", function(e) {
    context.beginPath();
    context.moveTo(mouse.x, mouse.y);

    canvas.addEventListener("mousemove", onPaint, false);
}, false);

canvas.addEventListener("mouseup", function() {
  canvas.removeEventListener("mousemove", onPaint, false);
}, false);

const onPaint = function() {
    context.lineTo(mouse.x, mouse.y);
    context.stroke();
}

// 画像保存
document.getElementById("download").onclick = (event) => {
	let canvas = document.getElementById("myCanvas");

	let link = document.createElement("a");
	link.href = canvas.toDataURL("image/jpeg");
	link.download = "test.jpg";
	link.click();
}


download.addEventListener('click', () => {
    const dataURL = canvas.toDataURL('image/png'); // 画像をBase64に変換
    fetch('/save-image', {
      method: 'POST',
      body: JSON.stringify({ image: dataURL }),
      headers: {
        'Content-Type': 'application/json',
      },
                    }).then(response => {
      if (response.ok) {
        alert('Image saved successfully!');
      } else {
        alert('Failed to save image.');
      }
    });
  });