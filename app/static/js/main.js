document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            bootstrap.Alert.getOrCreateInstance(alert)?.close();
        });
    }, 5000);

    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const taskId = this.dataset.taskId;
            const response = await fetch(`/like/${taskId}`, {
                method: 'POST',
                headers: {'X-CSRFToken': getCsrfToken()}
            });
            const data = await response.json();
            if (response.ok) {
                this.classList.toggle('active', data.liked);
                const icon = this.querySelector('i');
                icon.classList.toggle('bi-heart', !data.liked);
                icon.classList.toggle('bi-heart-fill', data.liked);
                this.closest('.card').querySelector('.like-count').textContent = data.count;
            }
        });
    });

    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const taskId = this.dataset.taskId;
            const response = await fetch(`/favorite/${taskId}`, {
                method: 'POST',
                headers: {'X-CSRFToken': getCsrfToken()}
            });
            const data = await response.json();
            if (response.ok) {
                this.classList.toggle('active', data.favorited);
                const icon = this.querySelector('i');
                icon.classList.toggle('bi-star', !data.favorited);
                icon.classList.toggle('bi-star-fill', data.favorited);
            }
        });
    });

    document.querySelectorAll('.answer-form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const taskId = this.dataset.taskId;
            const feedback = this.querySelector('.answer-feedback');
            const response = await fetch(`/check_answer/${taskId}`, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            feedback.innerHTML = `<div class="alert alert-${data.status === 'correct' ? 'success' : 'danger'}">${data.message}</div>`;
            if (data.status === 'correct') {
                this.querySelector('input[name="answer"]').disabled = true;
                this.querySelector('button[type="submit"]').disabled = true;
            }
        });
    });
});

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content');
    const input = document.querySelector('input[name="csrf_token"]');
    return input ? input.value : '';
}