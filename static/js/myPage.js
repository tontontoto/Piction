// 画像またはSVGアイコンをクリックしたときにファイル選択ダイアログを開く
document.querySelector('.cameraIconBox').addEventListener('click', function () {
    document.getElementById('fileInput').click();
});

// ファイルが選択されたときの処理
document.getElementById('fileInput').addEventListener('change', function (event) {
    var file = event.target.files[0];
    if (file) {
        var reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById('icon').src = e.target.result;  // 選んだ画像を表示
        };
        reader.readAsDataURL(file);
    }
});