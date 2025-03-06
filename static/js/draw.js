const canvas = document.getElementById("myCanvas");
const stage = new createjs.Stage(canvas);

// 関数を作成して、canvasのサイズを画面サイズに合わせる
function resizeCanvas() {
  const width = window.innerWidth;
  const height = window.innerHeight;

  // 幅と高さがどちらも570px以上の場合でも正方形を維持
  const size = Math.min(width, height, 570); // 570px以下でも正方形を保つ

  // 画面サイズに合わせてcanvasのサイズを変更
  canvas.width = size;
  canvas.height = size;
  canvas.style.width = `${size}px`; // 見た目のサイズ
  canvas.style.height = `${size}px`; // 見た目のサイズ

  stage.update();
}

// 初期化時にサイズを調整
resizeCanvas();

// 画面サイズが変更されたときにもサイズを調整
window.addEventListener("resize", resizeCanvas);

// 背景を描画する関数
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

// 色履歴を表示する関数
function loadColorHistory() {
  const colorHistory = JSON.parse(localStorage.getItem('colorHistory')) || [];
  const colorList = document.getElementById('colorList');
  
  // 既存の色リストをクリア
  colorList.innerHTML = '';

  // 色履歴を表示
  colorHistory.forEach(color => {
      const colorItem = document.createElement('li');
      colorItem.style.backgroundColor = color;
      colorItem.textContent = color; // カラーコードを表示
      colorItem.addEventListener('click', () => {
        // クリックした色をペンの色として選択
        document.getElementById('inputColor').value = color;
      });
      colorList.appendChild(colorItem);
  });
}

// 色選択ボックスの変更イベント
const colorInput = document.getElementById('inputColor');
colorInput.addEventListener('change', (event) => {
  const selectedColor = event.target.value;

  // 色履歴に保存
  let colorHistory = JSON.parse(localStorage.getItem('colorHistory')) || [];

  // 色が履歴にない場合、最大3色まで追加
  if (!colorHistory.includes(selectedColor)) {
      colorHistory.unshift(selectedColor); // 新しい色を先頭に追加
      if (colorHistory.length > 3) {
          colorHistory = colorHistory.slice(0, 3); // 最新3色だけ保持
      }
      localStorage.setItem('colorHistory', JSON.stringify(colorHistory));
  }

  loadColorHistory(); // 色履歴を再表示
});

// 初期化時に色履歴を読み込む
loadColorHistory();

// タッチスタートおよびタッチエンド時にスクロールを無効にする
canvas.addEventListener('touchstart', (e) => {
  e.preventDefault(); // スクロールを無効にする
}, { passive: false });

canvas.addEventListener('touchend', (e) => {
  e.preventDefault(); // スクロールを無効にする
}, { passive: false });

// クリアボタンのクリックイベント
const clearButton = document.getElementById("reset");
clearButton.addEventListener("click", () => {
  var result = confirm("リセットしてもよろしいですか？"); // 確認ダイアログ
  if(result == true){
    line.graphics.clear();
    stage.update();
  }
});

// マウスダウンおよびタッチスタートイベント
function startDrawing(e) {
  document.body.style.overflow = 'hidden';

  isDrawing = true;
  const rect = canvas.getBoundingClientRect();
  const mouseX = (e.clientX || e.touches[0].clientX) - rect.left;
  const mouseY = (e.clientY || e.touches[0].clientY) - rect.top;

  if (isEraserActive) {
    // 消しゴムの設定
    line.graphics.setStrokeStyle(lineWidth, 1, "round").beginStroke("white").moveTo(mouseX, mouseY);
  } else {
    // 通常のペン設定
    const paintColorHex = document.querySelector("#inputColor").value;

    // 色を16進数から10進数のRGBに変換
    const paintColorRGB = parseInt(paintColorHex.slice(1), 16); // #を除去して数値に変換

    // 描画を始める時に色を履歴に追加
    let colorHistory = JSON.parse(localStorage.getItem('colorHistory')) || [];
    if (!colorHistory.includes(paintColorHex)) {
      colorHistory.unshift(paintColorHex); // 新しい色を履歴に追加
      if (colorHistory.length > 3) {
        colorHistory = colorHistory.slice(0, 3); // 最新3色まで保持
      }
      localStorage.setItem('colorHistory', JSON.stringify(colorHistory));
      loadColorHistory(); // 色履歴を再表示
    }

    line.graphics
      .setStrokeStyle(lineWidth, 1, "round")
      .beginStroke(createjs.Graphics.getRGB(paintColorRGB, lineOpacity))
      .moveTo(mouseX, mouseY)
      .lineTo(mouseX, mouseY);
  }
}

// マウスムーブおよびタッチムーブイベント
function moveDrawing(e) {
  if (!isDrawing) return;
  const rect = canvas.getBoundingClientRect();
  const mouseX = (e.clientX || e.touches[0].clientX) - rect.left;
  const mouseY = (e.clientY || e.touches[0].clientY) - rect.top;
  line.graphics.lineTo(mouseX, mouseY);
  stage.update();
}

// マウスアップおよびタッチエンドイベント
function endDrawing() {
  document.body.style.overflow = '';

  isDrawing = false;
  line.graphics.endStroke();
  stage.update();
}

// イベントリスナーを追加
canvas.addEventListener("mousedown", startDrawing);
canvas.addEventListener("mousemove", moveDrawing);
canvas.addEventListener("mouseup", endDrawing);

canvas.addEventListener("touchstart", startDrawing);
canvas.addEventListener("touchmove", moveDrawing);
canvas.addEventListener("touchend", endDrawing);

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
      console.log("time saved!")

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
  if (!canvas) {
    console.error("Canvas element not found");
    return;
  }

  try {
    // キャンバスの内容を直接DataURLとして保存
    const dataURL = canvas.toDataURL('image/png');
    localStorage.setItem('canvasImage', dataURL);
    
    // キャンバスの幅と高さも保存
    localStorage.setItem('canvasWidth', canvas.width.toString());
    localStorage.setItem('canvasHeight', canvas.height.toString());

    // タイマーと値段を保存
    var timerValue = document.querySelector('.timer p').textContent;
    localStorage.setItem('timerValue', timerValue);
    localStorage.setItem('moneyValue', money.toString());

    console.log("Canvas saved successfully");
    console.log("Dimensions:", canvas.width, canvas.height);
    console.log("DataURL length:", dataURL.length);
  } catch (error) {
    console.error("Error saving canvas:", error);
  }
}

// 自動保存を追加
setInterval(saveCanvas, 5000); // 5秒ごとに保存

//ボタンをクリックしたときに保存する
window.addEventListener('DOMContentLoaded', (event) => {
  const saveButton = document.getElementById('saveButton');
  if (saveButton) {
    saveButton.addEventListener('click', saveCanvas);
  }
});

// color-picker がクリックされたときに inputColor を起動
const colorPicker = document.querySelector('.color-picker');
const inputColor = document.getElementById('inputColor');

colorPicker.addEventListener('click', () => {
    inputColor.click(); // inputColor のクリックをトリガー
});
