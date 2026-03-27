// Frontend Configuration
// Load environment variables based on deployment

const API_BASE_URL = (() => {
    // Check if API URL is already set by environment (e.g., via Vercel env)
    if (window.__API_BASE_URL__) {
        return window.__API_BASE_URL__;
    }
    
    // Detect environment
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // Production domains
    if (protocol === 'https:') {
        // For Vercel deployment, use the hardcoded Render backend URL
        if (hostname.includes('vercel.app')) {
            return 'https://physio-monitoring-backend.onrender.com';
        }
        
        // Fallback to same host (when deployed with backend)
        return `${protocol}//${hostname}`;
    }
    
    // Development/Local
    return `http://${hostname}:8000`;
})();

// Export for use in other modules
window.API_BASE_URL = API_BASE_URL;
console.log('📡 API Base URL:', window.API_BASE_URL);

// Log configuration on startup
console.log('🔧 Frontend Configuration:');
console.log(`   API Base URL: ${API_BASE_URL}`);
console.log(`   Environment: ${window.location.hostname.includes('localhost') ? 'development' : 'production'}`);
console.log(`   Hostname: ${window.location.hostname}`);
