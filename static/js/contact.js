document.addEventListener("DOMContentLoaded", () => {
    const furiganaInput = document.getElementById('furigana');
    const errorMessage = document.getElementById('error-message');

    furiganaInput.addEventListener('input', () => {
        // 入力内容を検証し、エラーメッセージを表示
        if (!/^([\u30A0-\u30FF\u30FC]*)$/.test(furiganaInput.value)) {
            errorMessage.textContent = '※カタカナ以外の文字が含まれています。';
        } else {
            errorMessage.textContent = '';
        }
    });

    document.querySelector('button[type="submit"]').addEventListener('click', (e) => {
        if (furiganaInput.value === '') {
            e.preventDefault();
            errorMessage.textContent = 'フリガナを入力してください。';
        } else if (!/^([\u30A0-\u30FF\u30FC]+)$/.test(furiganaInput.value)) {
            e.preventDefault();
            errorMessage.textContent = '※カタカナ以外の文字が含まれています。修正してください。';
        } else {
            alert('送信完了: ' + furiganaInput.value);
        }
    });
});