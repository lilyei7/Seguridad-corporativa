const CACHE_NAME = 'security-corp-notifications-v1';
const urlsToCache = [
    '/static/css/dashboard.css',
    '/static/js/notifications/notification-manager.js',
    '/static/img/logo.png'
];

// Instalar service worker
self.addEventListener('install', event => {
    console.log('Service Worker instalado');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Cache abierto');
                return cache.addAll(urlsToCache);
            })
    );
});

// Activar service worker
self.addEventListener('activate', event => {
    console.log('Service Worker activado');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Eliminando cache antigua:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Interceptar requests
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Devolver desde cache si existe, sino fetch
                return response || fetch(event.request);
            })
    );
});

// Manejar notificaciones push
self.addEventListener('push', event => {
    console.log('Push notification recibida:', event);

    let notificationData = {
        title: 'Security Corp',
        body: 'Nueva notificación',
        icon: '/static/img/logo.png',
        badge: '/static/img/badge.png',
        data: {
            url: '/'
        }
    };

    if (event.data) {
        try {
            const pushData = event.data.json();
            notificationData = {
                title: pushData.title || notificationData.title,
                body: pushData.body || notificationData.body,
                icon: pushData.icon || notificationData.icon,
                badge: pushData.badge || notificationData.badge,
                image: pushData.image,
                data: {
                    url: pushData.url || '/',
                    notificationId: pushData.notificationId,
                    ...pushData.data
                },
                actions: pushData.actions || [],
                tag: pushData.tag,
                requireInteraction: pushData.requireInteraction || false,
                silent: pushData.silent || false
            };
        } catch (error) {
            console.error('Error parseando datos de push:', error);
        }
    }

    const promiseChain = self.registration.showNotification(
        notificationData.title,
        {
            body: notificationData.body,
            icon: notificationData.icon,
            badge: notificationData.badge,
            image: notificationData.image,
            data: notificationData.data,
            actions: notificationData.actions,
            tag: notificationData.tag,
            requireInteraction: notificationData.requireInteraction,
            silent: notificationData.silent
        }
    );

    event.waitUntil(promiseChain);
});

// Manejar clicks en notificaciones
self.addEventListener('notificationclick', event => {
    console.log('Notificación clickeada:', event);

    event.notification.close();

    const urlToOpen = event.notification.data.url || '/';
    const notificationId = event.notification.data.notificationId;

    // Marcar notificación como leída si tiene ID
    if (notificationId) {
        markNotificationAsRead(notificationId);
    }

    // Manejar acciones específicas
    if (event.action) {
        console.log('Acción clickeada:', event.action);
        handleNotificationAction(event.action, event.notification.data);
        return;
    }

    // Abrir o enfocar ventana
    event.waitUntil(
        clients.matchAll({
            type: 'window',
            includeUncontrolled: true
        }).then(clientList => {
            // Buscar ventana existente
            for (const client of clientList) {
                if (client.url.includes(urlToOpen) && 'focus' in client) {
                    return client.focus();
                }
            }
            
            // Abrir nueva ventana si no existe
            if (clients.openWindow) {
                return clients.openWindow(urlToOpen);
            }
        })
    );
});

// Manejar cierre de notificaciones
self.addEventListener('notificationclose', event => {
    console.log('Notificación cerrada:', event);
    
    const notificationId = event.notification.data.notificationId;
    if (notificationId) {
        markNotificationAsRead(notificationId);
    }
});

// Funciones auxiliares
function markNotificationAsRead(notificationId) {
    fetch('/api/notifications/mark-read/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            notification_ids: [notificationId]
        })
    }).catch(error => {
        console.error('Error marcando notificación como leída:', error);
    });
}

function handleNotificationAction(action, data) {
    switch (action) {
        case 'approve_visit':
            handleVisitAction('approve', data.visitId);
            break;
        case 'reject_visit':
            handleVisitAction('reject', data.visitId);
            break;
        case 'view_details':
            clients.openWindow(data.detailsUrl);
            break;
        default:
            console.log('Acción no reconocida:', action);
    }
}

function handleVisitAction(action, visitId) {
    fetch(`/api/visits/${visitId}/${action}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => {
        if (response.ok) {
            console.log(`Visita ${action}da correctamente`);
        } else {
            console.error(`Error en acción de visita: ${action}`);
        }
    }).catch(error => {
        console.error(`Error ejecutando acción ${action}:`, error);
    });
}
