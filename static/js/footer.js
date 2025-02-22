document.addEventListener('DOMContentLoaded', function() {
    const footerColumns = document.querySelectorAll('.footer-column');
    footerColumns.forEach(function(footerColumn) {
        // footer-columnがクリックされたときの処理
        footerColumn.addEventListener('click', function(event) {
            const ul = footerColumn.querySelector('ul');
            if (event.target.closest('.footer-column')) {
                if (ul.style.display === 'none' || ul.style.display === '') {
                    ul.style.display = 'block';
                } else {
                    ul.style.display = 'none';
                }
            }
        });
    });
});
