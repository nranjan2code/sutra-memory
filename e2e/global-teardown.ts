import { FullConfig } from '@playwright/test'

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Running Playwright E2E Tests Global Teardown')
  
  // Clean up any test data if needed
  // For now, we don't need to clean up Docker services as they should remain running
  
  console.log('✅ Global teardown completed')
}

export default globalTeardown