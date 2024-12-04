let signupForm = document.getElementById('signupForm');

// 各フォームフィールドの値を取得
let userName = document.getElementById('userName');
let displayName = document.getElementById('displayName');
let mailAddress = document.getElementById('mailAddress');
let password = document.getElementById('password');
const checkBoxCheck = document.getElementById('privacyPolicy');


// エラーメッセージ表示要素を取得
let errorMessageRequired = document.getElementsByClassName('errorMessageRequired');


// 各項目正規表現
let userNameRegex = /^[a-zA-Z0-9_]{2,15}$/
let emailRegex = /^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*@([a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9]\.)+[a-zA-Z]{2,}$/;
let passwordRegex = /^[a-zA-Z0-9_]{6,15}$/;

// フォーム送信時にチェックする処理
signupForm.addEventListener('submit', function (event) {
    // 各フィールドが未入力ならエラーメッセージを表示
    let hasError = false;

    // ユーザーネームのチェック 
    if (userName.value.length === 0) {
        errorMessageRequired[0].innerHTML = "必須";
        hasError = true;
    } else {
        errorMessageRequired[0].innerHTML = "";
    }

    // 表示名のチェック 
    if (displayName.value.length === 0) {
        errorMessageRequired[1].innerHTML = "必須";
        hasError = true;
    } else {
        errorMessageRequired[1].innerHTML = "";
    }

    // メールアドレスのチェック
    if (mailAddress.value.length === 0) {
        errorMessageRequired[2].innerHTML = "必須";
        hasError = true;
    } else {
        errorMessageRequired[2].innerHTML = "";
    }
    // 有効メールアドレス制限
    if (!emailRegex.test(mailAddress.value)) {
        errorMessageRequired[2].innerHTML = "有効なメールアドレスを入力してください。";
    } else {
        errorMessageRequired[2].innerHTML = "";
    }
    console.log(mailAddress.value);
    console.log(emailRegex.test(mailAddress.value));

    // パスワードのチェック 
    if (password.value.length === 0) {
        errorMessageRequired[3].innerHTML = "必須";
        hasError = true;
    } else {
        if (password.value.Length < 6) {
            errorMessageRequired[3].innerHTML = "6文字以上で入力してください。";
            hasError = true;
        } else if (password.value.Length > 15) {
            errorMessageRequired[3].innerHTML = "15文字以内で入力してください。";
            hasError = true;
        }
    }
    if (!checkBoxCheck.checked) {
        console.log("not checked")
        errorMessageRequired[4].innerHTML = "利用規約に同意する必要があります。";
    } else {
        errorMessageRequired[4].innerHTML = "";
    }
    
    // エラーがあればフォーム送信を防ぐ
    if (hasError) {
        console.log("submit stop.")
        event.preventDefault(); // フォーム送信を防ぐ
    }
});


// リアルタイム入力時ので条件に当てはまっているかの処理--------------------------------
// ユーザーネーム文字制限
userName.addEventListener('input', function () {
    // ユーザー名が0文字の場合はエラーメッセージを表示しない
    if (userName.value.length === 0) {
        errorMessageRequired[0].innerHTML = "";
    }
    // ユーザー名が1文字以上、かつ1文字目が正規表現に従っていない場合
    else if (userName.value.length >= 1 && !/^[a-zA-Z0-9_]/.test(userName.value[0])) {
        errorMessageRequired[0].innerHTML = "半角英数字または半角アンダーバーで始めてください。";
    }
    // ユーザー名が2文字以上で、かつ正規表現に従っていない場合（全体に対してチェック）
    else if (userName.value.length >= 2 && !userNameRegex.test(userName.value)) {
        errorMessageRequired[0].innerHTML = "半角英数字と半角アンダーバーのみで入力してください。";
    }
    // ユーザー名が正規表現に従っている場合
    else {
        errorMessageRequired[0].innerHTML = "";
    }
})

// 表示名count、制限以上のinputエラーメッセージ
displayName.addEventListener('input', function () {
    const displayNameValue = this.value.trim();
    const displayNameLength = displayNameValue.length;
    const countArea = document.getElementById('displayNameCount')
    countArea.innerText = displayNameLength;
    if (displayNameLength > 30) {
        console.log("30文字以上です。")
        errorMessageRequired[1].innerHTML = "30文字以内で入力してください。";
        countArea.style.color = "red";
    } else {
        errorMessageRequired[1].innerHTML = "";
        countArea.style.color = "black";
    }
})

// password
password.addEventListener('input', function () {
    const passwordValue = this.value.trim();
    if (passwordRegex.test(passwordValue)) {
        console.log("半角英数のみ");
    }
})
password.addEventListener('blur', function () {
    const passwordValue = this.value.trim();
    const passwordLength = passwordValue.length;

    if (passwordLength < 6) {
        errorMessageRequired[3].innerHTML = "6文字以上で入力してください。";
    } else if (passwordLength > 15) {
        errorMessageRequired[3].innerHTML = "15文字以内で入力してください。";
    } else {
        errorMessageRequired[3].innerHTML = "";
    }
});



// パスワード入力欄のパスワード表示非表示機能
function pushHideButton() {
    let password = document.getElementById("password");
    let buttonEye = document.getElementById("buttonEye");
    if (password.type === "text") {
        password.type = "password";
        buttonEye.className = "fa fa-eye-slash";
    } else {
        password.type = "text";
        buttonEye.className = "fa fa-eye";
    }
}

