import React from 'react';

const GreenCreditsDisplay = ({ route, isLarge = false }) => {
  const credits = route?.green_credits_earned || 0;
  
  const getCreditsColor = (credits) => {
    if (credits === 0) return 'text-gray-500';
    if (credits < 5) return 'text-yellow-600';
    if (credits < 10) return 'text-green-600';
    return 'text-emerald-600';
  };

  const getCreditsBackground = (credits) => {
    if (credits === 0) return 'bg-gray-100';
    if (credits < 5) return 'bg-yellow-50';
    if (credits < 10) return 'bg-green-50';
    return 'bg-emerald-50';
  };

  const getCreditsBorder = (credits) => {
    if (credits === 0) return 'border-gray-300';
    if (credits < 5) return 'border-yellow-300';
    if (credits < 10) return 'border-green-300';
    return 'border-emerald-300';
  };

  const getMessage = (credits) => {
    if (credits === 0) return 'No credits';
    if (credits < 5) return 'Small reward';
    if (credits < 10) return 'Good reward!';
    return 'Great reward!';
  };

  if (isLarge) {
    return (
      <div className={`${getCreditsBackground(credits)} ${getCreditsBorder(credits)} border-2 rounded-lg p-4`}>
        <div className="text-center">
          <div className="text-3xl mb-2">
            {credits > 0 ? '🌟' : '⚪'}
          </div>
          <div className={`text-2xl font-bold ${getCreditsColor(credits)} mb-1`}>
            {credits.toFixed(1)}
          </div>
          <div className="text-sm font-semibold text-gray-700">
            Green Credits
          </div>
          <div className={`text-xs mt-1 ${getCreditsColor(credits)}`}>
            {getMessage(credits)}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex items-center justify-between p-3 rounded-lg ${getCreditsBackground(credits)} ${getCreditsBorder(credits)} border`}>
      <div className="flex items-center space-x-2">
        <span className="text-xl">
          {credits > 0 ? '🌟' : '⚪'}
        </span>
        <div>
          <div className="text-xs font-medium text-gray-600">Green Credits</div>
          <div className={`text-sm font-bold ${getCreditsColor(credits)}`}>
            {getMessage(credits)}
          </div>
        </div>
      </div>
      <div className={`text-xl font-bold ${getCreditsColor(credits)}`}>
        +{credits.toFixed(1)}
      </div>
    </div>
  );
};

export const GreenCreditsWallet = ({ userId, className = '' }) => {
  const [wallet, setWallet] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    if (!userId) {
      setWallet({
        total_credits: 0,
        eco_routes_count: 0,
        total_co2_saved_kg: 0
      });
      setLoading(false);
      return;
    }

    const fetchWallet = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8001/api/v1/routes/green-credits/${userId}`);
        if (response.ok) {
          const data = await response.json();
          setWallet(data.wallet);
        } else {
          throw new Error('Failed to fetch wallet');
        }
      } catch (err) {
        console.error('Error fetching wallet:', err);
        setError(err.message);
        // Set default values on error
        setWallet({
          total_credits: 0,
          eco_routes_count: 0,
          total_co2_saved_kg: 0
        });
      } finally {
        setLoading(false);
      }
    };

    fetchWallet();
  }, [userId]);

  if (loading) {
    return (
      <div className={`bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 ${className}`}>
        <div className="animate-pulse flex items-center space-x-3">
          <div className="h-10 w-10 bg-green-200 rounded-full"></div>
          <div className="flex-1">
            <div className="h-4 bg-green-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-green-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300 rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="text-3xl">🌟</div>
          <div>
            <div className="text-xs font-semibold text-green-700 uppercase tracking-wide">
              Your Green Credits
            </div>
            <div className="text-2xl font-bold text-green-800">
              {wallet?.total_credits?.toFixed(1) || '0.0'}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-green-600">
            {wallet?.eco_routes_count || 0} eco trips
          </div>
          <div className="text-xs text-green-600">
            {wallet?.total_co2_saved_kg?.toFixed(1) || '0.0'} kg CO₂ saved
          </div>
        </div>
      </div>
    </div>
  );
};

export const GreenCreditsComparison = ({ routes }) => {
  if (!routes || routes.length === 0) return null;

  const routeTypes = ['eco-friendly', 'balanced', 'fastest'];
  const routeData = routeTypes.map(type => {
    const route = routes.find(r => r.type === type);
    return {
      type,
      credits: route?.green_credits_earned || 0,
      route
    };
  });

  const maxCredits = Math.max(...routeData.map(r => r.credits));

  const getRouteConfig = (type) => {
    const configs = {
      'eco-friendly': { 
        icon: '🌱', 
        title: 'Eco Route',
        color: 'text-green-700',
        bgColor: 'bg-green-100',
        borderColor: 'border-green-400'
      },
      'balanced': { 
        icon: '⚖️', 
        title: 'Balanced',
        color: 'text-blue-700',
        bgColor: 'bg-blue-100',
        borderColor: 'border-blue-400'
      },
      'fastest': { 
        icon: '🚀', 
        title: 'Fastest',
        color: 'text-orange-700',
        bgColor: 'bg-orange-100',
        borderColor: 'border-orange-400'
      }
    };
    return configs[type] || configs['balanced'];
  };

  return (
    <div className="bg-white rounded-lg border-2 border-gray-200 p-6">
      <div className="text-center mb-6">
        <h3 className="text-xl font-bold text-gray-800 flex items-center justify-center gap-2">
          <span>🌟</span>
          <span>Green Credits Comparison</span>
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Earn credits by choosing eco-friendly routes
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {routeData.map(({ type, credits, route }) => {
          const config = getRouteConfig(type);
          const isMax = credits === maxCredits && credits > 0;
          
          return (
            <div 
              key={type}
              className={`relative p-4 rounded-lg border-2 ${config.borderColor} ${config.bgColor} ${
                isMax ? 'ring-4 ring-yellow-300 shadow-lg' : ''
              }`}
            >
              {isMax && credits > 0 && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-yellow-400 text-yellow-900 text-xs font-bold px-3 py-1 rounded-full">
                    ⭐ Best Choice
                  </span>
                </div>
              )}
              
              <div className="text-center">
                <div className="text-2xl mb-2">{config.icon}</div>
                <div className={`font-bold ${config.color} mb-2`}>
                  {config.title}
                </div>
                
                <div className="my-3">
                  <div className="text-3xl font-bold text-gray-800">
                    {credits > 0 ? '🌟' : '⚪'}
                  </div>
                  <div className={`text-2xl font-bold ${credits > 0 ? 'text-green-600' : 'text-gray-400'} mt-1`}>
                    {credits.toFixed(1)}
                  </div>
                  <div className="text-xs text-gray-600 font-medium mt-1">
                    credits
                  </div>
                </div>

                {credits === 0 ? (
                  <div className="text-xs text-gray-500 italic">
                    No credits for this route
                  </div>
                ) : (
                  <div className="text-xs text-green-700 font-medium">
                    +{credits.toFixed(1)} to your wallet!
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
        <div className="flex items-start space-x-3">
          <div className="text-2xl">💡</div>
          <div className="flex-1">
            <div className="font-semibold text-green-800 mb-1">How to earn more credits:</div>
            <ul className="text-sm text-green-700 space-y-1">
              <li>• Choose eco-friendly routes for maximum credits</li>
              <li>• Balanced routes earn 60% credits</li>
              <li>• Fastest routes earn no credits</li>
              <li>• Credits based on distance + CO₂ savings</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GreenCreditsDisplay;
