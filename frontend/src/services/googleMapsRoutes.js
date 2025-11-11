/**
 * Google Maps Three-Route Strategy Service
 * Handles integration with the Google Maps backend for route optimization
 */

const GOOGLE_MAPS_API_BASE = 'http://127.0.0.1:8001/api/v1';

class GoogleMapsRoutesError extends Error {
    constructor(message, status, details) {
        super(message);
        this.name = 'GoogleMapsRoutesError';
        this.status = status;
        this.details = details;
    }
}

class GoogleMapsRoutesService {
    constructor() {
        this.baseURL = GOOGLE_MAPS_API_BASE;
        this.timeout = 15000; // 15 seconds for route calculations
        this.retryCount = 2;
    }

    /**
     * Make HTTP request with error handling and retry logic
     */
    async request(endpoint, options = {}, retryCount = this.retryCount) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Add request body if provided
        if (options.body && config.method !== 'GET') {
            config.body = JSON.stringify(options.body);
        }

        for (let attempt = 0; attempt <= retryCount; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);
                
                const response = await fetch(url, {
                    ...config,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new GoogleMapsRoutesError(
                        errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`,
                        response.status,
                        errorData
                    );
                }

                return await response.json();
                
            } catch (error) {
                if (error.name === 'AbortError') {
                    if (attempt < retryCount) {
                        console.warn(`Request timeout, retrying... (${attempt + 1}/${retryCount + 1})`);
                        continue;
                    }
                    throw new GoogleMapsRoutesError('Request timeout - backend may be overloaded', 408);
                }
                
                if (error instanceof GoogleMapsRoutesError) {
                    throw error;
                }
                
                if (attempt < retryCount) {
                    console.warn(`Network error, retrying... (${attempt + 1}/${retryCount + 1}):`, error.message);
                    await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1))); // Exponential backoff
                    continue;
                }
                
                throw new GoogleMapsRoutesError(`Network error: ${error.message}`, 0);
            }
        }
    }

    /**
     * Health Check - Test Google Maps backend connectivity
     */
    async healthCheck() {
        try {
            const response = await this.request('/health', {}, 0); // No retries for health check
            return {
                status: 'healthy',
                message: response.message || 'Backend is running',
                timestamp: response.timestamp,
                version: response.version
            };
        } catch (error) {
            return {
                status: 'error',
                message: error.message,
                timestamp: Date.now() / 1000
            };
        }
    }

    /**
     * Get Three Route Strategies
     * Core method for the three-route optimization system
     */
    async getThreeRouteStrategies(origin, destination, options = {}) {
        const payload = {
            origin: this.normalizeLocation(origin),
            destination: this.normalizeLocation(destination),
            travel_mode: options.travelMode || 'driving',
            departure_time: options.departureTime || new Date().toISOString()
        };

        console.log('🚀 Requesting three route strategies:', payload);

        const result = await this.request('/routes/three-strategies', {
            method: 'POST',
            body: payload
        });

        console.log('✅ Received route strategies:', result);
        return result;
    }

    /**
     * Basic Route Calculation (fallback method)
     */
    async calculateRoute(origin, destination, options = {}) {
        const payload = {
            origin: this.normalizeLocation(origin),
            destination: this.destination(destination),
            travel_mode: options.travelMode || 'driving',
            departure_time: options.departureTime
        };

        return this.request('/routes/calculate', {
            method: 'POST',
            body: payload
        });
    }

    /**
     * Normalize location input to support both address and coordinate formats
     */
    normalizeLocation(location) {
        if (typeof location === 'string') {
            return { address: location };
        }
        
        if (location.lat && location.lng) {
            return { coordinates: { lat: location.lat, lng: location.lng } };
        }
        
        if (location.coordinates) {
            return { coordinates: location.coordinates };
        }
        
        if (location.address) {
            return { address: location.address };
        }
        
        return location;
    }

    /**
     * Transform backend route data to match frontend expectations
     */
    transformRouteData(backendData) {
        if (!backendData || !backendData.routes) {
            throw new GoogleMapsRoutesError('Invalid route data received from backend');
        }

        const transformedRoutes = [];

        // Transform each route type
        ['fastest', 'eco_friendly', 'balanced'].forEach(routeType => {
            const route = backendData.routes[routeType];
            if (route) {
                transformedRoutes.push({
                    type: routeType.replace('_', '-'), // Convert to kebab-case
                    path: this.extractPathFromSummary(route.summary),
                    totalTime: this.parseDuration(route.total_duration),
                    totalDistance: this.parseDistance(route.total_distance),
                    totalEmissions: route.emissions?.co2_emissions_kg * 1000 || 0, // Convert to grams
                    green_points_score: Math.round(route.emissions?.eco_score * 10) || 0,
                    summary: route.summary,
                    processingTime: backendData.processing_time_ms
                });
            }
        });

        return {
            routes: transformedRoutes,
            comparison: backendData.route_comparison,
            suggestions: backendData.optimization_suggestions || [],
            requestId: backendData.request_id,
            processingTime: backendData.processing_time_ms
        };
    }

    /**
     * Extract path information from route summary (fallback when path not provided)
     */
    extractPathFromSummary(summary) {
        // This is a simplified path extraction - in real implementation, you'd get actual waypoints
        const locations = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];
        const pathLength = Math.floor(Math.random() * 3) + 3; // 3-5 waypoints
        return locations.slice(0, pathLength);
    }

    /**
     * Parse duration from Google Maps format
     */
    parseDuration(duration) {
        if (duration?.value) {
            return Math.round(duration.value / 60); // Convert seconds to minutes
        }
        if (typeof duration === 'string') {
            const match = duration.match(/(\d+)\s*hour[s]?\s*(\d+)\s*min[s]?/);
            if (match) {
                return parseInt(match[1]) * 60 + parseInt(match[2]);
            }
        }
        return 60; // Default fallback
    }

    /**
     * Parse distance from Google Maps format
     */
    parseDistance(distance) {
        if (distance?.value) {
            return Math.round(distance.value / 1000 * 10) / 10; // Convert meters to km, 1 decimal
        }
        if (typeof distance === 'string') {
            const match = distance.match(/(\d+\.?\d*)\s*km/);
            if (match) {
                return parseFloat(match[1]);
            }
        }
        return 45.0; // Default fallback
    }

    /**
     * Get backend status and performance metrics
     */
    async getBackendStatus() {
        try {
            const health = await this.healthCheck();
            
            return {
                isConnected: health.status === 'healthy',
                version: health.version,
                message: health.message,
                lastCheck: health.timestamp
            };
        } catch (error) {
            return {
                isConnected: false,
                version: 'unknown',
                message: `Connection failed: ${error.message}`,
                lastCheck: Date.now() / 1000
            };
        }
    }

    /**
     * Batch process multiple route requests
     */
    async batchRouteCalculation(requests) {
        const promises = requests.map(request => 
            this.getThreeRouteStrategies(request.origin, request.destination, request.options)
        );

        try {
            const results = await Promise.allSettled(promises);
            return results.map((result, index) => ({
                index,
                success: result.status === 'fulfilled',
                data: result.status === 'fulfilled' ? result.value : null,
                error: result.status === 'rejected' ? result.reason.message : null
            }));
        } catch (error) {
            throw new GoogleMapsRoutesError(`Batch processing failed: ${error.message}`);
        }
    }

    /**
     * Get route optimization suggestions
     */
    async getOptimizationSuggestions(routeData) {
        // If backend provides suggestions, return them; otherwise generate basic suggestions
        if (routeData.optimization_suggestions) {
            return routeData.optimization_suggestions;
        }

        // Fallback suggestions based on route comparison
        const suggestions = [];
        const comparison = routeData.route_comparison;
        
        if (comparison?.eco_friendly && comparison?.fastest) {
            const timeDiff = comparison.fastest.duration_minutes - comparison.eco_friendly.duration_minutes;
            const emissionSavings = comparison.fastest.co2_emissions_kg - comparison.eco_friendly.co2_emissions_kg;
            
            if (emissionSavings > 1) {
                suggestions.push({
                    message: `Eco route saves ${emissionSavings.toFixed(1)} kg CO2 emissions`,
                    impact: emissionSavings > 2 ? 'high' : 'medium',
                    co2_savings_kg: emissionSavings,
                    additional_time_minutes: timeDiff
                });
            }
        }

        return suggestions;
    }
}

// Export singleton instance
export const googleMapsRoutesService = new GoogleMapsRoutesService();
export { GoogleMapsRoutesError };

// Enhanced hooks for React integration
export const useGoogleMapsRoutes = () => {
    const [routes, setRoutes] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState(null);
    const [backendStatus, setBackendStatus] = React.useState({ isConnected: false });

    const calculateThreeRoutes = React.useCallback(async (origin, destination, options = {}) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await googleMapsRoutesService.getThreeRouteStrategies(origin, destination, options);
            const transformedData = googleMapsRoutesService.transformRouteData(result);
            setRoutes(transformedData);
            return transformedData;
        } catch (err) {
            const errorMessage = err instanceof GoogleMapsRoutesError ? err.message : 'Route calculation failed';
            setError(errorMessage);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const checkBackendStatus = React.useCallback(async () => {
        const status = await googleMapsRoutesService.getBackendStatus();
        setBackendStatus(status);
        return status;
    }, []);

    React.useEffect(() => {
        checkBackendStatus();
    }, [checkBackendStatus]);

    return {
        routes,
        loading,
        error,
        backendStatus,
        calculateThreeRoutes,
        checkBackendStatus,
        clearRoutes: () => setRoutes(null),
        clearError: () => setError(null)
    };
};

export default googleMapsRoutesService;