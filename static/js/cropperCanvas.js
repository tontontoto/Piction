$(function () {
    var cropper; // Cropperインスタンスを保持

    // ページロード時にローカルストレージから画像データを取得
    const savedImage = localStorage.getItem('trimmedImage');
    if (savedImage) {
        var image = document.getElementById('trimed_image');
        image.src = savedImage;

        // Cropperインスタンスの再設定
        cropper = new Cropper(image, {
            aspectRatio: 1, // 正方形にトリミング
            viewMode: 1, // トリミング範囲を制限
        });
    }
    
    $('#triming_image').on('change', function (event) {
        var trimingImage = event.target.files[0];

        if (!trimingImage) return;

        var reader = new FileReader();
        reader.onload = function (e) {
            var image = document.getElementById('trimed_image');
            image.src = e.target.result;

            if (cropper) {
                cropper.destroy(); // 既存のCropperインスタンスを破棄
            }

            cropper = new Cropper(image, {
                aspectRatio: 1, // 正方形にトリミング
                viewMode: 1, // トリミング範囲を制限
            });
        };
        reader.readAsDataURL(trimingImage);
    });

    // トリミングボタンがクリックされた時
    $('#crop_btn').on('click', function () {
        if (!cropper) {
            alert('画像が選択されていません。');
            return;
        }

        // トリミングされたキャンバスを取得
        const croppedCanvas = cropper.getCroppedCanvas();
        const roundedCanvas = getRoundedCanvas(croppedCanvas);

        // トリミング後の画像を表示
        const roundedImage = document.createElement('img');
        roundedImage.src = roundedCanvas.toDataURL();
        roundedImage.id = 'trimed';
        document.getElementById('result').innerHTML = '';
        document.getElementById('result').appendChild(roundedImage);

        // トリミング後の画像をローカルストレージに保存
        localStorage.setItem('trimmedImage', roundedCanvas.toDataURL());

        // 画像データをinput[type="file"]に設定
        setImageToInput(roundedCanvas);
    });

    // 画像をinput[type="file"]に設定
    function setImageToInput(croppedCanvas) {
        // Canvasの画像データ（Base64）を取得
        const base64Data = croppedCanvas.toDataURL('image/jpeg');
        const byteString = atob(base64Data.split(',')[1]);
        const mimeString = base64Data.split(',')[0].split(':')[1].split(';')[0];

        // バイト配列を作成
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }

        // Blobオブジェクトを作成
        const blob = new Blob([ab], { type: mimeString });
        const file = new File([blob], 'cropped-image.jpg', { type: mimeString });

        // BlobをFileオブジェクトに変換してinput[type="file"]にセット
        const fileInput = document.getElementById('triming_image');
        const dataTransfer = new DataTransfer(); // 仮想的なファイル転送オブジェクト
        dataTransfer.items.add(file); // Fileを追加
        fileInput.files = dataTransfer.files; // inputのfilesプロパティに設定
    }

    // 丸くトリミングするためのキャンバスを作成
    function getRoundedCanvas(sourceCanvas) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        const width = sourceCanvas.width;
        const height = sourceCanvas.height;

        canvas.width = width;
        canvas.height = height;
        context.imageSmoothingEnabled = true;
        context.drawImage(sourceCanvas, 0, 0, width, height);
        context.globalCompositeOperation = 'destination-in';
        context.beginPath();
        context.arc(width / 2, height / 2, Math.min(width, height) / 2, 0, 2 * Math.PI, true);
        context.fill();
        return canvas;
    }

    // フォーム送信時にトリミングした画像をinputにセットして送信
    $('#uploadForm').on('submit', function (event) {
        event.preventDefault(); // デフォルトの送信を防止
        if (cropper) {
            const croppedCanvas = cropper.getCroppedCanvas();
            setImageToInput(croppedCanvas); // トリミングした画像をinputに設定
        }
        // フォームを送信
        // this.submit();
        console.log("form submit!");

    });
});
