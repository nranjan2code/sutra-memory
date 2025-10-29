/**
 * ErrorBoundary Component
 * Production-grade React error boundary for graceful error handling
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Text, Card, Button } from '@sutra/ui-framework';
import './ErrorBoundary.css';

interface Props {
  children: ReactNode;
  fallbackComponent?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // Call optional error handler
    this.props.onError?.(error, errorInfo);
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  public render() {
    if (this.state.hasError) {
      // Custom fallback component
      if (this.props.fallbackComponent) {
        return this.props.fallbackComponent;
      }

      // Default fallback UI
      return (
        <div className="error-boundary-container">
          <Card variant="outlined" className="error-boundary-card">
            <div className="error-boundary-header">
              <Text variant="h4" color="error">
                ⚠️ Something went wrong
              </Text>
            </div>

            <div className="error-boundary-content">
              <Text variant="body1" color="secondary">
                The application encountered an unexpected error.
              </Text>

              {this.state.error && (
                <div className="error-details">
                  <Text variant="caption" className="error-label">
                    Error Message:
                  </Text>
                  <Text variant="body2" className="error-message">
                    {this.state.error.toString()}
                  </Text>
                </div>
              )}

              {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                <details className="error-stack">
                  <summary>
                    <Text variant="caption">Stack Trace (Development Only)</Text>
                  </summary>
                  <pre className="error-stack-trace">
                    {this.state.errorInfo.componentStack}
                  </pre>
                </details>
              )}
            </div>

            <div className="error-boundary-actions">
              <Button variant="primary" onClick={this.handleReset}>
                Try Again
              </Button>
              <Button variant="ghost" onClick={() => window.location.reload()}>
                Reload Page
              </Button>
            </div>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
