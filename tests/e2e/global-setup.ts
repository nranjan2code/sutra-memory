import { FullConfig } from '@playwright/test';

/**
 * Global setup for Sutra AI E2E tests
 * Validates that all required services are running before tests begin
 */
async function globalSetup(config: FullConfig) {
  console.log('🚀 Setting up Sutra AI E2E Test Environment');
  
  // Check if Sutra services are running
  try {
    const response = await fetch('http://localhost:8080/api/health');
    const health = await response.json();
    
    if (response.ok && health.status === 'healthy') {
      console.log('✅ Sutra API is healthy and ready');
      console.log(`📊 API Version: ${health.version}`);
      console.log(`⏱️  API Uptime: ${Math.round(health.uptime_seconds)}s`);
    } else {
      throw new Error(`API health check failed: ${health.status}`);
    }
  } catch (error) {
    console.error('❌ Sutra services are not running properly');
    console.error('Please run: sutra deploy');
    console.error('And ensure all services are healthy with: sutra status');
    throw error;
  }
  
  // Validate required services
  const requiredServices = [
    'http://localhost:8080/api/health', // Main API
    // Add more service checks as needed
  ];
  
  for (const serviceUrl of requiredServices) {
    try {
      const response = await fetch(serviceUrl);
      if (!response.ok) {
        throw new Error(`Service ${serviceUrl} returned ${response.status}`);
      }
      console.log(`✅ Service available: ${serviceUrl}`);
    } catch (error) {
      console.error(`❌ Service unavailable: ${serviceUrl}`);
      throw error;
    }
  }
  
  console.log('🎯 Environment setup complete - Ready for continuous learning tests');
}

export default globalSetup;