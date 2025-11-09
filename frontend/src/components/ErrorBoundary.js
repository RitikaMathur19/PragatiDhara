import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      // Fallback UI
      return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">Something Went Wrong</h1>
            <p className="text-gray-600 mb-4">
              The application encountered an unexpected error. Please refresh the page or try again later.
            </p>
            
            {this.props.showDetails && this.state.error && (
              <details className="text-left text-sm bg-gray-50 p-3 rounded border">
                <summary className="cursor-pointer font-semibold text-gray-700 mb-2">
                  Error Details
                </summary>
                <div className="text-red-600 font-mono">
                  {this.state.error.toString()}
                </div>
                {this.state.errorInfo.componentStack && (
                  <div className="text-gray-600 font-mono text-xs mt-2">
                    {this.state.errorInfo.componentStack}
                  </div>
                )}
              </details>
            )}
            
            <div className="flex gap-3 mt-6">
              <button 
                onClick={() => window.location.reload()} 
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
              >
                🔄 Refresh Page
              </button>
              <button 
                onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })} 
                className="flex-1 bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition"
              >
                🔄 Try Again
              </button>
            </div>
          </div>
        </div>
      );
    }

    // No error, render children normally
    return this.props.children;
  }
}

export default ErrorBoundary;