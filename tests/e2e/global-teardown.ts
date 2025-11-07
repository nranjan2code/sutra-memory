import { FullConfig } from '@playwright/test';

/**
 * Global teardown for Sutra AI E2E tests
 * Cleanup and reporting after all tests complete
 */
async function globalTeardown(config: FullConfig) {
  console.log('🧹 Cleaning up after Sutra AI E2E tests');
  
  // Optional: Clean up any test data
  try {
    // Could add cleanup logic here if needed
    // For now, we let the test data remain in the system
    console.log('✅ Test data preserved for analysis');
  } catch (error) {
    console.warn('⚠️  Cleanup warning:', error.message);
  }
  
  // Report test completion
  console.log('🎉 Sutra AI E2E test suite completed');
  console.log('📊 Check test reports in playwright-report/ directory');
}

export default globalTeardown;