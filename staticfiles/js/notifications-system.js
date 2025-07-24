/**
 * Sistema de Notificaciones Robusto v2.0
 * Soporte completo para móvil y desktop
 * Notificaciones bidireccionales entre inquilinos y administradores
 */
class RobustNotificationSystem {
    constructor() {
        this.lastNotificationCheck = 0;
        this.notificationSound = null;
        this.isInitialized = false;
        this.pollingInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupAudio();
        this.initEventListeners();
        this.requestNotificationPermission();
        this.loadInitialNotifications();
        this.startPolling();
        this.isInitialized = true;
        console.log('🔔 Sistema de notificaciones robusto v2.0 iniciado');
    }
    
    setupAudio() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.createNotificationSound(audioContext);
        } catch (e) {
            console.log('Web Audio no disponible, usando método alternativo');
        }
    }
    
    createNotificationSound(audioContext) {
        this.notificationSound = { audioContext };
    }
    
    playNotificationSound(priority = 3) {
        try {
            if (this.notificationSound && this.notificationSound.audioContext) {
                const { audioContext } = this.notificationSound;
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                // Diferentes sonidos según prioridad
                if (priority <= 2) {
                    // Urgente/Alto - Sonido más agudo y rápido
                    oscillator.frequency.setValueAtTime(1000, audioContext.currentTime);
                    oscillator.frequency.setValueAtTime(800, audioContext.currentTime + 0.1);
                    oscillator.frequency.setValueAtTime(1000, audioContext.currentTime + 0.2);
                    oscillator.frequency.setValueAtTime(800, audioContext.currentTime + 0.3);
                } else {
                    // Normal - Sonido suave
                    oscillator.frequency.setValueAtTime(600, audioContext.currentTime);
                    oscillator.frequency.setValueAtTime(700, audioContext.currentTime + 0.15);
                    oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.3);
                }
                
                gainNode.gain.setValueAtTime(0, audioContext.currentTime);
                gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.01);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.4);
                
                oscillator.start();
                oscillator.stop(audioContext.currentTime + 0.4);
            }
        } catch (e) {
            console.log('Error reproduciendo sonido:', e);
        }
    }
    
    initEventListeners() {
        this.setupMobileNotifications();
        this.setupDesktopNotifications();
        this.setupMarkAllReadButtons();
        
        // Cerrar dropdowns al hacer click fuera
        document.addEventListener('click', (e) => {
            const mobileDropdown = document.getElementById('mobile-notifications-dropdown');
            const desktopDropdown = document.getElementById('desktop-notifications-dropdown');
            const mobileBtn = document.getElementById('mobile-notifications-btn');
            const desktopBtn = document.getElementById('desktop-notifications-btn');
            
            if (mobileDropdown && mobileBtn && 
                !mobileBtn.contains(e.target) && !mobileDropdown.contains(e.target)) {
                mobileDropdown.classList.add('hidden');
            }
            
            if (desktopDropdown && desktopBtn && 
                !desktopBtn.contains(e.target) && !desktopDropdown.contains(e.target)) {
                desktopDropdown.classList.add('hidden');
            }
        });
    }
    
    setupMobileNotifications() {
        const mobileBtn = document.getElementById('mobile-notifications-btn');
        const mobileDropdown = document.getElementById('mobile-notifications-dropdown');
        
        if (mobileBtn && mobileDropdown) {
            mobileBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                mobileDropdown.classList.toggle('hidden');
                if (!mobileDropdown.classList.contains('hidden')) {
                    this.loadNotificationsInDropdown('mobile');
                }
            });
            console.log('✅ Botón móvil configurado');
        } else {
            console.warn('⚠️ Elementos móviles no encontrados:', { mobileBtn: !!mobileBtn, mobileDropdown: !!mobileDropdown });
        }
    }
    
    setupDesktopNotifications() {
        const desktopBtn = document.getElementById('desktop-notifications-btn');
        const desktopDropdown = document.getElementById('desktop-notifications-dropdown');
        
        if (desktopBtn && desktopDropdown) {
            desktopBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                desktopDropdown.classList.toggle('hidden');
                if (!desktopDropdown.classList.contains('hidden')) {
                    this.loadNotificationsInDropdown('desktop');
                }
            });
            console.log('✅ Botón desktop configurado');
        } else {
            console.warn('⚠️ Elementos desktop no encontrados:', { desktopBtn: !!desktopBtn, desktopDropdown: !!desktopDropdown });
        }
    }
    
    setupMarkAllReadButtons() {
        const markAllReadBtns = document.querySelectorAll('[id*="mark-all-read"]');
        markAllReadBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.markAllAsRead();
            });
        });
        console.log(`✅ ${markAllReadBtns.length} botones "marcar como leído" configurados`);
    }
    
    async loadInitialNotifications() {
        try {
            const response = await fetch('/accounts/api/notifications/counts/');
            if (response.ok) {
                const data = await response.json();
                this.updateNotificationCounts(data.unread || 0, data.urgent || 0);
                console.log('✅ Notificaciones iniciales cargadas:', data);
            } else {
                console.warn('⚠️ Error cargando notificaciones iniciales:', response.status);
            }
        } catch (error) {
            console.error('❌ Error cargando notificaciones iniciales:', error);
        }
    }
    
    async checkForNewNotifications() {
        try {
            const response = await fetch('/accounts/api/notifications/counts/');
            if (response.ok) {
                const data = await response.json();
                const { unread, urgent } = data;
                
                // Si hay más notificaciones que antes, obtener las nuevas
                if (unread > this.lastNotificationCheck && this.lastNotificationCheck > 0) {
                    const newNotificationsResponse = await fetch('/accounts/api/notifications/recent/?limit=5');
                    if (newNotificationsResponse.ok) {
                        const newData = await newNotificationsResponse.json();
                        const newNotifications = newData.notifications.slice(0, unread - this.lastNotificationCheck);
                        
                        for (const notification of newNotifications) {
                            if (!notification.is_read) {
                                this.showNewNotification(notification);
                            }
                        }
                    }
                }
                
                this.updateNotificationCounts(unread || 0, urgent || 0);
                this.lastNotificationCheck = unread || 0;
            }
        } catch (error) {
            console.error('❌ Error verificando nuevas notificaciones:', error);
        }
    }
    
    showNewNotification(notification) {
        // Sonido
        this.playNotificationSound(notification.priority);
        
        // Vibración en móviles
        if ('vibrate' in navigator) {
            if (notification.priority <= 2) {
                navigator.vibrate([200, 100, 200, 100, 200]); // Urgente
            } else {
                navigator.vibrate([200, 100, 200]); // Normal
            }
        }
        
        // Notificación del navegador
        this.showBrowserNotification(notification);
        
        // Toast notification
        this.showToastNotification(notification);
        
        // Efecto visual en el icono de notificaciones
        this.animateNotificationBell();
    }
    
    animateNotificationBell() {
        const mobileBell = document.getElementById('mobile-notification-bell');
        const desktopBell = document.getElementById('desktop-notification-bell');
        
        [mobileBell, desktopBell].forEach(bell => {
            if (bell) {
                bell.classList.add('notification-bell-shake');
                setTimeout(() => {
                    bell.classList.remove('notification-bell-shake');
                }, 800);
            }
        });
    }
    
    updateNotificationCounts(unread, urgent = 0) {
        // Badges móviles
        const mobileBadge = document.getElementById('mobile-notification-badge');
        const mobileCount = document.getElementById('mobile-notification-count');
        
        // Badges desktop
        const desktopBadge = document.getElementById('desktop-notification-badge');
        const desktopCount = document.getElementById('desktop-notification-count');
        
        [
            { badge: mobileBadge, count: mobileCount, name: 'mobile' },
            { badge: desktopBadge, count: desktopCount, name: 'desktop' }
        ].forEach(({ badge, count, name }) => {
            if (badge && count) {
                if (unread > 0) {
                    badge.classList.remove('hidden');
                    count.textContent = unread > 99 ? '99+' : unread;
                    
                    // Color basado en urgencia
                    if (urgent > 0) {
                        badge.className = badge.className.replace(/bg-\w+-\d+/, 'bg-red-500');
                    } else {
                        badge.className = badge.className.replace(/bg-\w+-\d+/, 'bg-blue-500');
                    }
                    console.log(`✅ Badge ${name} actualizado: ${unread} notificaciones`);
                } else {
                    badge.classList.add('hidden');
                    console.log(`✅ Badge ${name} ocultado (sin notificaciones)`);
                }
            } else {
                console.warn(`⚠️ Elementos de badge ${name} no encontrados:`, { badge: !!badge, count: !!count });
            }
        });
    }
    
    async loadNotificationsInDropdown(type = 'mobile') {
        try {
            const response = await fetch('/accounts/api/notifications/recent/?limit=10');
            if (response.ok) {
                const data = await response.json();
                this.renderNotificationsInDropdown(data.notifications || [], type);
                console.log(`✅ Notificaciones cargadas en dropdown ${type}:`, data.notifications?.length || 0);
            } else {
                console.warn(`⚠️ Error cargando notificaciones para dropdown ${type}:`, response.status);
            }
        } catch (error) {
            console.error(`❌ Error cargando notificaciones para dropdown ${type}:`, error);
        }
    }
    
    renderNotificationsInDropdown(notifications, type) {
        const listElement = document.getElementById(`${type}-notifications-list`);
        if (!listElement) {
            console.warn(`⚠️ Lista de notificaciones ${type} no encontrada`);
            return;
        }
        
        if (notifications.length === 0) {
            listElement.innerHTML = `
                <div class="p-4 text-center text-gray-500">
                    <i class="fas fa-bell-slash text-2xl mb-2"></i>
                    <p>No hay notificaciones</p>
                </div>
            `;
            return;
        }
        
        const notificationItems = notifications.map(notification => {
            const timeAgo = this.getTimeAgo(notification.created_at);
            const priorityColors = {
                1: 'border-red-500 bg-red-50',
                2: 'border-orange-500 bg-orange-50',
                3: 'border-blue-500 bg-blue-50',
                4: 'border-gray-500 bg-gray-50'
            };
            
            const colorClass = priorityColors[notification.priority] || 'border-blue-500 bg-blue-50';
            const unreadClass = notification.is_read ? 'opacity-75' : '';
            
            return `
                <div class="p-3 border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer ${unreadClass}"
                     onclick="markNotificationAsRead(${notification.id}, '${notification.action_url || '#'}')">
                    <div class="flex items-start space-x-3">
                        <div class="flex-shrink-0">
                            <div class="w-8 h-8 rounded-full border-2 ${colorClass} flex items-center justify-center">
                                <span class="text-xs">${this.getNotificationIcon(notification.notification_type)}</span>
                            </div>
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-sm font-medium text-gray-900 truncate">
                                ${notification.title}
                            </p>
                            <p class="text-xs text-gray-600 mt-1">
                                ${notification.message.substring(0, 100)}${notification.message.length > 100 ? '...' : ''}
                            </p>
                            <p class="text-xs text-gray-500 mt-1">${timeAgo}</p>
                        </div>
                        ${!notification.is_read ? '<div class="w-2 h-2 bg-blue-500 rounded-full"></div>' : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        listElement.innerHTML = notificationItems;
    }
    
    getTimeAgo(dateString) {
        const now = new Date();
        const date = new Date(dateString);
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) {
            return 'hace un momento';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `hace ${minutes} minuto${minutes !== 1 ? 's' : ''}`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `hace ${hours} hora${hours !== 1 ? 's' : ''}`;
        } else {
            const days = Math.floor(diffInSeconds / 86400);
            return `hace ${days} día${days !== 1 ? 's' : ''}`;
        }
    }
    
    getNotificationIcon(type) {
        const icons = {
            'maintenance_request': '🔧',
            'maintenance_update': '🔄',
            'incident_report': '🚨',
            'visit_notification': '👥',
            'system_alert': '⚠️',
            'security_alert': '🛡️',
            'general': '📢'
        };
        return icons[type] || '📢';
    }
    
    showBrowserNotification(notification) {
        if ('Notification' in window && Notification.permission === 'granted') {
            const browserNotification = new Notification(notification.title, {
                body: notification.message,
                icon: '/static/favicon.ico',
                badge: '/static/favicon.ico',
                tag: `notification-${notification.id}`,
                requireInteraction: notification.priority <= 2,
                silent: false
            });
            
            browserNotification.onclick = () => {
                window.focus();
                if (notification.action_url) {
                    window.location.href = notification.action_url;
                }
                browserNotification.close();
            };
            
            // Auto cerrar después de 10 segundos excepto las urgentes
            if (notification.priority > 2) {
                setTimeout(() => browserNotification.close(), 10000);
            }
        }
    }
    
    showToastNotification(notification) {
        const priorityColors = {
            1: 'bg-red-600',
            2: 'bg-orange-600', 
            3: 'bg-blue-600',
            4: 'bg-gray-600'
        };
        
        const color = priorityColors[notification.priority] || priorityColors[3];
        const isUrgent = notification.priority <= 2;
        
        const toast = document.createElement('div');
        toast.className = `fixed top-20 right-4 ${color} text-white p-4 rounded-lg shadow-2xl z-50 max-w-sm transform translate-x-full transition-transform duration-500 ${isUrgent ? 'urgent-notification' : ''}`;
        toast.innerHTML = `
            <div class="flex items-start space-x-3">
                <div class="flex-shrink-0 text-lg">
                    ${this.getNotificationIcon(notification.notification_type)}
                </div>
                <div class="flex-1">
                    <h4 class="font-bold text-sm">${notification.title}</h4>
                    <p class="text-xs mt-1 opacity-90">${notification.message.substring(0, 150)}${notification.message.length > 150 ? '...' : ''}</p>
                    ${notification.action_url ? `<button onclick="window.location.href='${notification.action_url}'" class="mt-2 text-xs bg-white bg-opacity-20 px-3 py-1 rounded hover:bg-opacity-30 transition-colors font-medium">Ver detalles</button>` : ''}
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="text-white hover:text-gray-200 text-lg">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Animar entrada
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);
        
        // Auto remover (urgentes se quedan más tiempo)
        const autoRemoveTime = isUrgent ? 20000 : 10000;
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('translate-x-full');
                setTimeout(() => {
                    if (toast.parentElement) {
                        toast.remove();
                    }
                }, 500);
            }
        }, autoRemoveTime);
    }
    
    async markAllAsRead() {
        try {
            const response = await fetch('/accounts/api/notifications/mark-all-read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                this.updateNotificationCounts(0);
                this.loadNotificationsInDropdown('mobile');
                this.loadNotificationsInDropdown('desktop');
                
                console.log('✅ Todas las notificaciones marcadas como leídas');
                
                // Mostrar mensaje de confirmación
                if (window.showNotification) {
                    window.showNotification('Todas las notificaciones han sido marcadas como leídas', 'success');
                }
            }
        } catch (error) {
            console.error('❌ Error marcando notificaciones como leídas:', error);
        }
    }
    
    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    console.log('✅ Permisos de notificación concedidos');
                    this.showToastNotification({
                        title: '🔔 Notificaciones Activadas',
                        message: 'Ahora recibirás alertas instantáneas de nuevos reportes de mantenimiento',
                        notification_type: 'system_alert',
                        priority: 3
                    });
                }
            });
        }
    }
    
    startPolling() {
        // Verificar nuevas notificaciones cada 8 segundos
        this.pollingInterval = setInterval(() => {
            this.checkForNewNotifications();
        }, 8000);
        
        // Primera verificación después de 3 segundos
        setTimeout(() => {
            this.checkForNewNotifications();
        }, 3000);
        
        console.log('✅ Polling de notificaciones iniciado (cada 8 segundos)');
    }
    
    // Método para limpiar recursos al destruir
    destroy() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        console.log('🛑 Sistema de notificaciones destruido');
    }
}

// Función global para marcar notificación como leída
window.markNotificationAsRead = async function(notificationId, actionUrl = null) {
    try {
        const response = await fetch(`/accounts/api/notifications/${notificationId}/read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok && window.notificationSystem) {
            // Actualizar contadores
            window.notificationSystem.loadInitialNotifications();
            
            // Recargar dropdown
            window.notificationSystem.loadNotificationsInDropdown('mobile');
            window.notificationSystem.loadNotificationsInDropdown('desktop');
            
            console.log(`✅ Notificación ${notificationId} marcada como leída`);
            
            // Navegar si hay URL
            if (actionUrl && actionUrl !== '#') {
                window.location.href = actionUrl;
            }
        }
    } catch (error) {
        console.error('❌ Error marcando notificación como leída:', error);
    }
};

// Función global para mostrar notificaciones desde otros scripts (compatibilidad)
window.showMaintenanceNotification = function(message, type = 'info') {
    if (window.notificationSystem) {
        window.notificationSystem.showToastNotification({
            title: '🔧 Sistema de Mantenimiento',
            message: message,
            notification_type: 'system_alert',
            priority: type === 'error' ? 2 : 3
        });
    }
};

// Inicializar sistema de notificaciones cuando el DOM esté listo
let notificationSystem;
document.addEventListener('DOMContentLoaded', function() {
    // Esperar un poco para asegurarse de que todos los elementos estén cargados
    setTimeout(() => {
        notificationSystem = new RobustNotificationSystem();
        
        // Hacer disponible globalmente
        window.notificationSystem = notificationSystem;
        
        console.log('🚀 Sistema de notificaciones completamente iniciado');
    }, 500);
});

// Limpiar recursos al cerrar página
window.addEventListener('beforeunload', function() {
    if (window.notificationSystem) {
        window.notificationSystem.destroy();
    }
});

console.log('📦 notifications-system.js cargado correctamente');