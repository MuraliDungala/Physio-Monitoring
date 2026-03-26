// Frontend Configuration
// Load environment variables based on deployment

const API_BASE_URL = (() => {
    // Detect environment
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // Production domains
    if (protocol === 'https:') {
        // Use environment variable or API domain
        const apiUrl = process.env.REACT_APP_API_URL || 
                      process.env.VUE_APP_API_URL ||
                      process.env.NEXT_PUBLIC_API_URL;
        
        if (apiUrl) {
            return apiUrl;
        }
        
        // Fallback to same host (when deployed with backend)
        return `${protocol}//${hostname}`;
    }
    
    // Development/Local
    return `http://${hostname}:8000`;
})();

// Export for use in other modules
window.API_BASE_URL = API_BASE_URL;

// Log configuration on startup
console.log('🔧 Frontend Configuration:');
console.log(`   API Base URL: ${API_BASE_URL}`);
console.log(`   Environment: ${process.env.NODE_ENV || 'development'}`);
console.log(`   Hostname: ${window.location.hostname}`);
