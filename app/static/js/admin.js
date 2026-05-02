/**
 * Функции для админ-панели
 * (подтверждения действий, массовые операции, AJAX-управление)
 */

document.addEventListener('DOMContentLoaded', function() {
    // Массовое выделение чекбоксов
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('input[type="checkbox"][name="selected_items"]');
            checkboxes.forEach(cb => cb.checked = this.checked);
        });
    }

    // Подтверждение массовых действий
    const bulkActionForm = document.getElementById('bulkActionForm');
    if (bulkActionForm) {
        bulkActionForm.addEventListener('submit', function(e) {
            const action = document.getElementById('bulkActionSelect').value;
            if (!action) {
                e.preventDefault();
                alert('Выберите действие');
                return;
            }
            const selected = document.querySelectorAll('input[type="checkbox"][name="selected_items"]:checked');
            if (selected.length === 0) {
                e.preventDefault();
                alert('Выберите хотя бы один элемент');
                return;
            }
            if (!confirm(`Вы уверены, что хотите выполнить "${action}" для ${selected.length} элементов?`)) {
                e.preventDefault();
            }
        });
    }

    // Быстрое изменение статуса задачи (AJAX)
    const statusSelects = document.querySelectorAll('.task-status-select');
    statusSelects.forEach(select => {
        select.addEventListener('change', async function() {
            const taskId = this.dataset.taskId;
            const newStatus = this.value;
            if (!confirm(`Изменить статус задачи #${taskId} на "${newStatus}"?`)) {
                this.value = this.dataset.originalStatus;
                return;
            }
            const response = await fetch(`/admin/tasks/${taskId}/moderate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ status: newStatus })
            });
            if (response.ok) {
                this.dataset.originalStatus = newStatus;
                // Обновляем визуальное отображение статуса
                const badge = this.closest('tr')?.querySelector('.status-badge');
                if (badge) {
                    badge.textContent = newStatus;
                    badge.className = `badge bg-${getStatusColor(newStatus)}`;
                }
            } else {
                alert('Ошибка при изменении статуса');
                this.value = this.dataset.originalStatus;
            }
        });
    });

    function getStatusColor(status) {
        const colors = {
            'active': 'success',
            'pending': 'warning',
            'archived': 'secondary',
            'rejected': 'danger'
        };
        return colors[status] || 'secondary';
    }

    // Автоматическое обновление счётчиков на дашборде (каждые 30 сек)
    if (window.location.pathname === '/admin/') {
        setInterval(async () => {
            const response = await fetch('/api/v2/statistics');
            const data = await response.json();
            document.getElementById('totalUsers') && (document.getElementById('totalUsers').textContent = data.total_users);
            document.getElementById('totalTasks') && (document.getElementById('totalTasks').textContent = data.total_tasks);
            document.getElementById('totalSolves') && (document.getElementById('totalSolves').textContent = data.total_solves);
        }, 30000);
    }
});