let loginForm = document.getElementById('loginForm');
let userName = document.getElementById('userName');
let password = document.getElementById('password');

// エラーメッセージ表示要素を取得
let errorMessageRequired = document.getElementsByClassName('errorMessageRequired');

// ユーザーネームの正規表現
const userNameRegex = /^[a-zA-Z0-9_]{2,}$/; // 半角英数字とアンダーバーを2文字以上

// フォーム送信時にチェックする処理
loginForm.addEventListener('submit', function (event) {
    // 各フィールドが未入力ならエラーメッセージを表示
    let hasError = false;

    // ユーザーネームのチェック
    if (userName.value.length === 0) {
        errorMessageRequired[0].innerHTML = "必須";
        hasError = true;
    }
    // ユーザー名が1文字以上、かつ1文字目が正規表現に従っていない場合
    else if (userName.value.length >= 1 && !/^[a-zA-Z0-9_]/.test(userName.value[0])) {
        errorMessageRequired[0].innerHTML = "半角英数字または半角アンダーバーで始めてください。";
        hasError = true;
    }
    // ユーザー名が2文字以上で、かつ正規表現に従っていない場合（全体に対してチェック）
    else if (userName.value.length >= 2 && !userNameRegex.test(userName.value)) {
        errorMessageRequired[0].innerHTML = "半角英数字と半角アンダーバーのみで入力してください。";
        hasError = true;
    }
    else {
        errorMessageRequired[0].innerHTML = "";
    }

    // パスワードのチェック
    if (password.value.length === 0) {
        errorMessageRequired[1].innerHTML = "必須";
        hasError = true;
    } else {
        // パスワードが6文字以上、15文字以内
        if (password.value.length < 6) {
            errorMessageRequired[1].innerHTML = "6文字以上で入力してください。";
            hasError = true;
        } else if (password.value.length > 15) {
            errorMessageRequired[1].innerHTML = "15文字以内で入力してください。";
            hasError = true;
        } else {
            errorMessageRequired[1].innerHTML = ""; // エラーメッセージをクリア
        }
    }

    // エラーがあればフォーム送信を防ぐ
    if (hasError) {
        event.preventDefault(); // フォーム送信を防ぐ
    }
});
