import { Page, expect } from '@playwright/test'

/**
 * API Test Utilities for direct API testing and validation
 */
export class ApiTestUtils {
  private baseUrl: string
  private page: Page

  constructor(page: Page, baseUrl: string = 'http://localhost:8080/api') {
    this.page = page
    this.baseUrl = baseUrl
  }

  /**
   * Test API health endpoint
   */
  async testHealth(): Promise<boolean> {
    try {
      const response = await this.page.request.get(`${this.baseUrl}/health`)
      return response.ok()
    } catch (error) {
      console.warn('Health check failed:', error)
      return false
    }
  }

  /**
   * Test API authentication endpoints
   */
  async testAuthEndpoints() {
    const testEmail = `test_${Date.now()}@example.com`
    const testPassword = 'testpassword123'
    const testOrg = `Test Org ${Date.now()}`

    try {
      // Test registration
      const registerResponse = await this.page.request.post(`${this.baseUrl}/auth/register`, {
        data: {
          email: testEmail,
          password: testPassword,
          organization: testOrg,
          full_name: 'Test User'
        }
      })

      console.log('Registration response:', registerResponse.status())

      // Test login
      const loginResponse = await this.page.request.post(`${this.baseUrl}/auth/login`, {
        data: {
          email: testEmail,
          password: testPassword
        }
      })

      console.log('Login response:', loginResponse.status())

      return {
        registration: registerResponse.ok(),
        login: loginResponse.ok(),
        testUser: { email: testEmail, password: testPassword, organization: testOrg }
      }
    } catch (error) {
      console.error('Auth endpoint test failed:', error)
      return {
        registration: false,
        login: false,
        testUser: null
      }
    }
  }

  /**
   * Test reasoning API
   */
  async testReasoningApi(query: string = 'What is AI?'): Promise<boolean> {
    try {
      const response = await this.page.request.post(`${this.baseUrl}/reason`, {
        data: { query }
      })
      
      if (response.ok()) {
        const data = await response.json()
        return data && typeof data === 'object'
      }
      return false
    } catch (error) {
      console.warn('Reasoning API test failed:', error)
      return false
    }
  }

  /**
   * Test learning API
   */
  async testLearningApi(content: string = 'Test fact for learning'): Promise<boolean> {
    try {
      const response = await this.page.request.post(`${this.baseUrl}/learn`, {
        data: { content }
      })
      
      return response.ok()
    } catch (error) {
      console.warn('Learning API test failed:', error)
      return false
    }
  }
}

/**
 * Performance monitoring utilities
 */
export class PerformanceTestUtils {
  private page: Page
  private metrics: any[] = []

  constructor(page: Page) {
    this.page = page
  }

  /**
   * Start performance monitoring
   */
  async startMonitoring() {
    this.metrics = []
    
    // Listen to console logs for performance data
    this.page.on('console', (msg) => {
      if (msg.text().includes('Performance:')) {
        this.metrics.push({
          timestamp: Date.now(),
          message: msg.text()
        })
      }
    })

    // Monitor network requests
    this.page.on('response', (response) => {
      if (response.url().includes('/api/')) {
        this.metrics.push({
          timestamp: Date.now(),
          type: 'api_request',
          url: response.url(),
          status: response.status(),
          timing: response.timing
        })
      }
    })
  }

  /**
   * Get performance metrics
   */
  getMetrics() {
    return this.metrics
  }

  /**
   * Measure page load time
   */
  async measurePageLoad(url: string): Promise<number> {
    const startTime = Date.now()
    await this.page.goto(url)
    await this.page.waitForLoadState('networkidle')
    const endTime = Date.now()
    
    return endTime - startTime
  }

  /**
   * Measure interaction response time
   */
  async measureInteractionTime(action: () => Promise<void>): Promise<number> {
    const startTime = Date.now()
    await action()
    const endTime = Date.now()
    
    return endTime - startTime
  }
}

/**
 * Test data management utilities
 */
export class TestDataUtils {
  private static createdUsers: any[] = []
  private static createdConversations: any[] = []

  /**
   * Create test user data
   */
  static createTestUser() {
    const user = {
      email: `test_${Date.now()}_${Math.random().toString(36).substring(7)}@example.com`,
      password: this.generateSecurePassword(),
      organization: `Test Org ${Date.now()}`,
      fullName: `Test User ${Math.random().toString(36).substring(7)}`
    }
    
    this.createdUsers.push(user)
    return user
  }

  /**
   * Create test conversation data
   */
  static createTestConversation() {
    const conversation = {
      id: `conv_${Date.now()}_${Math.random().toString(36).substring(7)}`,
      title: `Test Conversation ${Date.now()}`,
      messages: [
        'Hello, this is a test conversation.',
        'How are you today?',
        'Can you help me with some questions?'
      ]
    }
    
    this.createdConversations.push(conversation)
    return conversation
  }

  /**
   * Generate secure password for testing
   */
  static generateSecurePassword(): string {
    const length = 12
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
    let password = ''
    
    // Ensure password has at least one of each required type
    password += 'A' // uppercase
    password += 'a' // lowercase
    password += '1' // number
    password += '!' // special char
    
    // Fill rest randomly
    for (let i = 4; i < length; i++) {
      password += charset.charAt(Math.floor(Math.random() * charset.length))
    }
    
    // Shuffle the password
    return password.split('').sort(() => 0.5 - Math.random()).join('')
  }

  /**
   * Create test knowledge base content
   */
  static createTestKnowledge() {
    return [
      'Artificial Intelligence is the simulation of human intelligence in machines.',
      'Machine Learning is a subset of AI that enables computers to learn without being explicitly programmed.',
      'Deep Learning uses neural networks with multiple layers to process data.',
      'Natural Language Processing helps computers understand and generate human language.',
      'Computer Vision enables machines to interpret and understand visual information.',
      'Robotics combines AI with mechanical engineering to create intelligent machines.',
      'Expert Systems are AI programs that mimic human expertise in specific domains.',
      'Neural Networks are computing systems inspired by biological neural networks.'
    ]
  }

  /**
   * Create test queries for reasoning
   */
  static createTestQueries() {
    return [
      'What is artificial intelligence?',
      'How does machine learning work?',
      'What are the applications of AI?',
      'Explain the difference between AI and ML',
      'What is deep learning?',
      'How is NLP used in AI?',
      'What are neural networks?',
      'Give me examples of AI in daily life'
    ]
  }

  /**
   * Clean up test data
   */
  static cleanup() {
    console.log(`Cleaning up ${this.createdUsers.length} test users and ${this.createdConversations.length} conversations`)
    this.createdUsers = []
    this.createdConversations = []
  }

  /**
   * Get all created test data
   */
  static getCreatedData() {
    return {
      users: this.createdUsers,
      conversations: this.createdConversations
    }
  }
}

/**
 * UI validation utilities
 */
export class UiValidationUtils {
  private page: Page

  constructor(page: Page) {
    this.page = page
  }

  /**
   * Check for common accessibility issues
   */
  async checkAccessibility() {
    const issues = []

    // Check for alt text on images
    const images = await this.page.locator('img').all()
    for (const img of images) {
      const alt = await img.getAttribute('alt')
      if (!alt) {
        issues.push('Image missing alt text')
      }
    }

    // Check for proper heading structure
    const headings = await this.page.locator('h1, h2, h3, h4, h5, h6').all()
    if (headings.length === 0) {
      issues.push('No headings found on page')
    }

    // Check for form labels
    const inputs = await this.page.locator('input[type="text"], input[type="email"], input[type="password"], textarea').all()
    for (const input of inputs) {
      const label = await input.getAttribute('aria-label')
      const labelElement = await this.page.locator(`label[for="${await input.getAttribute('id')}"]`).count()
      
      if (!label && labelElement === 0) {
        issues.push('Input missing label or aria-label')
      }
    }

    return issues
  }

  /**
   * Check for responsive design
   */
  async checkResponsiveness() {
    const viewports = [
      { width: 320, height: 568 },  // Mobile
      { width: 768, height: 1024 }, // Tablet
      { width: 1024, height: 768 }, // Desktop small
      { width: 1920, height: 1080 } // Desktop large
    ]

    const results = []

    for (const viewport of viewports) {
      await this.page.setViewportSize(viewport)
      await this.page.waitForTimeout(1000) // Let layout settle

      // Check if content is still accessible
      const isUsable = await this.checkContentUsability()
      
      results.push({
        viewport,
        usable: isUsable
      })
    }

    return results
  }

  /**
   * Check if content is usable at current viewport
   */
  private async checkContentUsability(): Promise<boolean> {
    try {
      // Check if main interactive elements are visible and clickable
      const messageInput = this.page.locator('textarea, input[placeholder*="message"]').first()
      const sendButton = this.page.locator('button[type="submit"], button:has-text("Send")').first()

      const inputVisible = await messageInput.isVisible().catch(() => false)
      const buttonVisible = await sendButton.isVisible().catch(() => false)

      return inputVisible && buttonVisible
    } catch (error) {
      return false
    }
  }

  /**
   * Check for console errors
   */
  async checkConsoleErrors(): Promise<string[]> {
    const errors = []
    
    this.page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })

    this.page.on('pageerror', (error) => {
      errors.push(`Page Error: ${error.message}`)
    })

    return errors
  }

  /**
   * Validate page load performance
   */
  async validatePagePerformance() {
    const performanceEntries = await this.page.evaluate(() => {
      return JSON.stringify(performance.getEntriesByType('navigation'))
    })

    const navigation = JSON.parse(performanceEntries)[0]
    
    return {
      loadTime: navigation.loadEventEnd - navigation.loadEventStart,
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
      totalTime: navigation.loadEventEnd - navigation.fetchStart
    }
  }
}

/**
 * Test environment utilities
 */
export class TestEnvironmentUtils {
  /**
   * Wait for services to be ready
   */
  static async waitForServices(page: Page, timeout: number = 30000): Promise<boolean> {
    const startTime = Date.now()
    
    while (Date.now() - startTime < timeout) {
      try {
        // Check web client
        const webResponse = await page.request.get('http://localhost:8080')
        if (!webResponse.ok()) {
          await new Promise(resolve => setTimeout(resolve, 1000))
          continue
        }

        // Check API
        const apiResponse = await page.request.get('http://localhost:8080/api/health')
        if (apiResponse.ok() || apiResponse.status() === 401) { // 401 might be expected for auth
          return true
        }

        await new Promise(resolve => setTimeout(resolve, 1000))
      } catch (error) {
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
    }
    
    return false
  }

  /**
   * Get environment info
   */
  static async getEnvironmentInfo(page: Page) {
    try {
      const apiInfo = await page.request.get('http://localhost:8080/api/edition').catch(() => null)
      const healthInfo = await page.request.get('http://localhost:8080/api/health').catch(() => null)
      
      return {
        webClientAccessible: true,
        apiAccessible: apiInfo?.ok() || healthInfo?.ok(),
        apiEdition: apiInfo?.ok() ? await apiInfo.json().catch(() => null) : null,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      return {
        webClientAccessible: false,
        apiAccessible: false,
        error: error.message,
        timestamp: new Date().toISOString()
      }
    }
  }

  /**
   * Check if running in CI environment
   */
  static isCI(): boolean {
    return !!process.env.CI
  }

  /**
   * Get test timeout based on environment
   */
  static getTimeout(): number {
    return this.isCI() ? 60000 : 30000 // Longer timeout in CI
  }
}