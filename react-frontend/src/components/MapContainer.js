import React, { useEffect, useRef } from 'react';

const MapContainer = React.forwardRef(({ routes, startLocation, endLocation }, ref) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const directionsRendererRefs = useRef([]);

  useEffect(() => {
    if (!window.google || !routes || routes.length === 0) return;

    const initMap = () => {
      // Initialize map centered on Delhi
      const map = new window.google.maps.Map(mapRef.current, {
        zoom: 12,
        center: { lat: 28.6139, lng: 77.2090 }, // Delhi center
        mapTypeId: 'roadmap',
        styles: [
          {
            featureType: 'poi',
            elementType: 'labels',
            stylers: [{ visibility: 'off' }]
          }
        ]
      });

      mapInstanceRef.current = map;

      // Clear existing renderers
      directionsRendererRefs.current.forEach(renderer => renderer.setMap(null));
      directionsRendererRefs.current = [];

      // Route colors matching the backend
      const routeColors = {
        'fastest': '#FF6B00',     // Dark Orange
        'eco-friendly': '#006400', // Dark Green  
        'balanced': '#000080'      // Dark Blue
      };

      // Create directions renderers for each route
      routes.forEach((route, index) => {
        if (!route.polyline || !route.polyline.points) return;

        const directionsRenderer = new window.google.maps.DirectionsRenderer({
          map: map,
          suppressMarkers: false,
          polylineOptions: {
            strokeColor: routeColors[route.type] || '#666666',
            strokeWeight: 6,
            strokeOpacity: 0.8
          },
          markerOptions: {
            icon: {
              url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(
                `<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="16" cy="16" r="14" fill="${routeColors[route.type] || '#666666'}" stroke="white" stroke-width="2"/>
                  <text x="16" y="20" text-anchor="middle" fill="white" font-size="14" font-weight="bold">${index + 1}</text>
                </svg>`
              )}`
            }
          }
        });

        directionsRendererRefs.current.push(directionsRenderer);

        // Decode and display the polyline
        try {
          const path = window.google.maps.geometry.encoding.decodePath(route.polyline.points);
          
          const polyline = new window.google.maps.Polyline({
            path: path,
            strokeColor: routeColors[route.type] || '#666666',
            strokeWeight: 6,
            strokeOpacity: 0.8,
            map: map
          });

          // Add markers for start and end
          if (index === 0) { // Only add markers once
            new window.google.maps.Marker({
              position: path[0],
              map: map,
              title: startLocation,
              icon: {
                path: window.google.maps.SymbolPath.CIRCLE,
                scale: 8,
                fillColor: '#10B981',
                fillOpacity: 1,
                strokeWeight: 2,
                strokeColor: '#ffffff'
              }
            });

            new window.google.maps.Marker({
              position: path[path.length - 1],
              map: map,
              title: endLocation,
              icon: {
                path: window.google.maps.SymbolPath.CIRCLE,
                scale: 8,
                fillColor: '#EF4444',
                fillOpacity: 1,
                strokeWeight: 2,
                strokeColor: '#ffffff'
              }
            });
          }

          // Fit map to show all routes
          const bounds = new window.google.maps.LatLngBounds();
          path.forEach(point => bounds.extend(point));
          map.fitBounds(bounds);

        } catch (error) {
          console.error('Error displaying route:', error);
        }
      });
    };

    // Wait for Google Maps to be loaded
    if (window.google && window.google.maps) {
      initMap();
    } else {
      console.error('Google Maps not loaded');
    }

  }, [routes, startLocation, endLocation]);

  if (!routes || routes.length === 0) {
    return (
      <div className="bg-white rounded-lg card-shadow p-6 h-96 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <div className="text-4xl mb-4">🗺️</div>
          <p>Map will appear here after route calculation</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg card-shadow overflow-hidden">
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-bold text-gray-800 flex items-center">
          🗺️ Route Visualization
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Color-coded routes: 
          <span className="ml-2 inline-flex items-center space-x-4">
            <span className="flex items-center">
              <div className="w-4 h-4 bg-orange-500 rounded mr-1"></div>
              Fastest
            </span>
            <span className="flex items-center">
              <div className="w-4 h-4 bg-green-600 rounded mr-1"></div>
              Eco-Friendly
            </span>
            <span className="flex items-center">
              <div className="w-4 h-4 bg-blue-800 rounded mr-1"></div>
              Balanced
            </span>
          </span>
        </p>
      </div>
      <div 
        ref={mapRef} 
        className="h-96 w-full"
        style={{ minHeight: '400px' }}
      ></div>
    </div>
  );
});

MapContainer.displayName = 'MapContainer';

export default MapContainer;