// 必要事項を入力していなかった時の処理。
// ユーザーネーム、表示名、メールアドレス、パスワード、利用規約のチェックボックス

function validateForm(event) {
    // エラーメッセージ要素を取得
    let errorMessages = document.getElementsByClassName('errorMassage');

    // 各フォームフィールドの値を取得
    let userName = document.getElementById('userName').value;
    let displayName = document.getElementById('displayName').value;
    let mailAddress = document.getElementById('mailAddress').value;
    let password = document.getElementById('password').value;
    let checkBox = document.getElementById('privacyPolicy').checked; // チェックボックスの状態を取得

    // 各フィールドが未入力ならエラーメッセージを表示
    let hasError = false;

    // ユーザーネームのチェック
    if (userName === "") {
        errorMessages[0].style.display = "block";
        hasError = true;
    } else {
        errorMessages[0].style.display = "none";
    }

    // 表示名のチェック
    if (displayName === "") {
        errorMessages[1].style.display = "block";
        hasError = true;
    } else {
        errorMessages[1].style.display = "none";
    }

    // メールアドレスのチェック
    if (mailAddress === "") {
        errorMessages[2].style.display = "block";
        hasError = true;
    } else {
        errorMessages[2].style.display = "none";
    }

    // パスワードのチェック
    if (password === "") {
        errorMessages[3].style.display = "block";
        hasError = true;
    } else {
        errorMessages[3].style.display = "none";
    }

    // 利用規約チェックボックスのチェック状態を確認
    if (!checkBox) {
        errorMessages[4].style.display = "block";
        hasError = true;
    } else {
        errorMessages[4].style.display = "none";
    }

    // エラーがあればフォーム送信を防ぐ
    if (hasError) {
        event.preventDefault(); // フォーム送信を防ぐ
        return false; // エラーがある場合は送信しない
    }

    return true; // すべて正しい場合はフォームを送信
}
