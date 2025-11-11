// Google Maps API Configuration
// Replace with your actual Google Maps API Key from Google Cloud Console

const GOOGLE_MAPS_CONFIG = {
    // 🔑 Get your API key from: https://console.cloud.google.com/apis/credentials
    //API_KEY: 'YOUR_GOOGLE_MAPS_API_KEY_HERE',
    API_KEY: 'AIzaSyAPX4poaKmvCupzp3ZWGP1jgJc26_OTRSg',
    
    // Map configuration
    DEFAULT_CENTER: {
        lat: 18.5204,
        lng: 73.8567  // Pune, India
    },
    
    DEFAULT_ZOOM: 12,
    
    // Route colors for visualization - Bright and distinct colors
    ROUTE_COLORS: {
        fastest: '#FF6B00',        // Dark Orange - Very visible for fastest route
        'eco-friendly': '#006400', // Dark Green - Perfect for eco-friendly route  
        balanced: '#000080'        // Dark Blue - Clear contrast for balanced route
    },
    
    // Libraries to load
    LIBRARIES: ['geometry', 'places'],
    
    // Map options
    MAP_OPTIONS: {
        mapTypeControl: true,
        streetViewControl: true,
        fullscreenControl: true,
        zoomControl: true,
        styles: []  // Custom map styling (optional)
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GOOGLE_MAPS_CONFIG;
}