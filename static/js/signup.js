// 必要事項を入力していなかった時の処理。
// ユーザーネーム、表示名、メールアドレス、パスワード、利用規約のチェックボックス
function validateForm(event) {
    // エラーメッセージ要素を取得
    let errorMessages = document.getElementsByClassName('errorMassage');

    // 各フォームフィールドの値を取得
    const userNameValue = document.getElementById('userName').value;
    const displayNameValue = document.getElementById('displayName').value;
    const mailAddressValue = document.getElementById('mailAddress').value;
    const passwordValue = document.getElementById('password').value;
    const checkBoxCheck = document.getElementById('privacyPolicy').checked; // チェックボックスの状態を取得
    const validEmailAddresError = document.getElementById('validEmailAddresError');
    // 各フィールドが未入力ならエラーメッセージを表示
    let hasError = false;

    // ユーザーネームのチェック
    let userNameRegex = /^[a-zA-Z0-9_]{1,15}$/
    if (!userNameRegex.test(userNameValue)) {
        errorMessages[0].style.display = "block";
        hasError = true;
    } else {
        errorMessages[0].style.display = "none";
    }

    // 表示名のチェック
    if (displayNameValue === "") {
        errorMessages[1].style.display = "block";
        hasError = true;
    } else {
        errorMessages[1].style.display = "none";
    }

    // メールアドレスのチェック
    if (mailAddressValue === "") {
        errorMessages[2].style.display = "block";
        hasError = true;
    } else {
        errorMessages[2].style.display = "none";
    }
    // 正規表現
    let emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    if (!emailRegex.test(mailAddressValue)) {
        // メールアドレスが無効な場合
        validEmailAddresError.style.display = "block";
        hasError = true;
    }

    // パスワードのチェック
    if (passwordValue === "") {
        errorMessages[3].style.display = "block";
        hasError = true;
    } else {
        errorMessages[3].style.display = "none";
    }

    // 利用規約チェックボックスのチェック状態を確認
    if (!checkBoxCheck) {
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

// 文字制限
const userName = document.getElementById('userName');
const inputCharacterError = document.getElementById('inputCharacterError');
userName.addEventListener('input', function(){
    const userNameInput = userName.value;
    const validPattern = /^[a-zA-Z0-9_]*$/;
    if (validPattern.test(userNameInput)) {
        inputCharacterError.style.display = 'none';  // エラーメッセージを非表示
    } else {
        inputCharacterError.style.display = 'block';  // エラーメッセージを表示
    }
})
// 有効メールアドレス制限



// パスワード入力欄のパスワード表示非表示機能
function pushHideButton() {
    let password = document.getElementById("password");
    let buttonEye = document.getElementById("buttonEye");
    if(password.type === "text") {
        password.type = "password";
        buttonEye.className = "fa fa-eye-slash";
    } else {
        password.type = "text";
        buttonEye.className = "fa fa-eye";
    }
}
