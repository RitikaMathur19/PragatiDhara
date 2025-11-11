/**
 * API Service for PragatiDhara Backend Integration
 * Handles all communication with the sustainable AI backend
 * Updated for Google Maps Three-Route Strategy integration
 */

const API_BASE_URL = 'http://127.0.0.1:8001/api/v1';

class APIError extends Error {
    constructor(message, status, details) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.details = details;
    }
}

class PragatiDharaAPI {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.timeout = 10000; // 10 seconds timeout
    }

    /**
     * Make HTTP request with error handling and timeout
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            timeout: this.timeout,
            ...options
        };

        // Add request body if provided
        if (options.body && config.method !== 'GET') {
            config.body = JSON.stringify(options.body);
        }

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
                throw new APIError(
                    errorData.message || `HTTP ${response.status}: ${response.statusText}`,
                    response.status,
                    errorData
                );
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new APIError('Request timeout - backend may be starting up', 408);
            }
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError(`Network error: ${error.message}`, 0);
        }
    }

    /**
     * Health Check - Test backend connectivity
     */
    async healthCheck() {
        return this.request('/health');
    }

    /**
     * Get current traffic data
     */
    async getCurrentTraffic() {
        return this.request('/traffic/current');
    }

    /**
     * Optimize routes using backend AI services
     */
    async optimizeRoutes(startNode, endNode, alpha = 1.0, preferences = {}) {
        return this.request('/routes/optimize', {
            method: 'POST',
            body: {
                start_node: startNode,
                end_node: endNode,
                alpha: alpha,
                preferences: preferences
            }
        });
    }

    /**
     * Get energy and sustainability metrics
     */
    async getEnergyMetrics() {
        return this.request('/metrics/energy');
    }

    /**
     * Get service performance metrics
     */
    async getServiceMetrics() {
        return this.request('/metrics/services');
    }
}

// Export singleton instance
export const apiService = new PragatiDharaAPI();
export { APIError };