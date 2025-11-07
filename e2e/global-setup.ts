import { chromium, FullConfig } from '@playwright/test'

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting Playwright E2E Tests Global Setup')
  
  // Validate that Sutra services are running
  const browser = await chromium.launch()
  const page = await browser.newPage()
  
  try {
    // Check if the web client is accessible
    console.log('📋 Checking Sutra web client accessibility...')
    const response = await page.goto('http://localhost:8080', { waitUntil: 'networkidle' })
    
    if (!response?.ok()) {
      throw new Error(`Web client not accessible: ${response?.status()} ${response?.statusText()}`)
    }
    
    // Check if API is accessible
    console.log('📋 Checking Sutra API accessibility...')
    const apiResponse = await page.request.get('http://localhost:8080/api/health')
    
    if (!apiResponse.ok()) {
      console.warn(`⚠️  API health check failed: ${apiResponse.status()} ${apiResponse.statusText()}`)
      console.warn('This might be expected if auth is required for health endpoint')
    } else {
      console.log('✅ API is accessible')
    }
    
    console.log('✅ Global setup completed successfully')
    
  } catch (error) {
    console.error('❌ Global setup failed:', error)
    throw error
  } finally {
    await browser.close()
  }
}

export default globalSetup