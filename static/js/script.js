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

const lineWidthInput = document.getElementById("lineWidth");
const lineOpacityInput = document.getElementById("lineOpacity");

const line = new createjs.Shape();
stage.addChild(line);
stage.update();

// 初期の太さ
let lineWidth = parseInt(lineWidthInput.value);
let lineOpacity = parseFloat(lineOpacityInput.value);

// スライダーの値表示を更新する関数
function updateSliderValue(slider, valueDisplay, isOpacity = false) {
  const value = slider.value;
  if (isOpacity) {
    valueDisplay.textContent = `${Math.round(value * 100)}%`;
  } else {
    valueDisplay.textContent = value;
  }
}

// 線の太さスライダー
const lineWidthValue = document.getElementById("lineWidth-value");
lineWidthInput.addEventListener("input", () => {
  lineWidth = parseInt(lineWidthInput.value);
  updateSliderValue(lineWidthInput, lineWidthValue);
});

// 透明度スライダー
const lineOpacityValue = document.getElementById("lineOpacity-value");
lineOpacityInput.addEventListener("input", () => {
  lineOpacity = parseFloat(lineOpacityInput.value);
  updateSliderValue(lineOpacityInput, lineOpacityValue, true);
});

// 初期値を設定
updateSliderValue(lineWidthInput, lineWidthValue);
updateSliderValue(lineOpacityInput, lineOpacityValue, true);

let isDrawing = false;
let isEraserActive = false;

// ペンボタンの初期状態をactiveに
const penButton = document.getElementById("pen");
penButton.classList.add("active");

// ペンボタンのクリックイベント
penButton.addEventListener("click", () => {
  if (isEraserActive) {
    isEraserActive = false;
    eraserButton.classList.remove("active");
    penButton.classList.add("active");
  }
});

// 消しゴムボタンのクリックイベント
const eraserButton = document.getElementById("eraser");
eraserButton.addEventListener("click", () => {
  if (!isEraserActive) {
    isEraserActive = true;
    penButton.classList.remove("active");
    eraserButton.classList.add("active");
  }
});

// クリアボタンのクリックイベント
const clearButton = document.getElementById("reset");
clearButton.addEventListener("click", () => {
  var result = confirm("リセットしてもよろしいですか？"); // 確認ダイアログ
  if(result == true){
    line.graphics.clear();
    stage.update();
  }
});

// 描画開始時
function startDrawing(e) {
  isDrawing = true;
  const rect = canvas.getBoundingClientRect();
  const mouseX = (e.clientX || e.touches[0]?.clientX || e.pointerX) - rect.left;
  const mouseY = (e.clientY || e.touches[0]?.clientY || e.pointerY) - rect.top;

  // 入力の種類（マウス、ペン、タッチ）を判定
  const isMouse = e.pointerType === 'mouse';
  const isPen = e.pointerType === 'pen';

  // マウス入力時は圧力感知を無効化
  const pressure = isMouse ? 1 : (e.pressure || 1); // マウスの場合は圧力を1に、ペンの場合は圧力を使用

  const adjustedLineWidth = lineWidth * pressure;
  const adjustedOpacity = lineOpacity * pressure;

  if (isEraserActive) {
    // 消しゴムの設定
    line.graphics.setStrokeStyle(adjustedLineWidth, 1, "round").beginStroke("white").moveTo(mouseX, mouseY);
  } else {
    // 通常のペン設定
    const paintColorHex = document.querySelector("#inputColor").value;
    const paintColorRGB = parseInt(paintColorHex.slice(1), 16); // 色を16進数からRGBに変換

    line.graphics
      .setStrokeStyle(adjustedLineWidth, 1, "round")
      .beginStroke(createjs.Graphics.getRGB(paintColorRGB, adjustedOpacity))
      .moveTo(mouseX, mouseY)
      .lineTo(mouseX, mouseY);
  }
}

// 描画中
function moveDrawing(e) {
  if (!isDrawing) return;
  const rect = canvas.getBoundingClientRect();
  const mouseX = (e.clientX || e.touches[0]?.clientX || e.pointerX) - rect.left;
  const mouseY = (e.clientY || e.touches[0]?.clientY || e.pointerY) - rect.top;

  // 入力の種類（マウス、ペン、タッチ）を判定
  const isMouse = e.pointerType === 'mouse';
  const isPen = e.pointerType === 'pen';

  // マウス入力時は圧力感知を無効化
  const pressure = isMouse ? 1 : (e.pressure || 1); // マウスの場合は圧力を1に、ペンの場合は圧力を使用

  const adjustedLineWidth = lineWidth * pressure;
  const adjustedOpacity = lineOpacity * pressure;

  line.graphics.setStrokeStyle(adjustedLineWidth, 1, "round");
  line.graphics.lineTo(mouseX, mouseY);
  stage.update();
}

// タッチイベントを修正
canvas.addEventListener("pointerdown", startDrawing);
canvas.addEventListener("pointermove", moveDrawing);
canvas.addEventListener("pointerup", endDrawing);

canvas.addEventListener("mousedown", startDrawing);
canvas.addEventListener("mousemove", moveDrawing);
canvas.addEventListener("mouseup", endDrawing);

canvas.addEventListener("touchstart", startDrawing);
canvas.addEventListener("touchmove", moveDrawing);
canvas.addEventListener("touchend", endDrawing);

// マウスアップおよびタッチエンドイベント
function endDrawing() {
  isDrawing = false;
  line.graphics.endStroke();
  stage.update();
}

// タイマー
function startTimer(duration, display) {
  var timer = duration, minutes, seconds;
  setInterval(function () {

      // 経過時間の計算
      var elapsed = duration - timer;

      minutes = parseInt(timer / 60, 10);
      seconds = parseInt(timer % 60, 10);

      minutes = minutes < 10 ? "0" + minutes : minutes;
      seconds = seconds < 10 ? "0" + seconds : seconds;

      display.textContent = minutes + ":" + seconds;

      // 経過時間をローカルストレージに保存
      localStorage.setItem('elapsedTime', elapsed);

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
