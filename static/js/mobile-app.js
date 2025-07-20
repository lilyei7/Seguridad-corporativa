// JavaScript para interacciones móviles tipo app nativa

class MobileAppManager {
    constructor() {
        this.initializeApp();
        this.setupGestures();
        this.setupPullToRefresh();
        this.setupHapticFeedback();
        this.setupTabNavigation();
        this.initializeAnimations();
    }

    initializeApp() {
        // Detectar si es móvil
        this.isMobile = window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        if (this.isMobile) {
            document.body.classList.add('mobile-app');
            this.preventZoom();
            this.setupViewportHeight();
        }

        // Prevenir zoom en inputs
        document.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
    }

    preventZoom() {
        // Prevenir zoom con gestos
        document.addEventListener('gesturestart', (e) => e.preventDefault());
        document.addEventListener('gesturechange', (e) => e.preventDefault());
        document.addEventListener('gestureend', (e) => e.preventDefault());
    }

    setupViewportHeight() {
        // Ajustar altura para móviles con barras de navegación
        const setViewportHeight = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };

        setViewportHeight();
        window.addEventListener('resize', setViewportHeight);
        window.addEventListener('orientationchange', setViewportHeight);
    }

    setupGestures() {
        let startX, startY, currentX, currentY;
        let isScrolling = false;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isScrolling = false;
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;

            currentX = e.touches[0].clientX;
            currentY = e.touches[0].clientY;

            const diffX = startX - currentX;
            const diffY = startY - currentY;

            if (Math.abs(diffX) > Math.abs(diffY)) {
                // Swipe horizontal
                if (!isScrolling) {
                    if (diffX > 50) {
                        this.handleSwipeLeft();
                    } else if (diffX < -50) {
                        this.handleSwipeRight();
                    }
                }
            }
            isScrolling = true;
        }, { passive: true });

        document.addEventListener('touchend', () => {
            startX = null;
            startY = null;
            isScrolling = false;
        }, { passive: true });
    }

    handleSwipeLeft() {
        console.log('Swipe left detected');
        // Navegar a la siguiente pestaña
        this.navigateTab('next');
    }

    handleSwipeRight() {
        console.log('Swipe right detected');
        // Navegar a la pestaña anterior
        this.navigateTab('previous');
    }

    navigateTab(direction) {
        const tabs = document.querySelectorAll('.mobile-nav-item');
        const activeTab = document.querySelector('.mobile-nav-item.active');
        
        if (!activeTab || tabs.length === 0) return;

        const currentIndex = Array.from(tabs).indexOf(activeTab);
        let newIndex;

        if (direction === 'next') {
            newIndex = (currentIndex + 1) % tabs.length;
        } else {
            newIndex = (currentIndex - 1 + tabs.length) % tabs.length;
        }

        tabs[newIndex].click();
    }

    setupPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        let isRefreshing = false;
        let pullDistance = 0;
        const threshold = 100;

        const refreshIndicator = this.createRefreshIndicator();

        document.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (window.scrollY > 0 || isRefreshing) return;

            currentY = e.touches[0].clientY;
            pullDistance = currentY - startY;

            if (pullDistance > 0) {
                e.preventDefault();
                const opacity = Math.min(pullDistance / threshold, 1);
                refreshIndicator.style.opacity = opacity;
                refreshIndicator.style.transform = `translateX(-50%) translateY(${Math.min(pullDistance / 2, 50)}px)`;

                if (pullDistance > threshold) {
                    refreshIndicator.classList.add('ready');
                } else {
                    refreshIndicator.classList.remove('ready');
                }
            }
        });

        document.addEventListener('touchend', () => {
            if (pullDistance > threshold && !isRefreshing) {
                this.performRefresh(refreshIndicator);
            } else {
                this.resetRefreshIndicator(refreshIndicator);
            }
            pullDistance = 0;
        });
    }

    createRefreshIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'pull-to-refresh';
        indicator.innerHTML = `
            <div class="loading-spinner"></div>
            <span>Actualizar</span>
        `;
        document.body.appendChild(indicator);
        return indicator;
    }

    performRefresh(indicator) {
        indicator.classList.add('refreshing');
        indicator.querySelector('span').textContent = 'Actualizando...';

        // Simular actualización
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }

    resetRefreshIndicator(indicator) {
        indicator.style.opacity = '0';
        indicator.style.transform = 'translateX(-50%) translateY(-60px)';
        indicator.classList.remove('ready', 'refreshing');
        indicator.querySelector('span').textContent = 'Actualizar';
    }

    setupHapticFeedback() {
        // Simular feedback háptico en dispositivos compatibles
        const hapticElements = document.querySelectorAll('.haptic-light, .haptic-medium, .haptic-heavy');
        
        hapticElements.forEach(element => {
            element.addEventListener('touchstart', () => {
                if (navigator.vibrate) {
                    const intensity = element.classList.contains('haptic-heavy') ? [10, 50, 10] :
                                    element.classList.contains('haptic-medium') ? [20] : [10];
                    navigator.vibrate(intensity);
                }
            }, { passive: true });
        });
    }

    setupTabNavigation() {
        const tabItems = document.querySelectorAll('.mobile-nav-item');
        
        tabItems.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remover active de todos los tabs
                tabItems.forEach(t => t.classList.remove('active'));
                
                // Agregar active al tab clickeado
                tab.classList.add('active');
                
                // Haptic feedback
                if (navigator.vibrate) {
                    navigator.vibrate(10);
                }

                // Navegar a la URL
                const href = tab.getAttribute('href');
                if (href && href !== '#') {
                    this.navigateWithAnimation(href);
                }
            });
        });
    }

    navigateWithAnimation(url) {
        // Agregar loading state
        document.body.classList.add('page-transitioning');
        
        // Simular transición
        setTimeout(() => {
            window.location.href = url;
        }, 150);
    }

    initializeAnimations() {
        // Animar elementos cuando entran en viewport
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observar cards y elementos animables
        const animatableElements = document.querySelectorAll('.ios-card, .ios-list-item');
        animatableElements.forEach(el => {
            el.classList.add('animate-on-scroll');
            observer.observe(el);
        });
    }

    handleTouchStart(e) {
        // Prevenir zoom en inputs
        if (e.target.tagName === 'INPUT') {
            e.target.addEventListener('blur', () => {
                setTimeout(() => {
                    window.scrollTo(0, 0);
                }, 100);
            }, { once: true });
        }
    }

    // Método para mostrar notificaciones tipo toast
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">${this.getToastIcon(type)}</span>
                <span class="toast-message">${message}</span>
            </div>
        `;

        document.body.appendChild(toast);

        // Animar entrada
        setTimeout(() => toast.classList.add('show'), 100);

        // Remover después de 3 segundos
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    getToastIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    // Método para mostrar action sheet
    showActionSheet(options) {
        const actionSheet = document.createElement('div');
        actionSheet.className = 'action-sheet';
        
        let itemsHTML = '';
        options.items.forEach(item => {
            itemsHTML += `
                <div class="action-sheet-item ${item.destructive ? 'destructive' : ''}" 
                     onclick="${item.action}">
                    ${item.title}
                </div>
            `;
        });

        actionSheet.innerHTML = `
            ${itemsHTML}
            <div class="action-sheet-item action-sheet-cancel" onclick="this.parentElement.remove()">
                Cancelar
            </div>
        `;

        document.body.appendChild(actionSheet);
        setTimeout(() => actionSheet.classList.add('active'), 100);

        // Cerrar al tocar fuera
        actionSheet.addEventListener('click', (e) => {
            if (e.target === actionSheet) {
                actionSheet.classList.remove('active');
                setTimeout(() => actionSheet.remove(), 300);
            }
        });
    }
}

// Estilos CSS adicionales para las animaciones
const additionalStyles = `
    .toast {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%) translateY(-100px);
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        z-index: 10000;
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    
    .toast.show {
        transform: translateX(-50%) translateY(0);
        opacity: 1;
    }
    
    .toast-content {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .toast-success {
        background: rgba(16, 185, 129, 0.95);
    }
    
    .toast-error {
        background: rgba(239, 68, 68, 0.95);
    }
    
    .toast-warning {
        background: rgba(245, 158, 11, 0.95);
    }
    
    .animate-on-scroll {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .animate-in {
        opacity: 1;
        transform: translateY(0);
    }
    
    .page-transitioning {
        overflow: hidden;
    }
    
    .page-transitioning * {
        pointer-events: none;
    }
    
    @media (max-width: 768px) {
        .mobile-app {
            height: calc(var(--vh, 1vh) * 100);
            overflow-x: hidden;
        }
    }
`;

// Agregar estilos al documento
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Inicializar la app móvil cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.mobileApp = new MobileAppManager();
});

// Exportar para uso global
window.MobileAppManager = MobileAppManager;
