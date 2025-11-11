import React from 'react';

const vehicleOptions = [
  {
    value: 'petrol',
    label: 'Petrol Car',
    icon: '⛽',
    efficiency: '15 km/L',
    cost: '₹110/L',
    description: 'Standard gasoline vehicle'
  },
  {
    value: 'diesel',
    label: 'Diesel Car',
    icon: '🚗',
    efficiency: '20 km/L',
    cost: '₹95/L',
    description: 'Diesel-powered vehicle'
  },
  {
    value: 'cng',
    label: 'CNG Car',
    icon: '🌿',
    efficiency: '25 km/kg',
    cost: '₹85/kg',
    description: 'Compressed Natural Gas'
  },
  {
    value: 'electric',
    label: 'Electric Car',
    icon: '🔋',
    efficiency: '5 km/kWh',
    cost: '₹8/kWh',
    description: 'Battery Electric Vehicle'
  },
  {
    value: 'hybrid',
    label: 'Hybrid Car',
    icon: '🔋⛽',
    efficiency: '25 km/L',
    cost: '₹110/L',
    description: 'Hybrid Electric Vehicle'
  }
];

const VehicleSelector = ({ selectedVehicle, onVehicleChange, disabled }) => {
  return (
    <div className="bg-white rounded-lg card-shadow p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
        🚗 Select Your Vehicle
      </h2>
      
      <div className="space-y-3">
        {vehicleOptions.map((vehicle) => (
          <div
            key={vehicle.value}
            className={`relative border-2 rounded-lg p-4 cursor-pointer transition-all duration-200 ${
              selectedVehicle === vehicle.value
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={() => !disabled && onVehicleChange(vehicle.value)}
          >
            <div className="flex items-center space-x-3">
              <div className="text-2xl">{vehicle.icon}</div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-800">{vehicle.label}</h3>
                  {selectedVehicle === vehicle.value && (
                    <div className="text-blue-500 font-bold">✓</div>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-1">{vehicle.description}</p>
                <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                  <span className="bg-green-100 text-green-700 px-2 py-1 rounded">
                    {vehicle.efficiency}
                  </span>
                  <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">
                    {vehicle.cost}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Radio button indicator */}
            <input
              type="radio"
              name="vehicle"
              value={vehicle.value}
              checked={selectedVehicle === vehicle.value}
              onChange={() => !disabled && onVehicleChange(vehicle.value)}
              className="absolute top-4 right-4 text-blue-600"
              disabled={disabled}
            />
          </div>
        ))}
      </div>
      
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600">
          💡 <strong>Tip:</strong> Different vehicles have varying fuel costs and efficiency. 
          Choose your vehicle type for accurate savings calculations.
        </p>
      </div>
    </div>
  );
};

export default VehicleSelector;