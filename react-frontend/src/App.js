import React, { useState, useEffect, useRef } from 'react';
import VehicleSelector from './components/VehicleSelector';
import RouteInput from './components/RouteInput';
import MapContainer from './components/MapContainer';
import ResultsDashboard from './components/ResultsDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';
import { GreenCreditsWallet } from './components/GreenCreditsDisplay';

const GOOGLE_MAPS_API_BASE = 'http://127.0.0.1:8001';

const App = () => {
  const [selectedVehicle, setSelectedVehicle] = useState('petrol');
  const [startLocation, setStartLocation] = useState('');
  const [endLocation, setEndLocation] = useState('');
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState({ connected: false, checking: true });
  const [userId] = useState('demo_user_001'); // Demo user ID for testing
  
  const mapRef = useRef(null);

  // Check backend status on component mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch(`${GOOGLE_MAPS_API_BASE}/health`);
      if (response.ok) {
        setBackendStatus({ connected: true, checking: false });
      } else {
        setBackendStatus({ connected: false, checking: false });
      }
    } catch (err) {
      setBackendStatus({ connected: false, checking: false });
    }
  };

  const clearError = () => {
    setError(null);
  };

  const handleRouteSearch = async () => {
    if (!startLocation.trim() || !endLocation.trim()) {
      setError('Please enter both start and end locations');
      return;
    }

    setLoading(true);
    setError(null);
    setRoutes([]);

    try {
      const payload = {
        origin: { address: startLocation },
        destination: { address: endLocation },
        travel_mode: 'driving',
        departure_time: new Date().toISOString(),
        vehicle_type: selectedVehicle
      };

      console.log('🚀 Calling API:', payload);

      const response = await fetch(`${GOOGLE_MAPS_API_BASE}/api/v1/routes/three-strategies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (!data.routes || !Array.isArray(data.routes) || data.routes.length === 0) {
        throw new Error('No routes found. Please try different locations.');
      }

      setRoutes(data.routes);
      
    } catch (err) {
      console.error('Route search error:', err);
      setError(err.message || 'Failed to get routes. Please check your internet connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setRoutes([]);
    setError(null);
    setStartLocation('');
    setEndLocation('');
    setSelectedVehicle('petrol');
  };

  if (backendStatus.checking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <LoadingSpinner size="large" message="Checking backend connectivity..." />
      </div>
    );
  }

  if (!backendStatus.connected) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md mx-auto bg-white rounded-lg card-shadow p-8 text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Backend Not Available</h2>
          <p className="text-gray-600 mb-6">
            The PragatiDhara backend service is not running. Please start the backend server first.
          </p>
          <button 
            onClick={checkBackendHealth}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="gradient-bg text-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">🌱 PragatiDhara</h1>
                <p className="text-blue-100 mt-1">Smart Route Planning & Fuel Savings</p>
              </div>
              <div className="hidden md:flex items-center space-x-4">
                <GreenCreditsWallet userId={userId} className="min-w-[250px]" />
                <div className="text-sm">
                  <span className="bg-green-500 text-white px-2 py-1 rounded text-xs font-semibold">
                    ✅ Backend Connected
                  </span>
                </div>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-8">
          {/* Input Section */}
          <div className="grid lg:grid-cols-3 gap-8 mb-8">
            {/* Vehicle Selection */}
            <div className="lg:col-span-1">
              <VehicleSelector 
                selectedVehicle={selectedVehicle}
                onVehicleChange={setSelectedVehicle}
                disabled={loading}
              />
            </div>

            {/* Route Input */}
            <div className="lg:col-span-2">
              <RouteInput
                startLocation={startLocation}
                endLocation={endLocation}
                onStartLocationChange={setStartLocation}
                onEndLocationChange={setEndLocation}
                onSearch={handleRouteSearch}
                onReset={resetForm}
                loading={loading}
                disabled={loading}
              />
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <div className="text-red-500 text-xl mr-3">❌</div>
                  <div>
                    <h3 className="text-red-800 font-semibold">Error</h3>
                    <p className="text-red-600 mt-1">{error}</p>
                  </div>
                </div>
                <button
                  onClick={clearError}
                  className="text-red-500 hover:text-red-700 ml-4"
                >
                  ✕
                </button>
              </div>
              <div className="mt-4 flex space-x-3">
                <button
                  onClick={handleRouteSearch}
                  disabled={loading}
                  className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-all duration-200 disabled:opacity-50"
                >
                  Try Again
                </button>
                <button
                  onClick={resetForm}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-lg transition-all duration-200"
                >
                  Reset Form
                </button>
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="mb-8">
              <LoadingSpinner size="medium" message="Finding best routes for your vehicle..." />
            </div>
          )}

          {/* Results Section */}
          {routes.length > 0 && !loading && (
            <div className="space-y-8">
              {/* Map Container */}
              <MapContainer 
                routes={routes}
                startLocation={startLocation}
                endLocation={endLocation}
                ref={mapRef}
              />

              {/* Results Dashboard */}
              <ResultsDashboard 
                routes={routes}
                selectedVehicle={selectedVehicle}
                onVehicleChange={setSelectedVehicle}
              />
            </div>
          )}

          {/* Empty State */}
          {routes.length === 0 && !loading && !error && (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">🗺️</div>
              <h2 className="text-2xl font-bold text-gray-600 mb-4">Ready to Find Your Route</h2>
              <p className="text-gray-500 max-w-md mx-auto">
                Select your vehicle type, enter your start and end locations, and we'll find the best routes with fuel cost analysis.
              </p>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="bg-gray-800 text-white py-8 mt-16">
          <div className="max-w-7xl mx-auto px-4 text-center">
            <p className="text-gray-400">
              © 2025 PragatiDhara | Smart Route Planning for a Sustainable Future
            </p>
          </div>
        </footer>
      </div>
    </ErrorBoundary>
  );
};

export default App;