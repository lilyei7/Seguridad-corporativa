const CACHE_NAME = 'securecorp-v1.0.0';
const STATIC_CACHE = 'securecorp-static-v1.0.0';
const DYNAMIC_CACHE = 'securecorp-dynamic-v1.0.0';

// URLs esenciales para cachear
const urlsToCache = [
  '/',
  '/dashboard/',
  '/vigilante-movil/',
  '/admin-movil/',
  '/inquilino-movil/',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  'https://cdn.tailwindcss.com',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap'
];

// URLs que siempre deben ir a la red (datos dinámicos)
const networkFirst = [
  '/api/',
  '/accounts/api/',
  '/admin/',
  '/login/',
  '/logout/'
];

// Instalación del Service Worker
self.addEventListener('install', function(event) {
  console.log('🔧 SecureCorp SW: Instalando...');
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then(cache => {
        console.log('📦 SecureCorp SW: Cacheando recursos estáticos...');
        return cache.addAll(urlsToCache);
      }),
      self.skipWaiting()
    ])
  );
});

// Activación del Service Worker
self.addEventListener('activate', function(event) {
  console.log('✅ SecureCorp SW: Activando...');
  event.waitUntil(
    Promise.all([
      // Limpiar cachés antiguos
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('🗑️ SecureCorp SW: Eliminando caché antiguo:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      self.clients.claim()
    ])
  );
});

// Estrategia de fetch
self.addEventListener('fetch', function(event) {
  const requestUrl = new URL(event.request.url);
  
  // Ignorar requests que no sean HTTP/HTTPS
  if (!event.request.url.startsWith('http')) {
    return;
  }
  
  // Network first para APIs y datos dinámicos
  if (networkFirst.some(pattern => requestUrl.pathname.startsWith(pattern))) {
    event.respondWith(networkFirstStrategy(event.request));
    return;
  }
  
  // Cache first para recursos estáticos
  if (urlsToCache.some(url => event.request.url.includes(url))) {
    event.respondWith(cacheFirstStrategy(event.request));
    return;
  }
  
  // Stale while revalidate para el resto
  event.respondWith(staleWhileRevalidateStrategy(event.request));
});

// Estrategia: Network First (para APIs)
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('🌐 SecureCorp SW: Network failed, trying cache for:', request.url);
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Fallback para páginas offline
    if (request.destination === 'document') {
      return caches.match('/offline/');
    }
    
    throw error;
  }
}

// Estrategia: Cache First (para recursos estáticos)
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    const cache = await caches.open(STATIC_CACHE);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    console.log('📦 SecureCorp SW: Cache and network failed for:', request.url);
    throw error;
  }
}

// Estrategia: Stale While Revalidate (para contenido general)
async function staleWhileRevalidateStrategy(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cachedResponse = await caches.match(request);
  
  const networkResponsePromise = fetch(request).then(networkResponse => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => null);
  
  return cachedResponse || await networkResponsePromise;
}

// ============================================
// NOTIFICACIONES PUSH
// ============================================

// Escuchar eventos push del servidor
self.addEventListener('push', function(event) {
  console.log('📬 SecureCorp SW: Push recibido:', event);
  
  if (!event.data) {
    console.log('❌ SecureCorp SW: Push sin datos');
    return;
  }
  
  let notificationData;
  try {
    notificationData = event.data.json();
  } catch (error) {
    console.log('❌ SecureCorp SW: Error parseando push data:', error);
    notificationData = {
      title: 'SecureCorp',
      body: event.data.text() || 'Nueva notificación',
      type: 'general'
    };
  }
  
  const options = buildNotificationOptions(notificationData);
  
  event.waitUntil(
    self.registration.showNotification(notificationData.title, options)
  );
});

// Configurar opciones de notificación según el tipo
function buildNotificationOptions(data) {
  const baseOptions = {
    body: data.body || 'Nueva notificación de SecureCorp',
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/icon-72.png',
    tag: data.tag || 'securecorp-notification',
    renotify: true,
    requireInteraction: false,
    silent: false,
    timestamp: Date.now(),
    data: {
      url: data.url || '/dashboard/',
      type: data.type || 'general',
      id: data.id || Date.now().toString()
    }
  };
  
  // Personalizar según el tipo de notificación
  switch (data.type) {
    case 'emergency':
      return {
        ...baseOptions,
        requireInteraction: true,
        silent: false,
        actions: [
          { action: 'view', title: '🚨 Ver Emergencia', icon: '/static/icons/icon-72.png' },
          { action: 'dismiss', title: 'Cerrar', icon: '/static/icons/icon-72.png' }
        ],
        vibrate: [200, 100, 200, 100, 200],
        tag: 'emergency-alert'
      };
      
    case 'visit_approval':
      return {
        ...baseOptions,
        actions: [
          { action: 'approve', title: '✅ Aprobar', icon: '/static/icons/icon-72.png' },
          { action: 'reject', title: '❌ Rechazar', icon: '/static/icons/icon-72.png' },
          { action: 'view', title: 'Ver Detalles', icon: '/static/icons/icon-72.png' }
        ],
        vibrate: [100, 50, 100],
        tag: 'visit-approval'
      };
      
    case 'maintenance_alert':
      return {
        ...baseOptions,
        actions: [
          { action: 'view', title: '🔧 Ver Reporte', icon: '/static/icons/icon-72.png' },
          { action: 'dismiss', title: 'Cerrar', icon: '/static/icons/icon-72.png' }
        ],
        vibrate: [100],
        tag: 'maintenance-alert'
      };
      
    case 'security_breach':
      return {
        ...baseOptions,
        requireInteraction: true,
        actions: [
          { action: 'view', title: '🛡️ Ver Alerta', icon: '/static/icons/icon-72.png' },
          { action: 'emergency', title: '🚨 Emergencia', icon: '/static/icons/icon-72.png' }
        ],
        vibrate: [200, 100, 200, 100, 200, 100, 200],
        tag: 'security-breach'
      };
      
    default:
      return {
        ...baseOptions,
        actions: [
          { action: 'view', title: 'Ver', icon: '/static/icons/icon-72.png' },
          { action: 'dismiss', title: 'Cerrar', icon: '/static/icons/icon-72.png' }
        ],
        vibrate: [100]
      };
  }
}

// Manejar clics en notificaciones
self.addEventListener('notificationclick', function(event) {
  console.log('👆 SecureCorp SW: Notification click:', event);
  
  event.notification.close();
  
  const action = event.action;
  const notificationData = event.notification.data;
  
  if (action === 'dismiss') {
    return;
  }
  
  let targetUrl = notificationData.url || '/dashboard/';
  
  // Manejar acciones especiales
  switch (action) {
    case 'approve':
      targetUrl = `/api/visits/${notificationData.id}/approve/`;
      handleQuickAction('approve', notificationData.id);
      break;
      
    case 'reject':
      targetUrl = `/api/visits/${notificationData.id}/reject/`;
      handleQuickAction('reject', notificationData.id);
      break;
      
    case 'emergency':
      targetUrl = '/emergencia/';
      break;
      
    case 'view':
    default:
      // Usar URL por defecto
      break;
  }
  
  // Abrir o enfocar ventana
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(clientList => {
        // Buscar ventana ya abierta
        for (const client of clientList) {
          if (client.url.includes(new URL(targetUrl, self.location).pathname) && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Abrir nueva ventana si no existe
        if (clients.openWindow) {
          return clients.openWindow(targetUrl);
        }
      })
  );
});

// Manejar acciones rápidas sin abrir ventana
async function handleQuickAction(action, visitId) {
  try {
    const response = await fetch(`/api/visits/${visitId}/${action}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include'
    });
    
    if (response.ok) {
      // Mostrar notificación de confirmación
      self.registration.showNotification('SecureCorp', {
        body: `Visita ${action === 'approve' ? 'aprobada' : 'rechazada'} exitosamente`,
        icon: '/static/icons/icon-192.png',
        tag: 'quick-action-result',
        silent: true
      });
    }
  } catch (error) {
    console.error('❌ SecureCorp SW: Error en acción rápida:', error);
  }
}

// Sincronización en segundo plano
self.addEventListener('sync', function(event) {
  console.log('🔄 SecureCorp SW: Background sync:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  try {
    // Sincronizar datos pendientes
    const response = await fetch('/api/sync/', {
      method: 'POST',
      credentials: 'include'
    });
    
    if (response.ok) {
      console.log('✅ SecureCorp SW: Background sync completado');
    }
  } catch (error) {
    console.error('❌ SecureCorp SW: Error en background sync:', error);
  }
}

// Manejar actualizaciones del Service Worker
self.addEventListener('message', function(event) {
  console.log('💬 SecureCorp SW: Mensaje recibido:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

console.log('🚀 SecureCorp Service Worker cargado exitosamente!');
