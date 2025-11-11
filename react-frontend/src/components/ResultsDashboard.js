import React, { useState } from 'react';

const RouteCard = ({ route, index, isSelected, onClick, vehicleData }) => {
  const routeConfig = {
    'fastest': { 
      color: '#FF6B00', 
      bgColor: '#FFF1E0', 
      borderColor: '#FF6B00', 
      icon: '🚀', 
      title: 'FASTEST ROUTE'
    },
    'eco-friendly': { 
      color: '#006400', 
      bgColor: '#F0FFF0', 
      borderColor: '#006400', 
      icon: '🌱', 
      title: 'ECO-FRIENDLY ROUTE'
    },
    'balanced': { 
      color: '#000080', 
      bgColor: '#F0F5FF', 
      borderColor: '#000080', 
      icon: '⚖️', 
      title: 'BALANCED ROUTE'
    }
  };

  const config = routeConfig[route.type] || routeConfig['balanced'];

  return (
    <div 
      className={`p-6 rounded-lg border-2 cursor-pointer transition-all duration-200 transform hover:scale-105 ${
        isSelected ? 'ring-4 ring-blue-300' : ''
      }`}
      style={{ 
        backgroundColor: config.bgColor, 
        borderColor: config.borderColor 
      }}
      onClick={onClick}
    >
      <div className="text-center mb-4">
        <h3 className="font-bold text-lg" style={{ color: config.color }}>
          {config.icon} {config.title}
        </h3>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">Distance:</span>
          <span className="font-bold" style={{ color: config.color }}>
            {route.distance || 'N/A'} km
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">Duration:</span>
          <span className="font-bold" style={{ color: config.color }}>
            {route.duration || 'N/A'} mins
          </span>
        </div>

        {vehicleData && (
          <>
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">Trip Cost:</span>
              <span className="font-bold text-lg" style={{ color: config.color }}>
                ₹{vehicleData.cost_per_trip?.toFixed(2) || 'N/A'}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">Consumption:</span>
              <span className="font-bold" style={{ color: config.color }}>
                {vehicleData.consumption?.toFixed(2) || 'N/A'} {vehicleData.unit || 'L'}
              </span>
            </div>
          </>
        )}

        <div className="pt-2 border-t border-gray-200">
          <div className="text-xs text-gray-600 text-center">
            Click to view detailed analysis
          </div>
        </div>
      </div>
    </div>
  );
};

const SavingsComparison = ({ routes, selectedVehicle }) => {
  const getVehicleData = (routeType) => {
    const route = routes.find(r => r.type === routeType);
    return route?.fuel_analysis?.vehicle_breakdown?.[selectedVehicle];
  };

  const fastest = getVehicleData('fastest');
  const eco = getVehicleData('eco-friendly');
  const balanced = getVehicleData('balanced');

  if (!fastest || !eco || !balanced) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
        <div className="text-yellow-600 text-2xl mb-2">⚠️</div>
        <p className="text-yellow-700">Vehicle-specific savings data not available</p>
      </div>
    );
  }

  const ecoSavings = {
    trip: fastest.cost_per_trip - eco.cost_per_trip,
    monthly: fastest.monthly_cost - eco.monthly_cost,
    annual: fastest.annual_cost - eco.annual_cost
  };

  const balancedSavings = {
    trip: fastest.cost_per_trip - balanced.cost_per_trip,
    monthly: fastest.monthly_cost - balanced.monthly_cost,
    annual: fastest.annual_cost - balanced.annual_cost
  };

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <h4 className="font-bold text-green-700 mb-4 text-center flex items-center justify-center">
          🌱 Eco vs Fastest Route Savings
        </h4>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-green-700">Per Trip:</span>
            <span className="font-bold text-green-800">₹{ecoSavings.trip.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-green-700">Monthly (20 trips):</span>
            <span className="font-bold text-green-800">₹{ecoSavings.monthly.toFixed(0)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-green-700">Annual (240 trips):</span>
            <span className="font-bold text-green-800 text-lg">₹{ecoSavings.annual.toFixed(0)}</span>
          </div>
        </div>
        <div className="mt-4 p-3 bg-green-100 rounded text-sm text-green-700 text-center">
          💚 Choose eco-friendly for maximum savings!
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h4 className="font-bold text-blue-700 mb-4 text-center flex items-center justify-center">
          ⚖️ Balanced vs Fastest Route Savings
        </h4>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-blue-700">Per Trip:</span>
            <span className="font-bold text-blue-800">₹{balancedSavings.trip.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-blue-700">Monthly (20 trips):</span>
            <span className="font-bold text-blue-800">₹{balancedSavings.monthly.toFixed(0)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-blue-700">Annual (240 trips):</span>
            <span className="font-bold text-blue-800 text-lg">₹{balancedSavings.annual.toFixed(0)}</span>
          </div>
        </div>
        <div className="mt-4 p-3 bg-blue-100 rounded text-sm text-blue-700 text-center">
          ⚡ Good balance of time and savings
        </div>
      </div>
    </div>
  );
};

const VehicleComparison = ({ routes, onVehicleChange }) => {
  const [selectedRoute, setSelectedRoute] = useState('eco-friendly');
  
  const vehicleTypes = ['petrol', 'diesel', 'cng', 'electric', 'hybrid'];
  const vehicleLabels = {
    'petrol': 'Petrol Car',
    'diesel': 'Diesel Car',
    'cng': 'CNG Car', 
    'electric': 'Electric Car',
    'hybrid': 'Hybrid Car'
  };

  const routeData = routes.find(r => r.type === selectedRoute);
  const vehicleBreakdown = routeData?.fuel_analysis?.vehicle_breakdown;

  if (!vehicleBreakdown) {
    return (
      <div className="text-center py-8 text-gray-500">
        <div className="text-4xl mb-2">📊</div>
        <p>Vehicle comparison data not available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Route Selector */}
      <div className="flex justify-center space-x-2">
        {['fastest', 'balanced', 'eco-friendly'].map(routeType => (
          <button
            key={routeType}
            onClick={() => setSelectedRoute(routeType)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              selectedRoute === routeType
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {routeType === 'fastest' && '🚀 Fastest'}
            {routeType === 'balanced' && '⚖️ Balanced'} 
            {routeType === 'eco-friendly' && '🌱 Eco-Friendly'}
          </button>
        ))}
      </div>

      {/* Vehicle Comparison Table */}
      <div className="overflow-x-auto">
        <table className="w-full bg-white rounded-lg shadow">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-3 text-left font-bold text-gray-700">Vehicle Type</th>
              <th className="px-4 py-3 text-center font-bold text-gray-700">Per Trip</th>
              <th className="px-4 py-3 text-center font-bold text-gray-700">Monthly</th>
              <th className="px-4 py-3 text-center font-bold text-gray-700">Annual</th>
              <th className="px-4 py-3 text-center font-bold text-gray-700">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {vehicleTypes.map(vehicleType => {
              const data = vehicleBreakdown[vehicleType];
              if (!data) return null;

              return (
                <tr key={vehicleType} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {vehicleLabels[vehicleType]}
                  </td>
                  <td className="px-4 py-3 text-center font-bold">
                    ₹{data.cost_per_trip?.toFixed(2) || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-center font-bold">
                    ₹{data.monthly_cost?.toFixed(0) || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-center font-bold">
                    ₹{data.annual_cost?.toFixed(0) || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => onVehicleChange(vehicleType)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-all"
                    >
                      Select
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const ResultsDashboard = ({ routes, selectedVehicle, onVehicleChange }) => {
  const [selectedRouteIndex, setSelectedRouteIndex] = useState(0);
  const [activeTab, setActiveTab] = useState('routes');

  if (!routes || routes.length === 0) {
    return null;
  }

  const selectedRoute = routes[selectedRouteIndex];
  const vehicleData = selectedRoute?.fuel_analysis?.vehicle_breakdown?.[selectedVehicle];

  return (
    <div className="space-y-6">
      {/* Route Cards */}
      <div className="bg-white rounded-lg card-shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
          📊 Route Analysis Dashboard
        </h2>
        
        <div className="grid lg:grid-cols-3 gap-6 mb-6">
          {routes.map((route, index) => (
            <RouteCard
              key={route.type}
              route={route}
              index={index}
              isSelected={selectedRouteIndex === index}
              onClick={() => setSelectedRouteIndex(index)}
              vehicleData={route.fuel_analysis?.vehicle_breakdown?.[selectedVehicle]}
            />
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg card-shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'routes', label: 'Route Details', icon: '📍' },
              { id: 'savings', label: 'Savings Analysis', icon: '💰' },
              { id: 'compare', label: 'Vehicle Comparison', icon: '🚗' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-all ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'routes' && (
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-xl font-bold text-gray-800 mb-2">
                  Selected Route: {selectedRoute.type?.toUpperCase().replace('-', ' ')}
                </h3>
                <p className="text-gray-600">
                  Vehicle: {selectedVehicle.charAt(0).toUpperCase() + selectedVehicle.slice(1)} Car
                </p>
              </div>

              {vehicleData && (
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-semibold text-blue-700 mb-2">Trip Cost</h4>
                    <p className="text-2xl font-bold text-blue-800">
                      ₹{vehicleData.cost_per_trip?.toFixed(2) || 'N/A'}
                    </p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <h4 className="font-semibold text-green-700 mb-2">Monthly Cost</h4>
                    <p className="text-2xl font-bold text-green-800">
                      ₹{vehicleData.monthly_cost?.toFixed(0) || 'N/A'}
                    </p>
                    <p className="text-xs text-green-600">20 trips/month</p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <h4 className="font-semibold text-purple-700 mb-2">Annual Cost</h4>
                    <p className="text-2xl font-bold text-purple-800">
                      ₹{vehicleData.annual_cost?.toFixed(0) || 'N/A'}
                    </p>
                    <p className="text-xs text-purple-600">240 trips/year</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'savings' && (
            <SavingsComparison routes={routes} selectedVehicle={selectedVehicle} />
          )}

          {activeTab === 'compare' && (
            <VehicleComparison routes={routes} onVehicleChange={onVehicleChange} />
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsDashboard;