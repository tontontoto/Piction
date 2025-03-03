// // 画像またはSVGアイコンをクリックしたときにファイル選択ダイアログを開く
document.querySelector('.cameraIconBox').addEventListener('click', function () {
    let fileInput = document.querySelector('.trimming_image'); // 1つ目の要素を取得
    if (fileInput) {
        fileInput.click();
        console.log(document.querySelector('.cameraIconBox'));
    }
});


document.getElementsByClassName('trimming_image').addEventListener('change', function () {
    // ファイルが選択されたとき、または同じファイルが選択されたとき
    if (this.files.length > 0) {
        document.getElementsByClassName('trimmingIconEdit').click();  // 次のアクションを実行
    }
});

document.getElementsByClassName('backExampleModalToggle').addEventListener('click', function () {
    // 前回選択されたファイルと同じファイルが選ばれてもイベントが発火するように、inputのvalueをリセット
    document.getElementsByClassName('trimming_image').value = '';  // valueをリセット
    console.log('valueリセット');
    
});

document.getElementsByClassName('crop_btn').addEventListener('click', function() {
    document.getElementsByClassName('backExampleModalToggle').click();
});




var myModal = new bootstrap.Modal(document.getElementById('exampleModalToggle2'), {
    backdrop: 'static',   // 背景クリックで閉じない
    keyboard: false       // ESCキーで閉じない
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
//     document.getElementsByClassName('triming_image').value = '';
//     document.getElementById('icon').src = ''; // アイコンの画像もリセット
// });

// // モーダル2が閉じられた際にリセットする
// document.getElementById('exampleModalToggle2').addEventListener('hidden.bs.modal', function () {
//     // 必要な状態をリセット
//     document.getElementById('trimed_image').src = ''; // トリミング画像のリセット
// });