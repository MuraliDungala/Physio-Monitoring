/**
 * PhysioMonitor - Smart Frontend Configuration & API Connection Manager
 * Supports Local Development, Vercel Static Frontend, and Render Cloud Backend
 */

(function () {
    const DEFAULT_LOCAL_URL = 'http://localhost:8000';
    const DEFAULT_RENDER_URL = 'https://physio-monitoring-backend1.onrender.com';

    function cleanUrl(url) {
        if (!url) return '';
        return url.trim().replace(/\/+$/, '');
    }

    function resolveInitialApiBase() {
        const hostname = window.location.hostname || '';
        const protocol = window.location.protocol || '';
        const isLocalHost = (
            hostname === 'localhost' ||
            hostname === '127.0.0.1' ||
            hostname === '0.0.0.0' ||
            protocol === 'file:' ||
            hostname.endsWith('.local')
        );

        const savedUrl = localStorage.getItem('API_BASE_URL');

        // If running locally, prefer local backend unless user specifically set a custom local address
        if (isLocalHost) {
            if (savedUrl && !savedUrl.includes('localhost') && !savedUrl.includes('127.0.0.1')) {
                console.warn('🧹 Resetting stale remote API_BASE_URL from localStorage for local development:', savedUrl);
                localStorage.removeItem('API_BASE_URL');
            } else if (savedUrl && (savedUrl.includes('localhost') || savedUrl.includes('127.0.0.1'))) {
                return cleanUrl(savedUrl);
            }
            return DEFAULT_LOCAL_URL;
        }

        // If on production / deployed domain (e.g. Vercel)
        if (savedUrl && savedUrl.trim()) {
            return cleanUrl(savedUrl);
        }

        if (typeof window.__API_BASE_URL__ !== 'undefined' && window.__API_BASE_URL__) {
            return cleanUrl(window.__API_BASE_URL__);
        }

        return DEFAULT_RENDER_URL;
    }

    const currentApiBase = resolveInitialApiBase();
    window.API_BASE_URL = currentApiBase;
    window.API_BASE = currentApiBase;
    window.DEFAULT_LOCAL_URL = DEFAULT_LOCAL_URL;
    window.DEFAULT_RENDER_URL = DEFAULT_RENDER_URL;

    /**
     * Get current API base URL
     */
    window.getAPIBaseURL = function () {
        return cleanUrl(window.API_BASE_URL || window.API_BASE || DEFAULT_LOCAL_URL);
    };

    /**
     * Set and save API base URL
     */
    window.setAPIBaseURL = function (newUrl) {
        const cleaned = cleanUrl(newUrl);
        if (!cleaned) return;
        localStorage.setItem('API_BASE_URL', cleaned);
        window.API_BASE_URL = cleaned;
        window.API_BASE = cleaned;
        console.log('🔄 API Base URL updated to:', cleaned);
        window.dispatchEvent(new CustomEvent('api-base-changed', { detail: { url: cleaned } }));
    };

    /**
     * Test connection to a specific backend URL
     */
    window.testBackendConnection = async function (targetUrl) {
        const base = cleanUrl(targetUrl || window.getAPIBaseURL());
        const startTime = performance.now();
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 12000); // 12 second timeout

        try {
            const resp = await fetch(`${base}/health`, {
                method: 'GET',
                signal: controller.signal,
                headers: { 'Accept': 'application/json' }
            });
            clearTimeout(timeoutId);
            const latency = Math.round(performance.now() - startTime);

            if (resp.ok) {
                const data = await resp.json().catch(() => ({}));
                return {
                    ok: true,
                    status: resp.status,
                    latency,
                    url: base,
                    data: data
                };
            } else {
                return {
                    ok: false,
                    status: resp.status,
                    latency,
                    url: base,
                    error: `Server returned HTTP ${resp.status}`
                };
            }
        } catch (err) {
            clearTimeout(timeoutId);
            const latency = Math.round(performance.now() - startTime);
            const isTimeout = err.name === 'AbortError';
            return {
                ok: false,
                status: 0,
                latency,
                url: base,
                isTimeout,
                error: isTimeout
                    ? 'Connection timed out (Render free tier may still be waking up - wait 30s and retry)'
                    : (err.message || 'Unable to connect to server')
            };
        }
    };

    console.log('🔧 Frontend Config loaded. Active API_BASE:', window.API_BASE);
})();
