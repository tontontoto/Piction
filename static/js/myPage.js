// // 画像またはSVGアイコンをクリックしたときにファイル選択ダイアログを開く
document.querySelector('.cameraIconBox').addEventListener('click', function () {
    document.getElementById('triming_image').click();
});

document.getElementById('triming_image').addEventListener('change', function () {
    // ファイルが選択されたとき、または同じファイルが選択されたとき
    if (this.files.length > 0) {
        document.getElementById('trimingiconedit').click();  // 次のアクションを実行
    }
});

document.getElementById('backExampleModalToggle').addEventListener('click', function () {
    // 前回選択されたファイルと同じファイルが選ばれてもイベントが発火するように、inputのvalueをリセット
    document.getElementById('triming_image').value = '';  // valueをリセット
    console.log('valueリセット');

});

document.getElementById('crop_btn').addEventListener('click', function () {
    document.getElementById('backExampleModalToggle').click();
});


var myModal = new bootstrap.Modal(document.getElementById('exampleModalToggle2'), {
    backdrop: 'static',   // 背景クリックで閉じない
    keyboard: false       // ESCキーで閉じない
});


document.addEventListener("DOMContentLoaded", function () {
    const profileForm = document.getElementById("saveButton");
    const displayName = document.querySelector("input[name='displayName']");
    const userName = document.querySelector("input[name='userName']");
    const mailAddress = document.querySelector("input[name='mailAddress']");
    const errorMessages = document.querySelectorAll(".errorMessageRequired");

    // ユーザー名の正規表現（半角英数+アンダースコア、2～15字）
    const userNameRegex = /^[a-zA-Z0-9_]{2,15}$/;
    // メールアドレスの正規表現
    const emailRegex = /^[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\-]+)*@([a-zA-Z0-9\-]*[a-zA-Z0-9]\.)+[a-zA-Z]{2,}$/;

    // フォーム送信時にチェックする処理
    profileForm.addEventListener("submit", function (event) {
        let hasError = false;

        // **表示名のチェック（1～30文字）**
        if (displayName.value.length === 0) {
            errorMessages[0].style.display = "block";
            errorMessages[0].textContent = "必須";
            hasError = true;
        } else if (displayName.value.length > 30) {
            errorMessages[0].style.display = "block";
            errorMessages[0].textContent = "30文字以内で入力してください。";
            hasError = true;
        } else {
            errorMessages[0].textContent = "";
        }

        // **ユーザー名のチェック**
        if (userName.value.length === 0) {
            errorMessages[1].style.display = "block";
            errorMessages[1].textContent = "必須";
            hasError = true;
        } else if (!/^[a-zA-Z0-9_]/.test(userName.value[0])) {
            errorMessages[1].style.display = "block";
            errorMessages[1].textContent = "半角英数字または半角アンダーバーで始めてください。";
            hasError = true;
        } else if (!userNameRegex.test(userName.value)) {
            errorMessages[1].style.display = "block";
            errorMessages[1].textContent = "半角英数字と半角アンダーバーのみ、2〜15文字で入力してください。";
            hasError = true;
        } else {
            errorMessages[1].textContent = "";
        }

        // **メールアドレスのチェック**
        if (mailAddress.value.length === 0) {
            errorMessages[2].style.display = "block";
            errorMessages[2].textContent = "必須";
            hasError = true;
        } else if (!emailRegex.test(mailAddress.value)) {
            errorMessages[2].style.display = "block";
            errorMessages[2].textContent = "有効なメールアドレスを入力してください。";
            hasError = true;
        } else {
            errorMessages[2].textContent = "";
        }

        // **エラーがある場合、送信を防ぐ**
        if (hasError) {
            console.log("フォーム送信を中止");
            event.preventDefault();
        }
    });
});


// // モーダル1の「次のステップ」ボタンをクリックしたとき
// document.querySelector('[data-bs-target="#exampleModalToggle2"]').addEventListener('click', function() {
//     // モーダル1を非表示にする
//     var firstModal = new bootstrap.Modal(document.getElementById('exampleModalToggle'));
//     firstModal.hide();

//     // モーダル2を表示する
//     var secondModal = new bootstrap.Modal(document.getElementById('exampleModalToggle2'));
//     secondModal.show();
// });

// // モーダル2の戻るボタン（←）をクリックしたとき
// document.querySelector('.btn-secondary[data-bs-dismiss="modal"][data-bs-target="#exampleModalToggle"]').addEventListener('click', function() {
//     // モーダル2を非表示にする
//     var secondModal = new bootstrap.Modal(document.getElementById('exampleModalToggle2'));
//     secondModal.hide();

//     // モーダル1を表示する
//     var firstModal = new bootstrap.Modal(document.getElementById('exampleModalToggle'));
//     firstModal.show();
// });

// // モーダル1が閉じられた際にリセットする
// document.getElementById('exampleModalToggle').addEventListener('hidden.bs.modal', function () {
//     // ファイル選択の状態をリセット
//     document.getElementById('triming_image').value = '';
//     document.getElementById('icon').src = ''; // アイコンの画像もリセット
// });

// // モーダル2が閉じられた際にリセットする
// document.getElementById('exampleModalToggle2').addEventListener('hidden.bs.modal', function () {
//     // 必要な状態をリセット
//     document.getElementById('trimed_image').src = ''; // トリミング画像のリセット
// });
