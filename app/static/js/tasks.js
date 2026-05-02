/**
 * Дополнительные функции для страниц задач
 * (работа с категориями, динамическая подгрузка, фильтры)
 */

document.addEventListener('DOMContentLoaded', function() {
    // Динамическая загрузка подсказки
    const hintBtn = document.getElementById('showHintBtn');
    if (hintBtn) {
        hintBtn.addEventListener('click', function() {
            const hintText = this.dataset.hint;
            const hintDiv = document.getElementById('hintContent');
            if (hintDiv) {
                hintDiv.textContent = hintText;
                hintDiv.classList.remove('d-none');
            }
            this.style.display = 'none';
        });
    }

    // Копирование ответа в буфер (если есть кнопка)
    const copyAnswerBtn = document.getElementById('copyAnswerBtn');
    if (copyAnswerBtn) {
        copyAnswerBtn.addEventListener('click', function() {
            const answer = this.dataset.answer;
            navigator.clipboard?.writeText(answer).then(() => {
                alert('Ответ скопирован!');
            }).catch(() => {
                prompt('Скопируйте вручную:', answer);
            });
        });
    }

    // Фильтр по сложности через ссылки (если на странице есть pills)
    const difficultyFilters = document.querySelectorAll('.difficulty-filter');
    difficultyFilters.forEach(filter => {
        filter.addEventListener('click', function(e) {
            e.preventDefault();
            const difficulty = this.dataset.difficulty;
            const url = new URL(window.location);
            url.searchParams.set('difficulty', difficulty);
            window.location = url;
        });
    });

    // Сохранение позиции скролла при пагинации (опционально)
    const paginationLinks = document.querySelectorAll('.pagination .page-link');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function() {
            sessionStorage.setItem('scrollPosition', window.scrollY);
        });
    });

    const savedPosition = sessionStorage.getItem('scrollPosition');
    if (savedPosition) {
        window.scrollTo(0, parseInt(savedPosition));
        sessionStorage.removeItem('scrollPosition');
    }
});