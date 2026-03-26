/**
 * PhysioMonitor Loading State Manager
 * Features:
 * - Global loading overlay
 * - Skeleton loading UI
 * - Smooth transitions
 * - No UI freezing
 */

class LoadingManager {
    constructor() {
        this.isLoading = false;
        this.loadingCount = 0;
        this.overlayElement = null;
        this.spinnerElement = null;
        
        this.init();
    }
    
    /**
     * Initialize loading manager
     */
    init() {
        this.createLoadingOverlay();
    }
    
    /**
     * Create loading overlay HTML
     */
    createLoadingOverlay() {
        if (document.getElementById('loadingOverlay')) return;
        
        const overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay hidden';
        overlay.innerHTML = `
            <div class="loading-spinner-container">
                <div class="loading-spinner">
                    <div class="spinner-circle"></div>
                </div>
                <p class="loading-text" data-i18n="loading">Loading...</p>
            </div>
        `;
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                transition: opacity 0.3s ease;
                opacity: 1;
            }
            
            .loading-overlay.hidden {
                opacity: 0;
                pointer-events: none;
            }
            
            .loading-spinner-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 20px;
            }
            
            .loading-spinner {
                position: relative;
                width: 50px;
                height: 50px;
            }
            
            .spinner-circle {
                width: 50px;
                height: 50px;
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-top: 4px solid #10b981;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            .loading-text {
                color: white;
                font-size: 14px;
                font-weight: 500;
            }
            
            /* Skeleton Loading */
            .skeleton {
                background: linear-gradient(90deg, 
                    #f3f3f3 25%, 
                    #e0e0e0 50%, 
                    #f3f3f3 75%);
                background-size: 200% 100%;
                animation: skeleton-loading 2s infinite;
            }
            
            @keyframes skeleton-loading {
                0% {
                    background-position: 200% 0;
                }
                100% {
                    background-position: -200% 0;
                }
            }
            
            .skeleton-card {
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            
            .skeleton-line {
                height: 16px;
                background: #e0e0e0;
                border-radius: 4px;
                margin: 10px 0;
                -webkit-animation: skeleton-loading 2s infinite;
                animation: skeleton-loading 2s infinite;
            }
            
            .skeleton-title {
                height: 24px;
                width: 60%;
                margin-bottom: 15px;
            }
            
            .skeleton-text {
                height: 16px;
                width: 100%;
                margin: 10px 0;
            }
        `;
        
        if (!document.querySelector('style[data-loading-styles]')) {
            style.setAttribute('data-loading-styles', 'true');
            document.head.appendChild(style);
        }
        
        document.body.appendChild(overlay);
        this.overlayElement = overlay;
    }
    
    /**
     * Start loading
     * @param {string} message - Loading message
     */
    startLoading(message = null) {
        this.loadingCount++;
        
        if (this.loadingCount > 0 && this.overlayElement) {
            this.overlayElement.classList.remove('hidden');
            
            if (message) {
                const textEl = this.overlayElement.querySelector('.loading-text');
                if (textEl) {
                    textEl.textContent = message;
                }
            }
        }
    }
    
    /**
     * Stop loading
     */
    stopLoading() {
        this.loadingCount = Math.max(0, this.loadingCount - 1);
        
        if (this.loadingCount === 0 && this.overlayElement) {
            this.overlayElement.classList.add('hidden');
        }
    }
    
    /**
     * Create skeleton element
     * @param {string} type - 'card', 'line', 'title'
     * @param {number} lines - Number of lines (for text skeleton)
     */
    createSkeleton(type = 'line', lines = 3) {
        const container = document.createElement('div');
        
        if (type === 'card') {
            container.className = 'skeleton-card';
            container.innerHTML = `
                <div class="skeleton skeleton-title"></div>
                ${Array(lines).fill(0).map(() => 
                    '<div class="skeleton skeleton-text"></div>'
                ).join('')}
            `;
        } else if (type === 'title') {
            container.className = 'skeleton skeleton-title';
        } else {
            container.className = 'skeleton skeleton-text';
        }
        
        return container;
    }
    
    /**
     * Replace element with skeleton
     * @param {HTMLElement} element - Element to replace
     * @param {string} type - Skeleton type
     */
    showSkeletonFor(element, type = 'card') {
        if (!element) return;
        
        const skeleton = this.createSkeleton(type);
        element.style.display = 'none';
        element.parentNode.insertBefore(skeleton, element);
        
        return skeleton;
    }
    
    /**
     * Hide skeleton and show element
     * @param {HTMLElement} element - Original element
     * @param {HTMLElement} skeleton - Skeleton element
     */
    hideSkeletonAndShow(element, skeleton) {
        if (skeleton && skeleton.parentNode) {
            skeleton.parentNode.removeChild(skeleton);
        }
        
        if (element) {
            element.style.display = '';
        }
    }
    
    /**
     * Show loading with timeout
     * @param {number} ms - Duration in milliseconds
     */
    async loadFor(ms) {
        this.startLoading();
        return new Promise(resolve => {
            setTimeout(() => {
                this.stopLoading();
                resolve();
            }, ms);
        });
    }
}

// Create globally accessible instance
const loadingManager = new LoadingManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = loadingManager;
}
