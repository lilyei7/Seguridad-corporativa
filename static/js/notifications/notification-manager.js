class NotificationManager {
    constructor() {
        this.isSupported = 'Notification' in window && 'serviceWorker' in navigator;
        this.isSubscribed = false;
        this.pushSubscription = null;
        this.init();
    }

    async init() {
        if (!this.isSupported) {
            console.warn('Push notifications no son compatibles en este navegador');
            return;
        }

        try {
            // Registrar service worker
            const registration = await navigator.serviceWorker.register('/static/js/notifications/sw.js');
            console.log('Service Worker registrado:', registration);

            // Verificar estado de suscripción
            await this.checkSubscriptionStatus(registration);
        } catch (error) {
            console.error('Error inicializando notificaciones:', error);
        }
    }

    async checkSubscriptionStatus(registration) {
        try {
            this.pushSubscription = await registration.pushManager.getSubscription();
            this.isSubscribed = !!this.pushSubscription;
            
            // Actualizar UI
            this.updateNotificationUI();
        } catch (error) {
            console.error('Error verificando suscripción:', error);
        }
    }

    async requestPermission() {
        if (!this.isSupported) return false;

        try {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        } catch (error) {
            console.error('Error solicitando permisos:', error);
            return false;
        }
    }

    async subscribe() {
        if (!this.isSupported) {
            alert('Las notificaciones push no son compatibles en este navegador');
            return false;
        }

        try {
            // Solicitar permisos
            const hasPermission = await this.requestPermission();
            if (!hasPermission) {
                alert('Los permisos de notificación son necesarios para recibir alertas');
                return false;
            }

            // Obtener registration del service worker
            const registration = await navigator.serviceWorker.ready;

            // Crear suscripción
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(window.VAPID_PUBLIC_KEY)
            });

            // Enviar suscripción al servidor
            const success = await this.sendSubscriptionToServer(subscription);
            
            if (success) {
                this.pushSubscription = subscription;
                this.isSubscribed = true;
                this.updateNotificationUI();
                this.showSuccessMessage('¡Notificaciones activadas correctamente!');
                return true;
            } else {
                throw new Error('Error enviando suscripción al servidor');
            }
        } catch (error) {
            console.error('Error suscribiendo a notificaciones:', error);
            alert('Error activando notificaciones. Intenta de nuevo.');
            return false;
        }
    }

    async unsubscribe() {
        if (!this.pushSubscription) return true;

        try {
            // Cancelar suscripción en el navegador
            const success = await this.pushSubscription.unsubscribe();
            
            if (success) {
                // Notificar al servidor
                await this.removeSubscriptionFromServer();
                
                this.pushSubscription = null;
                this.isSubscribed = false;
                this.updateNotificationUI();
                this.showSuccessMessage('Notificaciones desactivadas');
                return true;
            }
        } catch (error) {
            console.error('Error cancelando suscripción:', error);
            alert('Error desactivando notificaciones');
            return false;
        }
    }

    async sendSubscriptionToServer(subscription) {
        try {
            const response = await fetch('/api/notifications/subscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    subscription: subscription.toJSON()
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result.success;
        } catch (error) {
            console.error('Error enviando suscripción:', error);
            return false;
        }
    }

    async removeSubscriptionFromServer() {
        try {
            await fetch('/api/notifications/unsubscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
        } catch (error) {
            console.error('Error removiendo suscripción del servidor:', error);
        }
    }

    async markAsRead(notificationIds) {
        try {
            const response = await fetch('/api/notifications/mark-read/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    notification_ids: notificationIds
                })
            });

            return response.ok;
        } catch (error) {
            console.error('Error marcando notificaciones como leídas:', error);
            return false;
        }
    }

    async getUnreadNotifications() {
        try {
            const response = await fetch('/api/notifications/unread/');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error obteniendo notificaciones:', error);
        }
        return [];
    }

    updateNotificationUI() {
        // Actualizar botón de notificaciones
        const notificationBtn = document.getElementById('notification-toggle-btn');
        const notificationStatus = document.getElementById('notification-status');
        
        if (notificationBtn) {
            if (this.isSubscribed) {
                notificationBtn.innerHTML = `
                    <i class="fas fa-bell-slash"></i>
                    <span class="ml-2">Desactivar Notificaciones</span>
                `;
                notificationBtn.className = 'bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors';
                notificationBtn.onclick = () => this.unsubscribe();
            } else {
                notificationBtn.innerHTML = `
                    <i class="fas fa-bell"></i>
                    <span class="ml-2">Activar Notificaciones</span>
                `;
                notificationBtn.className = 'bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors';
                notificationBtn.onclick = () => this.subscribe();
            }
        }

        if (notificationStatus) {
            notificationStatus.textContent = this.isSubscribed ? 
                'Notificaciones activadas' : 'Notificaciones desactivadas';
            notificationStatus.className = this.isSubscribed ? 
                'text-green-600 text-sm' : 'text-gray-500 text-sm';
        }

        // Actualizar contador de notificaciones
        this.updateNotificationBadge();
    }

    async updateNotificationBadge() {
        const unread = await this.getUnreadNotifications();
        const badge = document.getElementById('notification-badge');
        
        if (badge) {
            if (unread.length > 0) {
                badge.textContent = unread.length > 99 ? '99+' : unread.length;
                badge.style.display = 'block';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    showSuccessMessage(message) {
        // Crear toast notification
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform';
        toast.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-check-circle mr-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Mostrar toast
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);
        
        // Ocultar después de 3 segundos
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.notificationManager = new NotificationManager();
});

// Exportar para uso en otros scripts
window.NotificationManager = NotificationManager;
