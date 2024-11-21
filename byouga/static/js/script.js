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

// タイマー
function startTimer(duration, display) {
  var timer = duration, minutes, seconds;
  setInterval(function () {
      minutes = parseInt(timer / 60, 10);
      seconds = parseInt(timer % 60, 10);

      minutes = minutes < 10 ? "0" + minutes : minutes;
      seconds = seconds < 10 ? "0" + seconds : seconds;

      display.textContent = minutes + ":" + seconds;

      if (--timer < 0) {
          timer = duration;
      }
  }, 1000);
}

// 値段の変化
let moneyElement = document.querySelector('.money p');
let money = 502;

function updateMoney() {
    if (moneyElement && money > 0) {
        money -= 2;
        moneyElement.textContent = money + '円';
    }
}

setInterval(updateMoney, 1000);

window.onload = function () {
  var threeMinutes = 60 * 3,
      display = document.querySelector('.timer p');
  startTimer(threeMinutes, display);
};

// 描画内容の仮保存
function saveCanvas() {
  var canvas = document.getElementById('myCanvas');
  var dataURL = canvas.toDataURL();
  localStorage.setItem('canvasImage', dataURL);

  // タイマーと値段を保存
  var timerValue = document.querySelector('.timer p').textContent;
  localStorage.setItem('timerValue', timerValue);
  localStorage.setItem('moneyValue', money);
}

//ボタンをクリックしたときに保存する
window.addEventListener('DOMContentLoaded', (event) => {
  const saveButton = document.getElementById('saveButton');
  if (saveButton) {
    saveButton.addEventListener('click', saveCanvas);
  }
});