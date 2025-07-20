// SecureCorp Admin - JavaScript Principal

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts después de 5 segundos
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirmar acciones destructivas
    const deleteButtons = document.querySelectorAll('[data-action="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const message = this.getAttribute('data-message') || '¿Estás seguro de que quieres eliminar este elemento?';
            if (confirm(message)) {
                // Proceder con la acción
                const href = this.getAttribute('href');
                if (href) {
                    window.location.href = href;
                }
            }
        });
    });

    // Filtros en tiempo real para tablas
    const searchInputs = document.querySelectorAll('[data-search-table]');
    searchInputs.forEach(input => {
        input.addEventListener('keyup', function() {
            const tableId = this.getAttribute('data-search-table');
            const table = document.getElementById(tableId);
            const filter = this.value.toLowerCase();
            const rows = table.getElementsByTagName('tr');

            for (let i = 1; i < rows.length; i++) {
                const row = rows[i];
                const cells = row.getElementsByTagName('td');
                let found = false;

                for (let j = 0; j < cells.length; j++) {
                    const cell = cells[j];
                    if (cell.textContent.toLowerCase().indexOf(filter) > -1) {
                        found = true;
                        break;
                    }
                }

                row.style.display = found ? '' : 'none';
            }
        });
    });

    // Sidebar toggle para mobile
    const sidebarToggle = document.querySelector('[data-toggle="sidebar"]');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
    }

    // Clock widget
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('es-MX', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        const dateString = now.toLocaleDateString('es-MX', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        const clockElement = document.getElementById('current-time');
        const dateElement = document.getElementById('current-date');

        if (clockElement) {
            clockElement.textContent = timeString;
        }
        if (dateElement) {
            dateElement.textContent = dateString;
        }
    }

    // Actualizar reloj cada segundo
    updateClock();
    setInterval(updateClock, 1000);

    // Estadísticas en tiempo real (cada 30 segundos)
    function updateStats() {
        fetch('/api/stats/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Actualizar estadísticas si los elementos existen
            const elements = {
                'total-tenants': data.total_tenants,
                'total-guards': data.total_guards,
                'pending-visits': data.pending_visits,
                'completed-visits': data.completed_visits
            };

            Object.keys(elements).forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = elements[id];
                }
            });
        })
        .catch(error => {
            console.log('Error actualizando estadísticas:', error);
        });
    }

    // Actualizar estadísticas cada 30 segundos en el dashboard
    if (window.location.pathname.includes('/dashboard/')) {
        setInterval(updateStats, 30000);
    }
});

// Funciones globales
window.SecureCorp = {
    // Mostrar loading spinner
    showLoading: function(element) {
        if (element) {
            const originalContent = element.innerHTML;
            element.innerHTML = '<span class="spinner"></span> Cargando...';
            element.disabled = true;
            element.setAttribute('data-original-content', originalContent);
        }
    },

    // Ocultar loading spinner
    hideLoading: function(element) {
        if (element) {
            const originalContent = element.getAttribute('data-original-content');
            if (originalContent) {
                element.innerHTML = originalContent;
                element.disabled = false;
                element.removeAttribute('data-original-content');
            }
        }
    },

    // Mostrar notificación toast
    showToast: function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remover el toast del DOM después de que se oculte
        toast.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    },

    // Crear contenedor de toasts si no existe
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    },

    // Confirmar acción
    confirm: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },

    // Formatear números
    formatNumber: function(number) {
        return new Intl.NumberFormat('es-MX').format(number);
    },

    // Formatear fecha
    formatDate: function(date) {
        return new Date(date).toLocaleDateString('es-MX');
    },

    // Formatear hora
    formatTime: function(time) {
        return new Date('1970-01-01T' + time + 'Z').toLocaleTimeString('es-MX', {
            timeZone: 'UTC',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
};
