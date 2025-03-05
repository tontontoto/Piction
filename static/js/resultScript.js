window.onload = function () {
  const canvas = document.getElementById("myCanvas");
  const context = canvas.getContext("2d");

  // ローカルストレージから保存されたデータを取得
  const dataURL = localStorage.getItem("canvasImage");
  const canvasWidth = localStorage.getItem("canvasWidth");
  const canvasHeight = localStorage.getItem("canvasHeight");
  console.log(canvasWidth, canvasHeight);
  
  if (dataURL) {
    const img = new Image();
    img.onload = function () {
      // 画像を描画する前にキャンバスサイズを復元
      canvas.width = canvasWidth || canvas.width;  // 幅が保存されていない場合はそのまま
      canvas.height = canvasHeight || canvas.height; // 高さが保存されていない場合はそのまま
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

document.addEventListener("DOMContentLoaded", function () {
  const oneWeekSelect = document.getElementById("one_week");
  const timesSelect = document.getElementById("times");

  // **日付リストを作成する関数**
  function generateDateList() {
      const now = new Date();
      let dateList = [];

      for (let i = 0; i < 7; i++) {
          let futureDate = new Date();
          futureDate.setDate(now.getDate() + i);

          let month = futureDate.getMonth() + 1;
          let day = futureDate.getDate();
          let dayOfWeek = futureDate.toLocaleDateString('ja-JP', { weekday: 'short' });

          let formattedDate = `${month}月${day}日 (${dayOfWeek})`;
          dateList.push({ value: formattedDate, formattedDate }); 
      }

      oneWeekSelect.innerHTML = "";
      dateList.forEach(item => {
          const option = document.createElement("option");
          option.value = item.value;  // "3月4日 (月)" 形式で送信
          option.textContent = item.formattedDate;
          oneWeekSelect.appendChild(option);
      });

      // 初回の時間リスト更新（デフォルト: 今日の時間）
      generateTimeList(dateList[0].value);
  }

  // **時間リストを作成する関数**
  function generateTimeList(selectedDate) {
      const now = new Date();
      let timeList = [];
      let startHour = selectedDate === oneWeekSelect.options[0].value ? now.getHours() + 1 : 0; 

      for (let hour = startHour; hour < 24; hour++) {
          let timeRange = `${hour}時～${hour + 1}時`;
          timeList.push(timeRange);
      }

      timesSelect.innerHTML = "";
      timeList.forEach((time) => {
          const option = document.createElement("option");
          option.value = time; // 直接 "10時～11時" を value に
          option.textContent = time;
          timesSelect.appendChild(option);
      });
  }

  // **日付が変更されたら時間リストを更新**
  oneWeekSelect.addEventListener("change", function () {
      generateTimeList(this.value);
  });

  generateDateList();
});




// このクラスはコピペだからわけわかんねえっす
// ComboboxAutocompleteクラスはコンボボックスのオートコンプリート機能を処理します
class ComboboxAutocomplete {
  constructor(comboboxNode, buttonNode, listboxNode) {
    this.comboboxNode = comboboxNode;
    this.buttonNode = buttonNode;
    this.listboxNode = listboxNode;

    this.comboboxHasVisualFocus = false;
    this.listboxHasVisualFocus = false;

    this.hasHover = false;

    this.isNone = false;
    this.isList = false;
    this.isBoth = false;

    this.allOptions = [];

    this.option = null;
    this.firstOption = null;
    this.lastOption = null;

    this.filteredOptions = [];
    this.filter = '';

    var autocomplete = this.comboboxNode.getAttribute('aria-autocomplete');

    if (typeof autocomplete === 'string') {
      autocomplete = autocomplete.toLowerCase();
      this.isNone = autocomplete === 'none';
      this.isList = autocomplete === 'list';
      this.isBoth = autocomplete === 'both';
    } else {
      // デフォルトのautocomplete値
      this.isNone = true;
    }

    this.comboboxNode.addEventListener(
      'keydown',
      this.onComboboxKeyDown.bind(this)
    );
    this.comboboxNode.addEventListener(
      'keyup',
      this.onComboboxKeyUp.bind(this)
    );
    this.comboboxNode.addEventListener(
      'click',
      this.onComboboxClick.bind(this)
    );
    this.comboboxNode.addEventListener(
      'focus',
      this.onComboboxFocus.bind(this)
    );
    this.comboboxNode.addEventListener('blur', this.onComboboxBlur.bind(this));

    document.body.addEventListener(
      'pointerup',
      this.onBackgroundPointerUp.bind(this),
      true
    );

    this.listboxNode.addEventListener(
      'pointerover',
      this.onListboxPointerover.bind(this)
    );
    this.listboxNode.addEventListener(
      'pointerout',
      this.onListboxPointerout.bind(this)
    );

    var nodes = this.listboxNode.getElementsByTagName('LI');

    //MARK: リストのクリックイベントの監視
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      this.allOptions.push(node);

      node.addEventListener('click', this.onOptionClick.bind(this));
      node.addEventListener('pointerover', this.onOptionPointerover.bind(this));
      node.addEventListener('pointerout', this.onOptionPointerout.bind(this));
    }

    this.filterOptions();

    var button = this.comboboxNode.nextElementSibling;

    if (button && button.tagName === 'BUTTON') {
      button.addEventListener('click', this.onButtonClick.bind(this));
    }
  }

  // ノードのテキストコンテンツを小文字で取得
  getLowercaseContent(node) {
    return node.textContent.toLowerCase();
  }

  // オプションが表示領域内にあるか確認
  isOptionInView(option) {
    var bounding = option.getBoundingClientRect();
    return (
      bounding.top >= 0 &&
      bounding.left >= 0 &&
      bounding.bottom <=
        (window.innerHeight || document.documentElement.clientHeight) &&
      bounding.right <=
        (window.innerWidth || document.documentElement.clientWidth)
    );
  }

  setActiveDescendant(option) {
    if (option && this.listboxHasVisualFocus) {
      this.comboboxNode.setAttribute('aria-activedescendant', option.id);
      if (!this.isOptionInView(option)) {
        option.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    } else {
      this.comboboxNode.setAttribute('aria-activedescendant', '');
    }
  }

  // 値を設定
  setValue(value) {
    this.filter = value;
    this.comboboxNode.value = this.filter;
    this.comboboxNode.setSelectionRange(this.filter.length, this.filter.length);
    this.filterOptions();
  }

  // オプションを設定
  setOption(option, flag) {
    if (typeof flag !== 'boolean') {
      flag = false;
    }

    if (option) {
      this.option = option;
      this.setCurrentOptionStyle(this.option);
      this.setActiveDescendant(this.option);

      if (this.isBoth) {
        this.comboboxNode.value = this.option.textContent;
        if (flag) {
          this.comboboxNode.setSelectionRange(
            this.option.textContent.length,
            this.option.textContent.length
          );
        } else {
          this.comboboxNode.setSelectionRange(
            this.filter.length,
            this.option.textContent.length
          );
        }
      }
    }
  }

  // コンボボックスに視覚的フォーカスを設定
  setVisualFocusCombobox() {
    this.listboxNode.classList.remove('focus');
    this.comboboxNode.parentNode.classList.add('focus'); // 親にフォーカスクラスを設定してスタイリングを簡単に
    this.comboboxHasVisualFocus = true;
    this.listboxHasVisualFocus = false;
    this.setActiveDescendant(false);
  }

  // リストボックスに視覚的フォーカスを設定
  setVisualFocusListbox() {
    this.comboboxNode.parentNode.classList.remove('focus');
    this.comboboxHasVisualFocus = false;
    this.listboxHasVisualFocus = true;
    this.listboxNode.classList.add('focus');
    this.setActiveDescendant(this.option);
  }

  // すべての視覚的フォーカスを削除
  removeVisualFocusAll() {
    this.comboboxNode.parentNode.classList.remove('focus');
    this.comboboxHasVisualFocus = false;
    this.listboxHasVisualFocus = false;
    this.listboxNode.classList.remove('focus');
    this.option = null;
    this.setActiveDescendant(false);
  }

  // オプションをフィルタリング
  filterOptions() {
    // autocompleteがnoneの場合はオプションをフィルタリングしない
    if (this.isNone) {
      this.filter = '';
    }

    var option = null;
    var currentOption = this.option;
    var filter = this.filter.toLowerCase();

    this.filteredOptions = [];
    this.listboxNode.innerHTML = '';

    for (var i = 0; i < this.allOptions.length; i++) {
      option = this.allOptions[i];
      if (
        filter.length === 0 ||
        this.getLowercaseContent(option).indexOf(filter) === 0
      ) {
        this.filteredOptions.push(option);
        this.listboxNode.appendChild(option);
      }
    }

    // フィルタリングされたオプション配列を使用してfirstOptionとlastOptionを初期化
    var numItems = this.filteredOptions.length;
    if (numItems > 0) {
      this.firstOption = this.filteredOptions[0];
      this.lastOption = this.filteredOptions[numItems - 1];

      if (currentOption && this.filteredOptions.indexOf(currentOption) >= 0) {
        option = currentOption;
      } else {
        option = this.firstOption;
      }
    } else {
      this.firstOption = null;
      option = null;
      this.lastOption = null;
    }

    return option;
  }

  // 現在のオプションのスタイルを設定
  setCurrentOptionStyle(option) {
    for (var i = 0; i < this.filteredOptions.length; i++) {
      var opt = this.filteredOptions[i];
      if (opt === option) {
        opt.setAttribute('aria-selected', 'true');
        if (
          this.listboxNode.scrollTop + this.listboxNode.offsetHeight <
          opt.offsetTop + opt.offsetHeight
        ) {
          this.listboxNode.scrollTop =
            opt.offsetTop + opt.offsetHeight - this.listboxNode.offsetHeight;
        } else if (this.listboxNode.scrollTop > opt.offsetTop + 2) {
          this.listboxNode.scrollTop = opt.offsetTop;
        }
      } else {
        opt.removeAttribute('aria-selected');
      }
    }
  }

  // 前のオプションを取得
  getPreviousOption(currentOption) {
    if (currentOption !== this.firstOption) {
      var index = this.filteredOptions.indexOf(currentOption);
      return this.filteredOptions[index - 1];
    }
    return this.lastOption;
  }

  // 次のオプションを取得
  getNextOption(currentOption) {
    if (currentOption !== this.lastOption) {
      var index = this.filteredOptions.indexOf(currentOption);
      return this.filteredOptions[index + 1];
    }
    return this.firstOption;
  }

  // オプションがフォーカスを持っているか確認
  doesOptionHaveFocus() {
    return this.comboboxNode.getAttribute('aria-activedescendant') !== '';
  }

  // リストボックスが開いているか確認
  isOpen() {
    return this.listboxNode.style.display === 'block';
  }

  // リストボックスが閉じているか確認
  isClosed() {
    return this.listboxNode.style.display !== 'block';
  }

  // オプションが存在するか確認
  hasOptions() {
    return this.filteredOptions.length;
  }

  // リストボックスを開く
  open() {
    this.listboxNode.style.display = 'block';
    this.comboboxNode.setAttribute('aria-expanded', 'true');
    this.buttonNode.setAttribute('aria-expanded', 'true');
  }

  // リストボックスを閉じる
  close(force) {
    if (typeof force !== 'boolean') {
      force = false;
    }

    if (
      force ||
      (!this.comboboxHasVisualFocus &&
        !this.listboxHasVisualFocus &&
        !this.hasHover)
    ) {
      this.setCurrentOptionStyle(false);
      this.listboxNode.style.display = 'none';
      this.comboboxNode.setAttribute('aria-expanded', 'false');
      this.buttonNode.setAttribute('aria-expanded', 'false');
      this.setActiveDescendant(false);
      this.comboboxNode.parentNode.classList.add('focus');
    }
  }

  // コンボボックスのkeydownイベントハンドラ
  onComboboxKeyDown(event) {
    var flag = false,
      altKey = event.altKey;

    if (event.ctrlKey || event.shiftKey) {
      return;
    }

    switch (event.key) {
      case 'Enter':
        if (this.listboxHasVisualFocus) {
          this.setValue(this.option.textContent);
        }
        this.close(true);
        this.setVisualFocusCombobox();
        flag = true;
        break;

      case 'Down':
      case 'ArrowDown':
        if (this.filteredOptions.length > 0) {
          if (altKey) {
            this.open();
          } else {
            this.open();
            if (
              this.listboxHasVisualFocus ||
              (this.isBoth && this.filteredOptions.length > 1)
            ) {
              this.setOption(this.getNextOption(this.option), true);
              this.setVisualFocusListbox();
            } else {
              this.setOption(this.firstOption, true);
              this.setVisualFocusListbox();
            }
          }
        }
        flag = true;
        break;

      case 'Up':
      case 'ArrowUp':
        if (this.hasOptions()) {
          if (this.listboxHasVisualFocus) {
            this.setOption(this.getPreviousOption(this.option), true);
          } else {
            this.open();
            if (!altKey) {
              this.setOption(this.lastOption, true);
              this.setVisualFocusListbox();
            }
          }
        }
        flag = true;
        break;

      case 'Esc':
      case 'Escape':
        if (this.isOpen()) {
          this.close(true);
          this.filter = this.comboboxNode.value;
          this.filterOptions();
          this.setVisualFocusCombobox();
        } else {
          this.setValue('');
          this.comboboxNode.value = '';
        }
        this.option = null;
        flag = true;
        break;

      case 'Tab':
        this.close(true);
        if (this.listboxHasVisualFocus) {
          if (this.option) {
            this.setValue(this.option.textContent);
          }
        }
        break;

      case 'Home':
        this.comboboxNode.setSelectionRange(0, 0);
        flag = true;
        break;

      case 'End':
        var length = this.comboboxNode.value.length;
        this.comboboxNode.setSelectionRange(length, length);
        flag = true;
        break;

      default:
        break;
    }

    if (flag) {
      event.stopPropagation();
      event.preventDefault();
    }
  }

  // 文字が印刷可能か確認
  isPrintableCharacter(str) {
    return str.length === 1 && str.match(/\S| /);
  }

  // コンボボックスのkeyupイベントハンドラ
  onComboboxKeyUp(event) {
    var flag = false,
      option = null,
      char = event.key;

    if (this.isPrintableCharacter(char)) {
      this.filter += char;
    }

    if (this.comboboxNode.value.length < this.filter.length) {
      this.filter = this.comboboxNode.value;
      this.option = null;
      this.filterOptions();
    }

    if (event.key === 'Escape' || event.key === 'Esc') {
      return;
    }

    switch (event.key) {
      case 'Backspace':
        this.setVisualFocusCombobox();
        this.setCurrentOptionStyle(false);
        this.filter = this.comboboxNode.value;
        this.option = null;
        this.filterOptions();
        flag = true;
        break;

      case 'Left':
      case 'ArrowLeft':
      case 'Right':
      case 'ArrowRight':
      case 'Home':
      case 'End':
        if (this.isBoth) {
          this.filter = this.comboboxNode.value;
        } else {
          this.option = null;
          this.setCurrentOptionStyle(false);
        }
        this.setVisualFocusCombobox();
        flag = true;
        break;

      default:
        if (this.isPrintableCharacter(char)) {
          this.setVisualFocusCombobox();
          this.setCurrentOptionStyle(false);
          flag = true;

          if (this.isList || this.isBoth) {
            option = this.filterOptions();
            if (option) {
              if (this.isClosed() && this.comboboxNode.value.length) {
                this.open();
              }

              if (
                this.getLowercaseContent(option).indexOf(
                  this.comboboxNode.value.toLowerCase()
                ) === 0
              ) {
                this.option = option;
                if (this.isBoth || this.listboxHasVisualFocus) {
                  this.setCurrentOptionStyle(option);
                  if (this.isBoth) {
                    this.setOption(option);
                  }
                }
              } else {
                this.option = null;
                this.setCurrentOptionStyle(false);
              }
            } else {
              this.close();
              this.option = null;
              this.setActiveDescendant(false);
            }
          } else if (this.comboboxNode.value.length) {
            this.open();
          }
        }

        break;
    }

    if (flag) {
      event.stopPropagation();
      event.preventDefault();
    }
  }

  // コンボボックスのクリックイベントハンドラ
  onComboboxClick() {
    if (this.isOpen()) {
      this.close(true);
    } else {
      this.open();
    }
  }

  // コンボボックスのフォーカスイベントハンドラ
  onComboboxFocus() {
    this.filter = this.comboboxNode.value;
    this.filterOptions();
    this.setVisualFocusCombobox();
    this.option = null;
    this.setCurrentOptionStyle(null);
  }

  // コンボボックスのブラーイベントハンドラ
  onComboboxBlur() {
    this.removeVisualFocusAll();
  }

  // 背景のpointerupイベントハンドラ
  onBackgroundPointerUp(event) {
    if (
      !this.comboboxNode.contains(event.target) &&
      !this.listboxNode.contains(event.target) &&
      !this.buttonNode.contains(event.target)
    ) {
      this.comboboxHasVisualFocus = false;
      this.setCurrentOptionStyle(null);
      this.removeVisualFocusAll();
      setTimeout(this.close.bind(this, true), 300);
    }
  }

  // ボタンのクリックイベントハンドラ
  onButtonClick() {
    if (this.isOpen()) {
      this.close(true);
    } else {
      this.open();
    }
    this.comboboxNode.focus();
    this.setVisualFocusCombobox();
  }

  // リストボックスのpointeroverイベントハンドラ
  onListboxPointerover() {
    this.hasHover = true;
  }

  // リストボックスのpointeroutイベントハンドラ
  onListboxPointerout() {
    this.hasHover = false;
    setTimeout(this.close.bind(this, false), 300);
  }

  //MARK: オプションのクリックイベントハンドラ
  onOptionClick(event) {
    this.comboboxNode.value = event.target.textContent;
    this.close(true);
    return this.comboboxNode.value;
  }

  // オプションのpointeroverイベントハンドラ
  onOptionPointerover() {
    this.hasHover = true;
    this.open();
  }

  // オプションのpointeroutイベントハンドラ
  onOptionPointerout() {
    this.hasHover = false;
    setTimeout(this.close.bind(this, false), 300);
  }
}

// ページのロード時にComboboxAutocompleteを初期化
window.addEventListener('load', function () {
  var comboboxes = document.querySelectorAll('.combobox-list');

  for (var i = 0; i < comboboxes.length; i++) {
    var combobox = comboboxes[i];
    var comboboxNode = combobox.querySelector('input');
    var buttonNode = combobox.querySelector('button');
    var listboxNode = combobox.querySelector('[role="listbox"]');
    new ComboboxAutocomplete(comboboxNode, buttonNode, listboxNode);
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
    const title = document.getElementById("title").value;
    const postingDate = document.getElementById("one_week").value; // 例: "3月4日 (月)"
    const postingTime = document.getElementById("times").value;   // 例: "10時～11時"
    const dataURL = localStorage.getItem("canvasImage");
    const time = localStorage.getItem("elapsedTime");
    const price = localStorage.getItem("moneyValue");
    const kategoriSelectValue = document.getElementById("kategori").value;

    if (!title || !postingDate || !postingTime || !dataURL || !price) {
        alert("必要な情報が足りません。全ての項目を入力してください。");
        return;
    }

    fetch("/add_sale", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            title,
            postingDate,  // "3月4日 (月)"
            postingTime,  // "10時～11時"
            image: dataURL,
            time,
            price,
            kategori: kategoriSelectValue
        }),
    })
    .then((response) => {
        if (response.ok) {
            alert("正常に保存されました。");
        } else {
            return response.json().then(data => { throw new Error(data.error || "保存に失敗しました。"); });
        }
    })
    .catch((error) => {
        console.error("送信エラー:", error);
        alert("保存に失敗しました: " + error.message);
    });
});


// kategoriセレクトボックスを取得
const kategoriSelect = document.getElementById('kategori');
// 'change' イベントをリスン
kategoriSelect.addEventListener('change', () => {
    const selectedCategoryId = kategoriSelect.value; // 選択されたcategoryIdを取得

    if (selectedCategoryId) {
        // バックエンドに送信する処理
        fetch("/get_category_name", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ categoryId: selectedCategoryId }),
        })
        .then(response => response.json())
        .then(data => {
            // サーバーから返されたカテゴリ名を表示
            console.log("カテゴリ名:", data.categoryName);
        })
        .catch(error => console.log("カテゴリ名の取得エラー:", error));
    }
});