import React, { useState } from 'react';

const RouteInput = ({ 
  startLocation, 
  endLocation, 
  onStartLocationChange, 
  onEndLocationChange, 
  onSearch, 
  onReset, 
  loading, 
  disabled 
}) => {
  const [suggestions, setSuggestions] = useState({ start: [], end: [] });
  const [showSuggestions, setShowSuggestions] = useState({ start: false, end: false });

  // Sample location suggestions for demo
  const commonLocations = [
    'Connaught Place, New Delhi',
    'India Gate, New Delhi',
    'Red Fort, New Delhi', 
    'Rajouri Garden, New Delhi',
    'Karol Bagh, New Delhi',
    'Gurgaon Cyber City',
    'Noida Sector 18',
    'Airport Metro Station, New Delhi',
    'AIIMS, New Delhi',
    'IIT Delhi'
  ];

  const handleLocationInput = (value, type) => {
    if (type === 'start') {
      onStartLocationChange(value);
    } else {
      onEndLocationChange(value);
    }

    // Simple suggestion matching
    if (value.length > 2) {
      const matches = commonLocations.filter(location => 
        location.toLowerCase().includes(value.toLowerCase())
      );
      setSuggestions(prev => ({ ...prev, [type]: matches.slice(0, 5) }));
      setShowSuggestions(prev => ({ ...prev, [type]: true }));
    } else {
      setShowSuggestions(prev => ({ ...prev, [type]: false }));
    }
  };

  const selectSuggestion = (location, type) => {
    if (type === 'start') {
      onStartLocationChange(location);
    } else {
      onEndLocationChange(location);
    }
    setShowSuggestions(prev => ({ ...prev, [type]: false }));
  };

  const swapLocations = () => {
    const temp = startLocation;
    onStartLocationChange(endLocation);
    onEndLocationChange(temp);
  };

  const canSearch = startLocation.trim() && endLocation.trim() && !loading;

  return (
    <div className="bg-white rounded-lg card-shadow p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
        📍 Route Planning
      </h2>

      <div className="space-y-6">
        {/* Start Location */}
        <div className="relative">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            From (Start Location)
          </label>
          <div className="relative">
            <input
              type="text"
              value={startLocation}
              onChange={(e) => handleLocationInput(e.target.value, 'start')}
              onFocus={() => setShowSuggestions(prev => ({ ...prev, start: suggestions.start.length > 0 }))}
              onBlur={() => setTimeout(() => setShowSuggestions(prev => ({ ...prev, start: false })), 200)}
              placeholder="Enter starting point (e.g., Connaught Place, New Delhi)"
              disabled={disabled}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-green-500">
              🟢
            </div>
          </div>
          
          {/* Start Location Suggestions */}
          {showSuggestions.start && suggestions.start.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
              {suggestions.start.map((location, index) => (
                <div
                  key={index}
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer text-sm"
                  onClick={() => selectSuggestion(location, 'start')}
                >
                  📍 {location}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Swap Button */}
        <div className="flex justify-center">
          <button
            type="button"
            onClick={swapLocations}
            disabled={disabled}
            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Swap locations"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
            </svg>
          </button>
        </div>

        {/* End Location */}
        <div className="relative">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            To (Destination)
          </label>
          <div className="relative">
            <input
              type="text"
              value={endLocation}
              onChange={(e) => handleLocationInput(e.target.value, 'end')}
              onFocus={() => setShowSuggestions(prev => ({ ...prev, end: suggestions.end.length > 0 }))}
              onBlur={() => setTimeout(() => setShowSuggestions(prev => ({ ...prev, end: false })), 200)}
              placeholder="Enter destination (e.g., India Gate, New Delhi)"
              disabled={disabled}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-red-500">
              🔴
            </div>
          </div>

          {/* End Location Suggestions */}
          {showSuggestions.end && suggestions.end.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
              {suggestions.end.map((location, index) => (
                <div
                  key={index}
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer text-sm"
                  onClick={() => selectSuggestion(location, 'end')}
                >
                  📍 {location}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-4 pt-4">
          <button
            onClick={onSearch}
            disabled={!canSearch}
            className={`flex-1 flex items-center justify-center py-3 px-6 rounded-lg font-semibold transition-all duration-200 ${
              canSearch
                ? 'bg-blue-600 hover:bg-blue-700 text-white transform hover:scale-105'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {loading ? (
              <>
                <div className="loading-spinner w-5 h-5 mr-2"></div>
                Finding Routes...
              </>
            ) : (
              <>
                🔍 Find Best Routes
              </>
            )}
          </button>

          <button
            onClick={onReset}
            disabled={loading}
            className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🔄 Reset
          </button>
        </div>
      </div>

      {/* Tips */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-semibold text-blue-800 mb-2">💡 Tips for better results:</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Include city name for better accuracy (e.g., "CP, New Delhi")</li>
          <li>• Use specific landmarks or addresses</li>
          <li>• Try popular locations from the suggestions</li>
        </ul>
      </div>
    </div>
  );
};

export default RouteInput;