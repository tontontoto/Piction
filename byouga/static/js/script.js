const canvas = document.getElementById("myCanvas");
const stage = new createjs.Stage(canvas);

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
});

function drawBackground() {
  const background = new createjs.Shape();
  background.graphics.beginFill("white").drawRect(0, 0, canvas.width, canvas.height);
  stage.addChild(background);
  stage.update();
}

drawBackground();

const line = new createjs.Shape();
stage.addChild(line);

let isDrawing = false;
let isEraserActive = false;

const penButton = document.getElementById("pen");
penButton.addEventListener("click", () => {
  isEraserActive = false; // ペンに切り替え
});

// 消しゴムボタンのクリックイベント
const eraserButton = document.getElementById("eraser");
eraserButton.addEventListener("click", () => {
  isEraserActive = true; // 消しゴム切り替え
});

// クリアボタンのクリックイベント
const clearButton = document.getElementById("reset");
clearButton.addEventListener("click", () => {
  line.graphics.clear();
  stage.update();
});

canvas.addEventListener("mousedown", (e) => {
  isDrawing = true;

  const rect = canvas.getBoundingClientRect();
  const mouseX = e.clientX - rect.left;
  const mouseY = e.clientY - rect.top;

  if (isEraserActive) {
    // 消しゴムの設定
    line.graphics.setStrokeStyle(20).beginStroke("white").moveTo(mouseX, mouseY);
  } else {
    // 通常のペン設定
    const paintColor = document.querySelector("#inputColor").value;
    line.graphics.setStrokeStyle(5).beginStroke(paintColor).moveTo(mouseX, mouseY);
  }
});

canvas.addEventListener("mousemove", (e) => {
  if (!isDrawing) return;
  const rect = canvas.getBoundingClientRect();
  const mouseX = e.clientX - rect.left;
  const mouseY = e.clientY - rect.top;
  line.graphics.lineTo(mouseX, mouseY);
  stage.update();
});

canvas.addEventListener("mouseup", () => {
  isDrawing = false;
  line.graphics.endStroke();
  stage.update();
});



// タイマー
function startTimer(duration, display) {
  var timer = duration, minutes, seconds;
  setInterval(function () {
      minutes = parseInt(timer / 60, 10);
      seconds = parseInt(timer % 60, 10);

      minutes = minutes < 10 ? "0" + minutes : minutes;
      seconds = seconds < 10 ? "0" + seconds : seconds;

      display.textContent = minutes + ":" + seconds;

      if (--timer < 0) { // タイマーが0になったら内容の保存＆リダイレクト
        saveCanvas();
        window.location.href = '/result';
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