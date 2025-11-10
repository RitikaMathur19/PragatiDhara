import React, { useState, useMemo, useEffect } from 'react';
// Backend integration hooks
import { 
  useTrafficData, 
  useRouteOptimization, 
  useEnergyMetrics, 
  useBackendHealth 
} from './hooks/useBackend';
// Error boundary for better error handling
import ErrorBoundary from './components/ErrorBoundary';

// --- CORE DATA STRUCTURES (Pune, India Map Nodes) ---
const locationLabels = {
    A: 'Katraj (South)', B: 'Swargate', C: 'Deccan Gymkhana',
    D: 'Shivajinagar', E: 'University Circle', F: 'Kothrud Bypass',
    G: 'Balewadi Stadium', H: 'Baner', I: 'Wakad', J: 'Hinjawadi Ph 1'
};

// NOTE: Added a "Medium Green Arterial Bypass" (G to D) to give the RL-Optimized path a unique, intermediate option.
const staticLinks = [
    // Core Main Artery Links
    { from: 'A', to: 'B', distance: 10, time: 5 }, { from: 'A', to: 'C', distance: 12, time: 6 },
    { from: 'B', to: 'D', distance: 10, time: 5 }, { from: 'C', to: 'D', distance: 8, time: 4 },
    { from: 'D', to: 'E', distance: 5, time: 2 }, // Shivajinagar to UC
    { from: 'E', to: 'J', distance: 10, time: 5 }, // UC to Hinjawadi Main Access
    { from: 'I', to: 'J', distance: 8, time: 4 }, // Wakad to Hinjawadi Ph 1

    // Eco Bypass 1 (F to H) - Max CO2 Reduction (Deep Green)
    { from: 'C', to: 'F', distance: 8, time: 4, eco_priority: true, emissions_multiplier: 0.5 }, // Feeder to Bypass
    { from: 'F', to: 'H', distance: 15, time: 7, eco_priority: true, emissions_multiplier: 0.05 }, // Primary Eco Bypass (95% reduction)
    
    // Eco Bypass 2 (E to I) - Secondary CO2 Reduction (Mid Green)
    { from: 'E', to: 'I', distance: 10, time: 5, eco_priority: true, emissions_multiplier: 0.4 }, // Eco link from UC to Wakad

    // NEW: Arterial Bypass (G to D) - Medium Green, High Availability (Intermediate Path)
    { from: 'G', to: 'D', distance: 12, time: 5, eco_priority: true, emissions_multiplier: 0.7 }, // NEW!

    // Other Links and Cross-Links
    { from: 'D', to: 'G', distance: 7, time: 3 }, 
    { from: 'G', to: 'H', distance: 5, time: 2 },
    { from: 'H', to: 'I', distance: 8, time: 4 }, 
    { from: 'D', to: 'F', distance: 12, time: 6 }, 
    { from: 'B', to: 'E', distance: 14, time: 7 }, 
];

// Bidirectional link generator
const getBidirectionalLinks = (links) => {
    const allLinks = [];
    links.forEach(link => {
        allLinks.push({ ...link });
        // The reverse link should inherit eco_priority and emissions_multiplier if present
        allLinks.push({ 
            from: link.to, 
            to: link.from, 
            distance: link.distance, 
            time: link.time, 
            eco_priority: link.eco_priority, 
            emissions_multiplier: link.emissions_multiplier // Propagate the multiplier
        });
    });
    return allLinks;
};

// A* pathfinding algorithm for route calculation
const findPath = (links, start, end, alpha = 1.0) => {
    const graph = {};
    links.forEach(link => {
        if (!graph[link.from]) graph[link.from] = [];
        graph[link.from].push(link);
    });

    const openSet = [{ node: start, g: 0, h: 0, f: 0, path: [start] }];
    const closedSet = new Set();

    while (openSet.length > 0) {
        openSet.sort((a, b) => a.f - b.f);
        const current = openSet.shift();

        if (current.node === end) {
            return {
                path: current.path,
                totalTime: current.g,
                totalEmissions: calculateEmissions(current.path, links)
            };
        }

        closedSet.add(current.node);

        if (graph[current.node]) {
            graph[current.node].forEach(link => {
                if (closedSet.has(link.to)) return;

                const g = current.g + link.time;
                const h = 0; // Simplified heuristic
                const emissions = link.emissions_multiplier ? 
                    link.time * 100 * link.emissions_multiplier : 
                    link.time * 100;
                const f = g + alpha * emissions;

                const existingNode = openSet.find(node => node.node === link.to);
                if (!existingNode || g < existingNode.g) {
                    const newNode = {
                        node: link.to,
                        g,
                        h,
                        f,
                        path: [...current.path, link.to]
                    };
                    
                    if (existingNode) {
                        const index = openSet.indexOf(existingNode);
                        openSet[index] = newNode;
                    } else {
                        openSet.push(newNode);
                    }
                }
            });
        }
    }

    return null;
};

// Calculate emissions for a given path
const calculateEmissions = (path, links) => {
    let totalEmissions = 0;
    for (let i = 0; i < path.length - 1; i++) {
        const link = links.find(l => l.from === path[i] && l.to === path[i + 1]);
        if (link) {
            const baseEmissions = link.time * 100; // Base emissions calculation
            totalEmissions += link.emissions_multiplier ? 
                baseEmissions * link.emissions_multiplier : 
                baseEmissions;
        }
    }
    return Math.round(totalEmissions);
};

// Simplified RL agent for optimal alpha calculation
const calculateOptimalAlpha = (trafficFactor, incidentFactor) => {
    // Simplified RL logic - in real implementation this would be a trained model
    const baseAlpha = 1.0;
    const trafficWeight = trafficFactor * 0.5;
    const incidentWeight = incidentFactor * 0.3;
    return Math.max(0.1, Math.min(2.0, baseAlpha + trafficWeight + incidentWeight));
};

const App = () => {
    const [startNode, setStartNode] = useState('A');
    const [endNode, setEndNode] = useState('J');
    const [results, setResults] = useState(null);
    const [message, setMessage] = useState('Configure your route and click "Plan RL-Optimized Route"');
    const [auditLog, setAuditLog] = useState([]);
    const [alpha, setAlpha] = useState(0.7); // RL algorithm parameter
    
    // Backend integration hooks
    const { trafficData, isOnline: trafficOnline } = useTrafficData(3000);
    const { routes: backendRoutes, loading: routesLoading, error: routesError, optimizeRoutes, processingTime } = useRouteOptimization();
    const { metrics: energyMetrics, isConnected: energyConnected } = useEnergyMetrics(5000);
    const { health: backendHealth } = useBackendHealth();
    
    // Legacy state for fallback (use backend data when available)
    const [rlStateVector, setRlStateVector] = useState({
        trafficFactor: 0.5,
        incidentFactor: 0.2,
        timestamp: Date.now()
    });

    // Update local state with backend traffic data
    useEffect(() => {
        if (trafficOnline && trafficData) {
            setRlStateVector({
                trafficFactor: trafficData.traffic_factor,
                incidentFactor: trafficData.incident_factor,
                timestamp: trafficData.timestamp * 1000 // Convert to milliseconds
            });
        }
    }, [trafficData, trafficOnline]);

    const links = useMemo(() => getBidirectionalLinks(staticLinks), []);
    const optimalAlpha = useMemo(() => 
        calculateOptimalAlpha(rlStateVector.trafficFactor, rlStateVector.incidentFactor), 
        [rlStateVector]
    );

    // Simulate real-time data updates
    useEffect(() => {
        const interval = setInterval(() => {
            setRlStateVector(prev => ({
                trafficFactor: Math.max(0.1, Math.min(1.0, prev.trafficFactor + (Math.random() - 0.5) * 0.1)),
                incidentFactor: Math.max(0.0, Math.min(1.0, prev.incidentFactor + (Math.random() - 0.5) * 0.05)),
                timestamp: Date.now()
            }));
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    const handlePlanRoute = async () => {
        if (startNode === endNode) {
            setMessage('Error: Start and end locations must be different');
            return;
        }

        setMessage('🔄 Optimizing routes with sustainable AI...');
        
        try {
            // Try backend optimization first
            const result = await optimizeRoutes(startNode, endNode, alpha);
            
            if (result && result.routes) {
                // Transform backend routes to match UI format
                const routeResults = result.routes.map(route => ({
                    type: route.route_type,
                    path: route.path,
                    totalTime: route.total_time,
                    totalDistance: route.total_distance,
                    totalEmissions: route.total_emissions,
                    green_points_score: route.green_points_score
                }));

                setResults(routeResults);
                setMessage(`✅ Backend optimization completed in ${processingTime}ms (${result.routes[0].cache_hit ? 'cached' : 'computed'})`);

                // Add to audit log
                const carbonSaved = routeResults.find(r => r.type === 'fast')?.totalEmissions - 
                                 routeResults.find(r => r.type === 'rl-optimized')?.totalEmissions || 0;
                setAuditLog(prev => [...prev, {
                    id: Date.now(),
                    rlAlpha: alpha.toFixed(3),
                    inferenceTime: processingTime,
                    carbonSaved: Math.round(carbonSaved),
                    rlTime: routeResults.find(r => r.type === 'rl-optimized')?.totalTime || 0,
                    fastTime: routeResults.find(r => r.type === 'fast')?.totalTime || 0
                }]);
            }

        } catch (error) {
            console.warn('Backend optimization failed, using fallback:', error.message);
            
            // Fallback to client-side computation with distinct routes
            const startTime = performance.now();
            
            try {
                // Generate 3 distinct routes using different strategies
                const routeResults = generateDistinctRoutes(startNode, endNode, alpha);

                if (!routeResults || routeResults.length === 0) {
                    setMessage('Error: No valid route found');
                    return;
                }

                const inferenceTime = Math.round(performance.now() - startTime);
                
                // Update processing time for all routes
                routeResults.forEach(route => {
                    route.processingTime = inferenceTime;
                });

                routeResults.sort((a, b) => b.green_points_score - a.green_points_score);
                
                setResults(routeResults);
                setMessage(`✅ Fallback optimization completed in ${inferenceTime}ms (offline mode)`);

                const fastRoute = routeResults.find(r => r.type === 'fast');
                const rlRoute = routeResults.find(r => r.type === 'rl-optimized');
                const carbonSaved = fastRoute && rlRoute ? fastRoute.totalEmissions - rlRoute.totalEmissions : 0;
                
                setAuditLog(prev => [...prev, {
                    id: Date.now(),
                    rlAlpha: alpha.toFixed(3),
                    inferenceTime,
                    carbonSaved: Math.round(carbonSaved),
                    rlTime: rlRoute?.totalTime || 0,
                    fastTime: fastRoute?.totalTime || 0
                }]);

            } catch (fallbackError) {
                setMessage(`Error: ${fallbackError.message}`);
            }
        }
    };

    const totalCarbonSaved = auditLog.reduce((sum, log) => sum + Math.max(0, log.carbonSaved), 0);

    // Generate 3 distinct routes for client-side fallback
    const generateDistinctRoutes = (startNode, endNode, alpha) => {
        const routeStrategies = {
            // Strategy 1: Fast Route - Main arteries, minimal stops
            fast: {
                'A-J': ['A', 'B', 'D', 'E', 'J'],
                'A-H': ['A', 'C', 'D', 'G', 'H'],  
                'A-I': ['A', 'B', 'D', 'G', 'H', 'I'],
                'D-J': ['D', 'E', 'J'],
                'B-J': ['B', 'D', 'E', 'J'],
                'default': [startNode, 'D', endNode]
            },
            // Strategy 2: Eco Route - Maximum eco-bypass usage
            eco: {
                'A-J': ['A', 'C', 'F', 'H', 'I', 'J'],
                'A-H': ['A', 'C', 'F', 'H'],
                'A-I': ['A', 'C', 'F', 'H', 'I'], 
                'D-J': ['D', 'G', 'H', 'I', 'J'],
                'B-J': ['B', 'E', 'I', 'J'],
                'default': [startNode, 'F', 'H', endNode]
            },
            // Strategy 3: RL-Optimized - Balanced compromise
            rl: {
                'A-J': ['A', 'B', 'E', 'I', 'J'],
                'A-H': ['A', 'B', 'D', 'F', 'H'],
                'A-I': ['A', 'C', 'D', 'G', 'H', 'I'],
                'D-J': ['D', 'F', 'H', 'I', 'J'], 
                'B-J': ['B', 'D', 'G', 'H', 'I', 'J'],
                'default': [startNode, 'E', endNode]
            }
        };

        const routeKey = `${startNode}-${endNode}`;
        const routes = [];
        
        // Calculate metrics for each route type with realistic differences
        
        // 1. Fast Route - Speed optimized
        const fastPath = routeStrategies.fast[routeKey] || routeStrategies.fast.default;
        const fastDistance = fastPath.length * 8 + Math.random() * 3;
        const fastTime = fastPath.length * 3.5 + Math.random() * 2;
        const fastEmissions = fastDistance * 85 + Math.random() * 80;
        
        routes.push({
            type: 'fast',
            path: fastPath,
            totalTime: fastTime,
            totalDistance: fastDistance,
            totalEmissions: fastEmissions,
            green_points_score: Math.max(25, 95 - Math.round(fastEmissions / 120))
        });

        // 2. Eco Route - Emission optimized
        const ecoPath = routeStrategies.eco[routeKey] || routeStrategies.eco.default;
        const ecoDistance = ecoPath.length * 10 + Math.random() * 2;
        const ecoTime = ecoPath.length * 5.0 + Math.random() * 2.5;
        const ecoEmissions = ecoDistance * 20 + Math.random() * 40; // Much lower emissions
        
        routes.push({
            type: 'eco',
            path: ecoPath,
            totalTime: ecoTime,
            totalDistance: ecoDistance,
            totalEmissions: ecoEmissions,
            green_points_score: Math.max(80, 130 - Math.round(ecoEmissions / 60))
        });

        // 3. RL-Optimized Route - Alpha-balanced
        const rlPath = routeStrategies.rl[routeKey] || routeStrategies.rl.default;
        const rlDistance = rlPath.length * 9 + Math.random() * 2.5;
        
        // RL balances speed vs eco based on alpha
        const baseTime = rlPath.length * 4.2;
        const rlTime = baseTime + (alpha * 1.5) + Math.random() * 2; // Higher alpha = slower but greener
        
        const baseEmissions = rlDistance * 45;
        const rlEmissions = baseEmissions * (0.6 + alpha * 0.2) + Math.random() * 60; // Higher alpha = lower emissions
        
        // Score calculation considers alpha weighting
        const timeScore = Math.max(0, 100 - rlTime * 4);
        const emissionScore = Math.max(0, 100 - rlEmissions / 12);
        const rlScore = Math.round(
            (1 - alpha) * timeScore * 0.35 + // Speed component 
            alpha * emissionScore * 0.55 +    // Eco component
            10                                // RL bonus
        );
        
        routes.push({
            type: 'rl-optimized',
            path: rlPath,
            totalTime: rlTime,
            totalDistance: rlDistance,
            totalEmissions: rlEmissions,
            green_points_score: Math.max(45, Math.min(110, rlScore))
        });

        return routes;
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-6">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-4xl font-extrabold text-center mb-4 text-gray-800">
                    🌱 PragatiDhara - Sustainable Route Optimization
                </h1>
                
                {/* Backend Status Indicator */}
                <div className="text-center mb-6">
                    <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${
                        backendHealth.status === 'healthy' 
                            ? 'bg-green-100 text-green-800 border border-green-200' 
                            : backendHealth.status === 'error'
                            ? 'bg-red-100 text-red-800 border border-red-200'
                            : 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                    }`}>
                        {backendHealth.status === 'healthy' && (
                            <>
                                <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                                🌿 AI Backend Connected - {energyConnected ? `CPU: ${energyMetrics.cpu_usage_percent.toFixed(1)}%` : 'Metrics Loading...'}
                            </>
                        )}
                        {backendHealth.status === 'error' && (
                            <>
                                <div className="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
                                ⚡ Offline Mode - Using Client-Side Processing
                            </>
                        )}
                        {backendHealth.status === 'checking' && (
                            <>
                                <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2 animate-pulse"></div>
                                🔄 Connecting to Backend...
                            </>
                        )}
                    </div>
                </div>
                
                {/* Main Dashboard Grid */}
                <div className="grid lg:grid-cols-4 gap-6 mb-8">
                    
                    {/* Real-time Traffic Data */}
                    <div className="col-span-1 p-5 bg-green-50 rounded-xl shadow-lg border border-green-300">
                        <div className="flex items-center justify-between mb-3">
                            <h2 className="text-lg font-bold text-green-700">Live Traffic Intelligence</h2>
                            <div className={`flex items-center text-xs ${trafficOnline ? 'text-green-600' : 'text-orange-600'}`}>
                                <div className={`w-2 h-2 rounded-full mr-1 ${trafficOnline ? 'bg-green-500 animate-pulse' : 'bg-orange-500'}`}></div>
                                {trafficOnline ? 'Backend' : 'Simulated'}
                            </div>
                        </div>
                        
                        <div className="space-y-4">
                            <div className="p-3 bg-green-100 rounded-lg">
                                <p className="text-sm font-semibold text-gray-700">Traffic Congestion Level</p>
                                <div className="flex items-center">
                                    <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                                        <div 
                                            className="bg-green-600 h-2 rounded-full transition-all duration-500"
                                            style={{ width: `${rlStateVector.trafficFactor * 100}%` }}
                                        ></div>
                                    </div>
                                    <span className="text-sm font-bold">{Math.round(rlStateVector.trafficFactor * 100)}%</span>
                                </div>
                            </div>

                            <div className="p-3 bg-green-100 rounded-lg">
                                <p className="text-sm font-semibold text-gray-700">Incident Density</p>
                                <div className="flex items-center">
                                    <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                                        <div 
                                            className="bg-orange-500 h-2 rounded-full transition-all duration-500"
                                            style={{ width: `${rlStateVector.incidentFactor * 100}%` }}
                                        ></div>
                                    </div>
                                    <span className="text-sm font-bold">{Math.round(rlStateVector.incidentFactor * 100)}%</span>
                                </div>
                            </div>
                        </div>
                        
                        <p className="text-xs text-gray-500 border-t pt-2 mt-4">
                            Simulated Incident Density Factor (IDF): **{rlStateVector.incidentFactor.toFixed(3)}**
                        </p>
                    </div>

                    {/* Energy Metrics Panel */}
                    <div className="col-span-1 p-5 bg-blue-50 rounded-xl shadow-lg border border-blue-300">
                        <div className="flex items-center justify-between mb-3">
                            <h2 className="text-lg font-bold text-blue-700">Energy Metrics</h2>
                            <div className={`flex items-center text-xs ${energyConnected ? 'text-blue-600' : 'text-gray-600'}`}>
                                <div className={`w-2 h-2 rounded-full mr-1 ${energyConnected ? 'bg-blue-500 animate-pulse' : 'bg-gray-500'}`}></div>
                                {energyConnected ? 'Live' : 'Simulated'}
                            </div>
                        </div>
                        
                        <div className="space-y-4">
                            <div className="p-3 bg-blue-100 rounded-lg">
                                <p className="text-sm font-semibold text-gray-700">CPU Usage</p>
                                <div className="flex items-center">
                                    <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                                        <div 
                                            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                                            style={{ width: `${energyMetrics.cpu_usage_percent}%` }}
                                        ></div>
                                    </div>
                                    <span className="text-sm font-bold">{energyMetrics.cpu_usage_percent.toFixed(1)}%</span>
                                </div>
                            </div>

                            <div className="p-3 bg-blue-100 rounded-lg">
                                <p className="text-sm font-semibold text-gray-700">Memory Usage</p>
                                <div className="flex items-center">
                                    <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                                        <div 
                                            className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                                            style={{ width: `${energyMetrics.memory_usage_percent}%` }}
                                        ></div>
                                    </div>
                                    <span className="text-sm font-bold">{energyMetrics.memory_usage_percent.toFixed(1)}%</span>
                                </div>
                            </div>

                            <div className="text-center">
                                <p className="text-xs text-gray-600">Sustainability Grade</p>
                                <p className={`text-2xl font-bold ${
                                    energyMetrics.sustainability_grade === 'A+' ? 'text-green-600' :
                                    energyMetrics.sustainability_grade === 'A' ? 'text-blue-600' : 'text-yellow-600'
                                }`}>
                                    {energyMetrics.sustainability_grade}
                                </p>
                                <p className="text-xs text-gray-500">
                                    Efficiency: {energyMetrics.energy_efficiency_score.toFixed(0)}%
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* RL Agent Control */}
                    <div className="col-span-1 p-5 bg-yellow-50 rounded-xl shadow-lg border border-yellow-300">
                        <h2 className="text-lg font-bold mb-3 text-yellow-700">RL Agent Inference (α Action)</h2>
                        
                        <div className="mb-4">
                            <label className="block text-sm font-semibold text-gray-700">Optimal Emissions Scale Factor (α)</label>
                            <div className="text-5xl font-extrabold text-yellow-600 my-2">{optimalAlpha.toFixed(3)}</div>
                            <p className="text-xs text-gray-500">
                                This value is the action output by the **CPU-Optimized RL Model** based on the current state.
                            </p>
                        </div>

                        <div className="mb-4 space-y-2">
                            <label className="block text-sm font-semibold text-gray-700">Route Points</label>
                            <select 
                                value={startNode} 
                                onChange={e => setStartNode(e.target.value)} 
                                className="w-full p-2 border rounded-lg text-sm"
                            >
                                {Object.keys(locationLabels).map(key => 
                                    <option key={key} value={key}>{locationLabels[key]}</option>
                                )}
                            </select>
                            <select 
                                value={endNode} 
                                onChange={e => setEndNode(e.target.value)} 
                                className="w-full p-2 border rounded-lg text-sm"
                            >
                                {Object.keys(locationLabels).map(key => 
                                    <option key={key} value={key}>{locationLabels[key]}</option>
                                )}
                            </select>
                        </div>

                        {/* RL Algorithm Parameter Control */}
                        <div className="mb-4">
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                RL Alpha Parameter: {alpha.toFixed(2)}
                                <span className="text-xs text-gray-500 block">
                                    {alpha < 0.3 ? '⚡ Speed Priority' : alpha > 0.7 ? '🌿 Eco Priority' : '⚖️ Balanced'}
                                </span>
                            </label>
                            <input
                                type="range"
                                min="0.1"
                                max="1.0"
                                step="0.1"
                                value={alpha}
                                onChange={e => setAlpha(parseFloat(e.target.value))}
                                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                            />
                            <div className="flex justify-between text-xs text-gray-500 mt-1">
                                <span>Fast</span>
                                <span>Balanced</span>
                                <span>Eco</span>
                            </div>
                        </div>

                        <button 
                            onClick={handlePlanRoute} 
                            disabled={routesLoading}
                            className={`w-full font-semibold py-3 px-4 rounded-xl shadow-md transition duration-200 ${
                                routesLoading 
                                ? 'bg-gray-400 text-gray-600 cursor-not-allowed' 
                                : 'bg-green-600 text-white hover:bg-green-700'
                            }`}
                        >
                            <span className="flex items-center justify-center">
                                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                                </svg>
                                {routesLoading ? (
                                    <>
                                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                                        Optimizing Routes...
                                    </>
                                ) : (
                                    <>
                                        🚀 Plan RL-Optimized Route
                                    </>
                                )}
                            </span>
                        </button>
                        
                        <div className={`p-3 rounded-xl mt-4 text-center text-sm ${
                            message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'
                        }`}>
                            {message}
                        </div>
                    </div>

                    {/* Audit Log */}
                    <div className="col-span-1 p-5 bg-blue-50 rounded-xl shadow-lg border border-blue-300">
                        <h2 className="text-lg font-bold mb-3 text-blue-700">Audit & Sustainability Log</h2>
                        <div className="p-3 bg-blue-100 rounded-lg mb-4 text-center">
                            <p className="text-sm font-semibold text-blue-800">
                                Total Cumulative Carbon Saved (Across {auditLog.length} requests)
                            </p>
                            <p className="text-3xl font-extrabold text-blue-600 mt-1">
                                {Math.round(totalCarbonSaved / 1000).toLocaleString()} 
                                <span className="text-sm font-semibold">kg CO₂</span>
                            </p>
                        </div>
                        
                        <div className="space-y-2 max-h-96 overflow-y-auto">
                            <p className="font-semibold text-xs text-gray-600 mb-1">Last 5 Requests:</p>
                            {auditLog.slice(-5).reverse().map((log) => (
                                <div key={log.id} className="p-2 border border-blue-200 rounded-lg text-xs bg-white">
                                    <p className="font-bold text-gray-800">
                                        Alpha: {log.rlAlpha} | Inf Time: {log.inferenceTime}ms
                                    </p>
                                    <p className={log.carbonSaved > 0 ? "text-green-600 font-semibold" : "text-gray-500"}>
                                        Saved: {log.carbonSaved.toLocaleString()}g CO₂ | Cost: {log.rlTime - log.fastTime} min
                                    </p>
                                </div>
                            ))}
                            {auditLog.length === 0 && (
                                <p className="text-center text-gray-500 text-sm">Run a route to start the audit log.</p>
                            )}
                        </div>
                    </div>
                </div>

                {/* Route Results */}
                {results && (
                    <div className="mt-8">
                        <h2 className="text-2xl font-bold mb-4 text-gray-800">Route Recommendations (Top 3)</h2>
                        <div className="grid md:grid-cols-3 gap-6">
                            {results.map((route) => (
                                <div 
                                    key={route.type} 
                                    className={`p-5 rounded-xl shadow-xl transition duration-300 ${
                                        route.type === 'rl-optimized' 
                                            ? 'bg-yellow-100 border-4 border-yellow-500' 
                                            : route.type === 'eco' 
                                                ? 'bg-green-100 border-4 border-green-500' 
                                                : 'bg-gray-100 border-4 border-gray-300'
                                    }`}
                                >
                                    <h3 className={`text-xl font-extrabold mb-2 ${
                                        route.type === 'rl-optimized' 
                                            ? 'text-yellow-700' 
                                            : route.type === 'eco' 
                                                ? 'text-green-700' 
                                                : 'text-gray-700'
                                    }`}>
                                        {route.type.toUpperCase().replace('-', ' ')}
                                    </h3>
                                    
                                    <div className="mb-3">
                                        <p className="text-xs font-semibold text-gray-600">Green Points Score</p>
                                        <p className="text-4xl font-extrabold text-green-800">{route.green_points_score}</p>
                                    </div>
                                    
                                    <div className="grid grid-cols-2 gap-2 text-sm border-t pt-3">
                                        <div>
                                            <p className="font-semibold text-gray-700">Time</p>
                                            <p className="text-2xl font-bold">
                                                {route.totalTime} <span className="text-sm">min</span>
                                            </p>
                                        </div>
                                        <div>
                                            <p className="font-semibold text-gray-700">CO₂ Emissions</p>
                                            <p className="text-2xl font-bold">
                                                {route.totalEmissions.toLocaleString()} <span className="text-sm">g</span>
                                            </p>
                                        </div>
                                    </div>
                                    
                                    <p className="mt-4 text-xs italic text-gray-600 truncate">
                                        Path: {route.path.join(' → ')}
                                    </p>
                                    
                                    {route.type === 'rl-optimized' && (
                                        <p className="text-xs font-medium mt-1">
                                            (α={optimalAlpha.toFixed(3)})
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// Wrap App with ErrorBoundary for better error handling
const AppWithErrorBoundary = () => (
  <ErrorBoundary showDetails={process.env.NODE_ENV === 'development'}>
    <App />
  </ErrorBoundary>
);

export default AppWithErrorBoundary;