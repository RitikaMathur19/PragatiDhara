/**
 * Custom React Hooks for Backend Integration
 * Provides state management and API integration for sustainable AI features
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiService, APIError } from '../services/api';

/**
 * Hook for managing API request states
 */
export const useApiRequest = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);

    const execute = useCallback(async (apiCall) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await apiCall();
            setData(result);
            return result;
        } catch (err) {
            const errorMessage = err instanceof APIError 
                ? err.message 
                : 'An unexpected error occurred';
            setError(errorMessage);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const reset = useCallback(() => {
        setLoading(false);
        setError(null);
        setData(null);
    }, []);

    return { loading, error, data, execute, reset };
};

/**
 * Hook for real-time traffic data
 */
export const useTrafficData = (interval = 3000) => {
    const [trafficData, setTrafficData] = useState({
        traffic_factor: 0.5,
        incident_factor: 0.2,
        timestamp: Date.now() / 1000
    });
    const [isOnline, setIsOnline] = useState(true);
    const intervalRef = useRef();

    const fetchTrafficData = useCallback(async () => {
        try {
            const data = await apiService.getCurrentTraffic();
            setTrafficData(data);
            setIsOnline(true);
        } catch (error) {
            console.warn('Failed to fetch traffic data, using simulated data:', error.message);
            setIsOnline(false);
            
            // Fallback to simulated data
            setTrafficData(prev => ({
                traffic_factor: Math.max(0.1, Math.min(1.0, prev.traffic_factor + (Math.random() - 0.5) * 0.1)),
                incident_factor: Math.max(0.0, Math.min(1.0, prev.incident_factor + (Math.random() - 0.5) * 0.05)),
                timestamp: Date.now() / 1000
            }));
        }
    }, []);

    useEffect(() => {
        fetchTrafficData(); // Initial fetch
        
        if (interval > 0) {
            intervalRef.current = setInterval(fetchTrafficData, interval);
        }

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, [fetchTrafficData, interval]);

    return { trafficData, isOnline, refetch: fetchTrafficData };
};

/**
 * Hook for route optimization with backend AI
 */
export const useRouteOptimization = () => {
    const { loading, error, execute } = useApiRequest();
    const [routes, setRoutes] = useState(null);
    const [processingTime, setProcessingTime] = useState(0);

    const optimizeRoutes = useCallback(async (startNode, endNode, alpha) => {
        const startTime = Date.now();
        
        try {
            const result = await execute(() => 
                apiService.optimizeRoutes(startNode, endNode, alpha)
            );
            
            setRoutes(result.routes);
            setProcessingTime(Date.now() - startTime);
            
            return result;
        } catch (err) {
            // Fallback to client-side simulation if backend fails
            console.warn('Backend optimization failed, using fallback:', err.message);
            
            const fallbackRoutes = generateFallbackRoutes(startNode, endNode, alpha);
            setRoutes(fallbackRoutes);
            setProcessingTime(Date.now() - startTime);
            
            return { routes: fallbackRoutes, recommendation: 'eco', sustainability_score: 85 };
        }
    }, [execute]);

    return {
        routes,
        loading,
        error,
        processingTime,
        optimizeRoutes,
        clearRoutes: () => setRoutes(null)
    };
};

/**
 * Hook for energy metrics monitoring
 */
export const useEnergyMetrics = (interval = 5000) => {
    const [metrics, setMetrics] = useState({
        cpu_usage_percent: 0,
        memory_usage_percent: 0,
        energy_efficiency_score: 100,
        sustainability_grade: 'A+'
    });
    const [isConnected, setIsConnected] = useState(true);

    const fetchMetrics = useCallback(async () => {
        try {
            const data = await apiService.getEnergyMetrics();
            setMetrics(data);
            setIsConnected(true);
        } catch (error) {
            console.warn('Failed to fetch energy metrics:', error.message);
            setIsConnected(false);
            
            // Simulate metrics when backend unavailable
            setMetrics(prev => ({
                cpu_usage_percent: Math.max(5, Math.min(50, prev.cpu_usage_percent + (Math.random() - 0.5) * 10)),
                memory_usage_percent: Math.max(20, Math.min(80, prev.memory_usage_percent + (Math.random() - 0.5) * 5)),
                energy_efficiency_score: Math.max(70, Math.min(100, prev.energy_efficiency_score + (Math.random() - 0.5) * 5)),
                sustainability_grade: prev.energy_efficiency_score > 90 ? 'A+' : prev.energy_efficiency_score > 80 ? 'A' : 'B'
            }));
        }
    }, []);

    useEffect(() => {
        fetchMetrics(); // Initial fetch
        
        const intervalId = setInterval(fetchMetrics, interval);
        return () => clearInterval(intervalId);
    }, [fetchMetrics, interval]);

    return { metrics, isConnected, refetch: fetchMetrics };
};

/**
 * Hook for backend health monitoring
 */
export const useBackendHealth = () => {
    const [health, setHealth] = useState({
        status: 'checking',
        message: 'Checking backend connection...',
        timestamp: null
    });

    const checkHealth = useCallback(async () => {
        try {
            const result = await apiService.healthCheck();
            setHealth({
                status: 'healthy',
                message: result.message || 'Backend is running sustainably!',
                timestamp: result.timestamp
            });
            return true;
        } catch (error) {
            setHealth({
                status: 'error',
                message: error.message || 'Backend connection failed',
                timestamp: Date.now() / 1000
            });
            return false;
        }
    }, []);

    useEffect(() => {
        checkHealth();
    }, [checkHealth]);

    return { health, checkHealth };
};

/**
 * Fallback route generation when backend is unavailable
 */
function generateFallbackRoutes(startNode, endNode, alpha) {
    const locationLabels = {
        A: 'Katraj (South)', B: 'Swargate', C: 'Deccan Gymkhana',
        D: 'Shivajinagar', E: 'University Circle', F: 'Kothrud Bypass',
        G: 'Balewadi Stadium', H: 'Baner', I: 'Wakad', J: 'Hinjawadi Ph 1'
    };

    // Simple fallback routes
    return [
        {
            path: [startNode, 'D', endNode],
            total_time: 15.0 + Math.random() * 5,
            total_distance: 20.0 + Math.random() * 10,
            total_emissions: 800 + Math.random() * 200,
            green_points_score: 85,
            route_type: 'fast',
            processing_time_ms: 25.0,
            cache_hit: false
        },
        {
            path: [startNode, 'F', 'H', endNode],
            total_time: 18.0 + Math.random() * 3,
            total_distance: 25.0 + Math.random() * 5,
            total_emissions: 400 + Math.random() * 100,
            green_points_score: 95,
            route_type: 'eco',
            processing_time_ms: 30.0,
            cache_hit: false
        },
        {
            path: [startNode, 'E', endNode],
            total_time: 16.5 + Math.random() * 2,
            total_distance: 22.0 + Math.random() * 3,
            total_emissions: 600 + Math.random() * 150,
            green_points_score: 90,
            route_type: 'rl-optimized',
            processing_time_ms: 28.0,
            cache_hit: false
        }
    ].sort((a, b) => b.green_points_score - a.green_points_score);
}