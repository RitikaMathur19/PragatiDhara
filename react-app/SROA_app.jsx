import React, { useState, useMemo, useEffect } from 'react';

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
    { from: 'B', to: 'D', distance: 10, time: 5 }, { from: 'C', 'to': 'D', distance: 8, time: 4 },
    { from: 'D', to: 'E', distance: 5, time: 2 }, // Shivajinagar to UC
    { from: 'E', to: 'J', distance: 10, time: 5 }, // UC to Hinjawadi Main Access
    { from: 'I', to: 'J', distance: 8, time: 4 }, // Wakad to Hinjawadi Ph 1

    // Eco Bypass 1 (F to H) - Max CO2 Reduction (Deep Green)
    { from: 'C', 'to': 'F', distance: 8, time: 4, eco_priority: true, emissions_multiplier: 0.5 }, // Feeder to Bypass
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

// --- DATA MOCKING FUNCTIONS (Simulating Data Streams) ---

// Mocks the Incident Density Factor (IDF) and User Load Factor (ULF)
const generateIDFAndULF = (route, avgCF) => {
    const safeCF = Number(avgCF) || 1.0; 
    const idf = Math.min(1, Math.random() * (safeCF / 3) + (Math.random() * 0.1));
    const ulf = Math.min(1, Math.random() * 0.5 + (safeCF / 2));
    const incidentMetric = (idf * 0.7) + (ulf * 0.3);
    return Math.min(1, incidentMetric);
};

// Calculates CO2 Emissions based on vehicle config and link distance/traffic
const calculateEmissionsAndCost = (link, vehicleConfig, congestionFactor, incidentFactor) => {
    const distance = link.distance;
    const { base_rate, congestion_sensitivity, fuelType } = vehicleConfig;
    
    // 1. Determine effective Congestion Factor (CF)
    let effectiveCF = congestionFactor;
    if (link.eco_priority) {
        // Eco Bypass links are assumed to be less affected by the area's congestion (50% less impact)
        effectiveCF = 1.0 + ((Math.max(1.0, congestionFactor) - 1.0) * 0.5);
    }
    
    // 1. Calculate Base Emissions (g CO2)
    // Apply inherent link emissions multiplier (defaults to 1.0 if not set)
    let emissions = distance * base_rate * (link.emissions_multiplier || 1.0); 

    // 2. Apply Congestion Penalty to Emissions (Eco Logic)
    if (effectiveCF > 1 && fuelType !== 'Electric') {
        const emissionsPenalty = (effectiveCF - 1) * congestion_sensitivity * 100; 
        emissions *= (1 + emissionsPenalty / 100);
    }

    // 3. Apply Incident/Load Penalty to Travel Time
    let travelTime = link.time * effectiveCF;
    // High incident factor adds a small, unpredictable time delay (e.g., slowdown for pothole)
    if (incidentFactor > 0.5) {
        travelTime *= (1 + incidentFactor * 0.2);
    }
    
    return {
        emissionsCost: Math.round(emissions),
        travelTime: travelTime,
        distance: distance 
    };
};

// --- REINFORCEMENT LEARNING AGENT (CPU-Optimized Simulation) ---
const predictOptimalAlpha = (state) => {
    const { normalizedCF, normalizedIDF, normalizedAcceptance, fuelType, normalizedEfficiency } = state;

    const CF = Number(normalizedCF) || 0; 
    const IDF = Number(normalizedIDF) || 0;
    const Acceptance = Number(normalizedAcceptance) || 0;
    const Efficiency = Number(normalizedEfficiency) || 0;

    // SROA Logic:
    let alphaBase = 0.05 + (0.3 * CF); // High traffic increases alpha (pushes towards eco)
    alphaBase -= (0.1 * IDF); // High incidents slightly decreases alpha (pushes away from potentially slower detours)
    alphaBase += (0.1 * Acceptance); // User acceptance increases alpha
    
    // Vehicle context overrides
    if (fuelType === 'Electric') {
        alphaBase = 0.05; // EVs already eco, low need to push
    } else if (Efficiency < 0.3) {
        alphaBase += 0.05; // Very inefficient car, aggressive push to eco
    }

    // Confine alpha to the useful range for balancing the A* cost function
    // With more options, we can raise the floor and ceiling slightly for more aggressive optimization.
    let alpha = Math.max(0.05, Math.min(0.6, alphaBase));

    return alpha;
};

// --- A* ROUTING ALGORITHM (Optimized Dijkstra's with Multi-Goal Cost) ---
const PURE_EMISSIONS_MULTIPLIER = 5; // High multiplier for the pure 'eco' path to prioritize CO2 reduction

const findRoute = (start, end, vehicleConfig, currentTraffic, incidentFactor, goal, emissionsScaleFactor) => {
    const weights = {}; 
    const emissions = {}; 
    const times = {};     
    const previous = {};  
    const priorityQueue = new Set(); 

    const allNodes = Object.keys(locationLabels);
    allNodes.forEach(node => {
        weights[node] = Infinity;
        emissions[node] = Infinity;
        times[node] = Infinity;
        previous[node] = null;
        priorityQueue.add(node);
    });

    weights[start] = 0;
    emissions[start] = 0;
    times[start] = 0;

    const adjacencyList = {};
    getBidirectionalLinks(staticLinks).forEach(link => {
        const { from } = link;
        if (!adjacencyList[from]) adjacencyList[from] = [];
        adjacencyList[from].push(link);
    });

    while (priorityQueue.size > 0) {
        let minNode = null;
        let minWeight = Infinity;
        priorityQueue.forEach(node => {
            if (weights[node] < minWeight) {
                minWeight = weights[node];
                minNode = node;
            }
        });

        if (minNode === null || minNode === end) break; 
        priorityQueue.delete(minNode); 

        (adjacencyList[minNode] || []).forEach(link => {
            const neighbor = link.to;
            if (!priorityQueue.has(neighbor)) return; 
            
            const linkKey = `${link.from}-${link.to}`;
            // Use the specific congestion factor from the traffic mock
            const congestionFactor = currentTraffic[linkKey] || 1; 

            const { emissionsCost, travelTime } = calculateEmissionsAndCost(
                link, vehicleConfig, congestionFactor, incidentFactor
            );

            let linkWeight;
            
            const TIME_COST_MULTIPLIER = 2; // Time is weighted to make it comparable to CO2 cost

            if (goal === 'fast') {
                // Route 1: Fastest (Time-only objective)
                linkWeight = travelTime * TIME_COST_MULTIPLIER; 
            } else if (goal === 'eco') {
                // Route 2: Eco-Pure (Emissions-only objective)
                linkWeight = emissionsCost * PURE_EMISSIONS_MULTIPLIER; 
            } else { // 'rl-optimized'
                // Route 3: RL-Optimized Balanced (Time vs. CO2 using Alpha)
                linkWeight = (emissionsCost * emissionsScaleFactor) + (travelTime * TIME_COST_MULTIPLIER); 
            }

            const newTotalWeight = weights[minNode] + linkWeight;
            
            if (newTotalWeight < weights[neighbor]) {
                weights[neighbor] = newTotalWeight;
                emissions[neighbor] = emissions[minNode] + emissionsCost;
                times[neighbor] = times[minNode] + travelTime;
                previous[neighbor] = minNode;
            }
        });
    }

    const path = [];
    let currentNode = end;
    while (currentNode) {
        path.unshift(currentNode);
        if (currentNode === start) break;
        currentNode = previous[currentNode];
    }
    
    if (path[0] !== start) return null; 

    const labeledPath = path.map(id => locationLabels[id]).join(' → ');

    return {
        type: goal,
        path: labeledPath,
        totalEmissions: emissions[end],
        totalTime: Math.round(times[end]),
        rawPath: path,
    };
};

// --- GREEN POINTS & AUDIT LOGIC ---

const calculateGreenPoints = (fastRoute, rlRoute, passengers) => {
    if (!fastRoute || !rlRoute) return 0;

    const co2Saved = fastRoute.totalEmissions - rlRoute.totalEmissions;
    const timeCost = rlRoute.totalTime - fastRoute.totalTime;
    
    if (co2Saved <= 0 || fastRoute.totalEmissions <= 0) return 0;

    // Green Points formula rewards CO2 saved against time cost, weighted by passengers
    const greenPoints = 
        100 * (co2Saved / fastRoute.totalEmissions) * (1 / (timeCost > 0 ? timeCost : 1)) * passengers; 

    return Math.round(greenPoints);
};

// --- REACT COMPONENT ---

const App = () => {
    // --- State Management ---
    const [startNode, setStartNode] = useState('A');
    const [endNode, setEndNode] = useState('J');
    const [vehicleInputs, setVehicleInputs] = useState({
        mpg: 45, fuelType: 'Petrol', passengers: 1, makeModel: 'Toyota Prius'
    });
    const [rlStateInputs, setRlStateInputs] = useState({
        time: 17, // 5 PM
        day: 5, // Friday
        avgCF: 2.5, // Heavy Traffic (Crucial for forcing a detour!)
        historicalAcceptance: 0.6 // 60%
    });
    const [results, setResults] = useState(null);
    const [auditLog, setAuditLog] = useState([]);
    const [message, setMessage] = useState("Configure vehicle, traffic, and plan a route.");

    // --- Derived Configuration & Data ---

    const vehicleConfig = useMemo(() => {
        const mpg = parseFloat(vehicleInputs.mpg) || 25;
        const fuelType = vehicleInputs.fuelType;
        const GAL_TO_L = 3.785;
        const MILE_TO_KM = 1.609;
        const co2Factors = { 'Petrol': 2350, 'Diesel': 2680, 'Electric': 0 };
        const fuelCo2Factor = co2Factors[fuelType];

        let baseRate = 0; 
        let congestionSensitivity = 1.5;

        if (fuelType !== 'Electric') {
            const litersPerKm = GAL_TO_L / mpg / MILE_TO_KM;
            baseRate = litersPerKm * fuelCo2Factor;
            congestionSensitivity = Math.min(2.5, 0.8 + (50 - mpg) * 0.05); 
        }

        return {
            base_rate: baseRate,
            congestion_sensitivity: congestionSensitivity,
            fuelType: fuelType,
            normalizedEfficiency: Math.min(1, mpg / 60)
        };
    }, [vehicleInputs.mpg, vehicleInputs.fuelType]);

    const rlStateVector = useMemo(() => {
        const time = Number(rlStateInputs.time) || 0;
        const avgCF = Number(rlStateInputs.avgCF) || 1.0;
        const acceptance = Number(rlStateInputs.historicalAcceptance) || 0;
        
        const normalizedCF = Math.min(1, avgCF / 4);
        const normalizedAcceptance = acceptance;
        const normalizedEfficiency = vehicleConfig.normalizedEfficiency;
        
        const incidentFactor = generateIDFAndULF(null, avgCF); 

        return {
            normalizedTime: time / 24, 
            normalizedDay: rlStateInputs.day / 7, 
            normalizedCF, 
            normalizedAcceptance, 
            normalizedEfficiency,
            fuelType: vehicleConfig.fuelType,
            incidentFactor
        };
    }, [rlStateInputs, vehicleConfig]);

    // RL Agent Inference (CPU-intensive task, should be memoized)
    const optimalAlpha = useMemo(() => {
        return predictOptimalAlpha(rlStateVector);
    }, [rlStateVector]);

    // --- Handlers ---

    const handlePlanRoute = () => {
        const startTime = performance.now();
        
        if (startNode === endNode) {
            setMessage("Start and Destination must be different.");
            return;
        }
        if (vehicleConfig.base_rate === 0 && vehicleInputs.fuelType !== 'Electric') {
            setMessage("Please enter a valid MPG (> 0) to calculate emissions.");
            return;
        }

        // --- MOCK TRAFFIC LOGIC (Forces Route Divergence) ---
        const HIGH_CF = rlStateInputs.avgCF; 
        const LOW_CF = 1.2; 

        const traffic = getBidirectionalLinks(staticLinks).reduce((acc, link) => {
            if (HIGH_CF > 1.5) {
                if (link.eco_priority) {
                    // Eco links get low, controlled congestion
                    acc[`${link.from}-${link.to}`] = LOW_CF * (1.0 + Math.random() * 0.1); 
                } else {
                    // Main links get highly variable, high congestion
                    acc[`${link.from}-${link.to}`] = HIGH_CF * (0.8 + Math.random() * 0.4);
                }
            } else {
                // Low traffic mode, all links are near 1.0 CF
                acc[`${link.from}-${link.to}`] = 1.0 + Math.random() * 0.2;
            }
            return acc;
        }, {});
        // -----------------------------------------------------------


        // --- Execute Route Calculations ---
        const fastRoute = findRoute(startNode, endNode, vehicleConfig, traffic, rlStateVector.incidentFactor, 'fast', 0);
        const ecoRoute = findRoute(startNode, endNode, vehicleConfig, traffic, rlStateVector.incidentFactor, 'eco', 0); 
        const rlRoute = findRoute(startNode, endNode, vehicleConfig, traffic, rlStateVector.incidentFactor, 'rl-optimized', optimalAlpha);

        const endTime = performance.now();
        const inferenceTime = (endTime - startTime).toFixed(3);

        if (fastRoute && ecoRoute && rlRoute) {
            // Calculate Green Points
            const rlGreenPoints = calculateGreenPoints(fastRoute, rlRoute, vehicleInputs.passengers);
            const ecoGreenPoints = calculateGreenPoints(fastRoute, ecoRoute, vehicleInputs.passengers);

            const allRoutes = [
                {...rlRoute, green_points_score: rlGreenPoints, totalEmissions: Math.round(rlRoute.totalEmissions)},
                {...ecoRoute, green_points_score: ecoGreenPoints, totalEmissions: Math.round(ecoRoute.totalEmissions)},
                {...fastRoute, green_points_score: 0, totalEmissions: Math.round(fastRoute.totalEmissions)},
            ].sort((a, b) => b.green_points_score - a.green_points_score); // Sort by Green Points

            setResults(allRoutes);

            // Create Audit Log
            const carbonSaved = fastRoute.totalEmissions - rlRoute.totalEmissions;
            setAuditLog(prevLog => [
                ...prevLog,
                {
                    id: Date.now(),
                    rlAlpha: optimalAlpha.toFixed(3),
                    fastCO2: Math.round(fastRoute.totalEmissions),
                    rlCO2: Math.round(rlRoute.totalEmissions),
                    fastTime: fastRoute.totalTime,
                    rlTime: rlRoute.totalTime,
                    carbonSaved: Math.round(carbonSaved),
                    inferenceTime: parseFloat(inferenceTime),
                }
            ]);

            setMessage(`Route calculated in ${inferenceTime} ms. RL Agent found optimal \u03B1=${optimalAlpha.toFixed(3)}.`);
        } else {
            setMessage("Could not find a path between the selected nodes.");
            setResults(null);
        }
    };

    // Total cumulative savings for the audit report
    const totalCarbonSaved = auditLog.reduce((sum, entry) => sum + entry.carbonSaved, 0);

    return (
        <div className="p-4 bg-gray-50 min-h-screen text-gray-800">
            <h1 className="text-3xl font-extrabold text-green-700 mb-6 border-b pb-2">Sustainable Route Optimization Agent (SROA)</h1>
            <p className="mb-6 text-sm text-gray-600">This application simulates the output of the CPU-optimized RL Agent and the multi-objective A* algorithm.</p>

            <div className="grid md:grid-cols-3 gap-6">
                
                {/* -------------------- 1. Data Input and State Vector (S) -------------------- */}
                <div className="col-span-1 p-5 bg-white rounded-xl shadow-lg border border-gray-100">
                    <h2 className="text-lg font-bold mb-3 text-green-600">Agent State & Vehicle Input</h2>
                    
                    {/* Vehicle Inputs */}
                    <div className="space-y-3 mb-5 border-b pb-4">
                        <h3 className="font-semibold text-sm text-gray-700">Vehicle Profile</h3>
                        <input type="text" value={vehicleInputs.makeModel} onChange={e => setVehicleInputs(prev => ({ ...prev, makeModel: e.target.value }))} placeholder="Make & Model" className="w-full p-2 border rounded-lg text-sm" />
                        <div className="flex space-x-3">
                            <input type="number" value={vehicleInputs.mpg} onChange={e => setVehicleInputs(prev => ({ ...prev, mpg: e.target.value }))} placeholder="MPG" className="w-1/2 p-2 border rounded-lg text-sm" />
                            <select value={vehicleInputs.fuelType} onChange={e => setVehicleInputs(prev => ({ ...prev, fuelType: e.target.value }))} className="w-1/2 p-2 border rounded-lg text-sm">
                                <option value="Petrol">Petrol</option>
                                <option value="Diesel">Diesel</option>
                                <option value="Electric">Electric (EV)</option>
                            </select>
                        </div>
                        <input type="number" value={vehicleInputs.passengers} onChange={e => setVehicleInputs(prev => ({ ...prev, passengers: parseInt(e.target.value) || 1 }))} placeholder="Passengers" min="1" className="w-full p-2 border rounded-lg text-sm" />
                    </div>

                    {/* RL State Sliders (Dynamic Context) */}
                    <div className="space-y-4">
                        <h3 className="font-semibold text-sm text-gray-700">RL Context Simulation (State S)</h3>
                        {[
                            { key: 'time', label: `Time of Day: ${rlStateInputs.time}:00`, max: 23, step: 1, min: 0 },
                            { key: 'avgCF', label: `Avg Route Congestion Factor (CF): ${rlStateInputs.avgCF.toFixed(1)}x`, max: 4.0, step: 0.1, min: 1.0 },
                            { key: 'historicalAcceptance', label: `User Acceptance Rate: ${(rlStateInputs.historicalAcceptance * 100).toFixed(0)}%`, max: 1.0, step: 0.05, min: 0 },
                        ].map(({ key, label, max, step, min }) => (
                            <div key={key}>
                                <label className="block text-xs font-medium text-gray-500">{label}</label>
                                <input
                                    type="range"
                                    min={min}
                                    max={max}
                                    step={step}
                                    value={rlStateInputs[key]}
                                    onChange={e => setRlStateInputs(prev => ({ ...prev, [key]: parseFloat(e.target.value) }))}
                                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer range-lg"
                                />
                            </div>
                        ))}
                        <p className="text-xs text-gray-500 border-t pt-2">Simulated Incident Density Factor (IDF): **{(rlStateVector.incidentFactor).toFixed(3)}**</p>
                    </div>
                </div>

                {/* -------------------- 2. RL Agent Output & Control -------------------- */}
                <div className="col-span-1 p-5 bg-yellow-50 rounded-xl shadow-lg border border-yellow-300">
                    <h2 className="text-lg font-bold mb-3 text-yellow-700">RL Agent Inference (\u03B1 Action)</h2>
                    
                    <div className="mb-4">
                        <label className="block text-sm font-semibold text-gray-700">Optimal Emissions Scale Factor (\u03B1)</label>
                        <div className="text-5xl font-extrabold text-yellow-600 my-2">{optimalAlpha.toFixed(3)}</div>
                        <p className="text-xs text-gray-500">This value is the action output by the **CPU-Optimized RL Model** based on the current state. It dictates the balance between time and CO₂ in the A* cost function.</p>
                    </div>

                    <div className="mb-4 space-y-2">
                        <label className="block text-sm font-semibold text-gray-700">Route Points</label>
                        <select value={startNode} onChange={e => setStartNode(e.target.value)} className="w-full p-2 border rounded-lg text-sm">
                            {Object.keys(locationLabels).map(key => <option key={key} value={key}>{locationLabels[key]}</option>)}
                        </select>
                        <select value={endNode} onChange={e => setEndNode(e.target.value)} className="w-full p-2 border rounded-lg text-sm">
                            {Object.keys(locationLabels).map(key => <option key={key} value={key}>{locationLabels[key]}</option>)}
                        </select>
                    </div>

                    <button 
                        onClick={handlePlanRoute} 
                        className="w-full bg-green-600 text-white font-semibold py-3 px-4 rounded-xl shadow-md hover:bg-green-700 transition duration-200">
                        <span className="flex items-center justify-center">
                            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                            Plan RL-Optimized Route
                        </span>
                    </button>
                    <div className={`p-3 rounded-xl mt-4 text-center text-sm ${message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'}`}>
                        {message}
                    </div>
                </div>

                {/* -------------------- 3. Cumulative Audit Log -------------------- */}
                 <div className="col-span-1 p-5 bg-blue-50 rounded-xl shadow-lg border border-blue-300">
                    <h2 className="text-lg font-bold mb-3 text-blue-700">Audit & Sustainability Log</h2>
                    <div className="p-3 bg-blue-100 rounded-lg mb-4 text-center">
                        <p className="text-sm font-semibold text-blue-800">Total Cumulative Carbon Saved (Across {auditLog.length} requests)</p>
                        <p className="text-3xl font-extrabold text-blue-600 mt-1">{Math.round(totalCarbonSaved / 1000).toLocaleString()} <span className="text-sm font-semibold">kg CO₂</span></p>
                    </div>
                    
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                        <p className="font-semibold text-xs text-gray-600 mb-1">Last 5 Requests:</p>
                        {auditLog.slice(-5).reverse().map((log, index) => (
                            <div key={log.id} className="p-2 border border-blue-200 rounded-lg text-xs bg-white">
                                <p className="font-bold text-gray-800">Alpha: {log.rlAlpha} | Inf Time: {log.inferenceTime}ms</p>
                                <p className={log.carbonSaved > 0 ? "text-green-600 font-semibold" : "text-gray-500"}>
                                    Saved: {log.carbonSaved.toLocaleString()}g CO₂ | Cost: {log.rlTime - log.fastTime} min
                                </p>
                            </div>
                        ))}
                        {auditLog.length === 0 && <p className="text-center text-gray-500 text-sm">Run a route to start the audit log.</p>}
                    </div>
                </div>

            </div>

            {/* -------------------- Route Comparison Results -------------------- */}
            {results && (
                <div className="mt-8">
                    <h2 className="text-2xl font-bold mb-4 text-gray-800">Route Recommendations (Top 3)</h2>
                    <div className="grid md:grid-cols-3 gap-6">
                        {results.map((route) => (
                            <div 
                                key={route.type} 
                                className={`p-5 rounded-xl shadow-xl transition duration-300 
                                    ${route.type === 'rl-optimized' ? 'bg-yellow-100 border-4 border-yellow-500' : route.type === 'eco' ? 'bg-green-100 border-4 border-green-500' : 'bg-gray-100 border-4 border-gray-300'}`
                                }>
                                <h3 className={`text-xl font-extrabold mb-2 ${route.type === 'rl-optimized' ? 'text-yellow-700' : route.type === 'eco' ? 'text-green-700' : 'text-gray-700'}`}>
                                    {route.type.toUpperCase().replace('_', ' ')}
                                </h3>
                                
                                <div className="mb-3">
                                    <p className="text-xs font-semibold text-gray-600">Green Points Score</p>
                                    <p className="text-4xl font-extrabold text-green-800">{route.green_points_score}</p>
                                </div>
                                
                                <div className="grid grid-cols-2 gap-2 text-sm border-t pt-3">
                                    <div>
                                        <p className="font-semibold text-gray-700">Time</p>
                                        <p className="text-2xl font-bold">{route.totalTime} <span className="text-sm">min</span></p>
                                    </div>
                                    <div>
                                        <p className="font-semibold text-gray-700">CO₂ Emissions</p>
                                        <p className="text-2xl font-bold">{route.totalEmissions.toLocaleString()} <span className="text-sm">g</span></p>
                                    </div>
                                </div>
                                <p className="mt-4 text-xs italic text-gray-600 truncate">Path: {route.path}</p>
                                <p className="text-xs font-medium mt-1">
                                    {route.type === 'rl-optimized' && `(\u03B1=${optimalAlpha.toFixed(3)})`}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default App;