import { Page, Locator, expect } from '@playwright/test'

export class SutraPageObject {
  readonly page: Page

  constructor(page: Page) {
    this.page = page
  }

  /**
   * Common page actions
   */
  async goto(path: string = '/') {
    await this.page.goto(path)
  }

  async waitForLoadingToFinish() {
    // Wait for any loading spinners to disappear
    await this.page.waitForSelector('[role="progressbar"]', { state: 'hidden', timeout: 10000 })
      .catch(() => {
        // It's okay if there's no loading spinner
      })
  }

  async waitForNetworkIdle() {
    await this.page.waitForLoadState('networkidle')
  }

  /**
   * Take a screenshot for debugging
   */
  async screenshot(name: string) {
    await this.page.screenshot({ path: `screenshots/${name}.png`, fullPage: true })
  }
}

export class LoginPage extends SutraPageObject {
  // Page elements
  readonly emailInput: Locator
  readonly passwordInput: Locator
  readonly organizationInput: Locator
  readonly fullNameInput: Locator
  readonly submitButton: Locator
  readonly toggleModeLink: Locator
  readonly errorAlert: Locator
  readonly sutraLogo: Locator

  constructor(page: Page) {
    super(page)
    this.emailInput = page.locator('input[type="email"]')
    this.passwordInput = page.locator('input[type="password"]')
    this.organizationInput = page.locator('input[autocomplete="organization"]')
    this.fullNameInput = page.locator('input[autocomplete="name"]')
    this.submitButton = page.locator('button[type="submit"]')
    this.toggleModeLink = page.locator('text=/Sign in here|Create an account/')
    this.errorAlert = page.locator('[role="alert"]')
    this.sutraLogo = page.locator('text="Sutra AI"')
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email)
    await this.passwordInput.fill(password)
    await this.submitButton.click()
    await this.waitForLoadingToFinish()
  }

  async register(email: string, password: string, organization: string, fullName?: string) {
    // Switch to registration mode if not already
    const submitButtonText = await this.submitButton.textContent()
    if (submitButtonText !== 'Create Account') {
      await this.toggleModeLink.click()
      await this.page.waitForSelector('input[autocomplete="organization"]')
    }

    await this.organizationInput.fill(organization)
    if (fullName) {
      await this.fullNameInput.fill(fullName)
    }
    await this.emailInput.fill(email)
    await this.passwordInput.fill(password)
    await this.submitButton.click()
    await this.waitForLoadingToFinish()
  }

  async switchToLoginMode() {
    const submitButtonText = await this.submitButton.textContent()
    if (submitButtonText !== 'Sign In') {
      await this.toggleModeLink.click()
      await this.page.waitForSelector('text="Sign In"')
    }
  }

  async switchToRegisterMode() {
    const submitButtonText = await this.submitButton.textContent()
    if (submitButtonText !== 'Create Account') {
      await this.toggleModeLink.click()
      await this.page.waitForSelector('input[autocomplete="organization"]')
    }
  }

  async getErrorMessage(): Promise<string | null> {
    if (await this.errorAlert.isVisible()) {
      return await this.errorAlert.textContent()
    }
    return null
  }

  async assertOnLoginPage() {
    await expect(this.sutraLogo).toBeVisible()
    await expect(this.emailInput).toBeVisible()
    await expect(this.passwordInput).toBeVisible()
    await expect(this.submitButton).toBeVisible()
  }
}

export class ChatPage extends SutraPageObject {
  // Page elements
  readonly messageInput: Locator
  readonly sendButton: Locator
  readonly messagesContainer: Locator
  readonly sampleQuestions: Locator
  readonly userMenu: Locator
  readonly logoutButton: Locator

  constructor(page: Page) {
    super(page)
    // Based on UI discovery - actual selectors from the working interface
    this.messageInput = page.locator('textarea[placeholder="Ask a question..."]')
    this.sendButton = page.locator('button[type="button"]:not(.Mui-disabled)').last() // Get enabled send button
    this.messagesContainer = page.locator('body') // Messages appear in the main body
    this.sampleQuestions = page.locator('button:has-text("Who is Alice?"), button:has-text("What does Bob like?"), button:has-text("Tell me about Python")')
    this.userMenu = page.locator('button:has-text("U")') // User menu button shows "U"
    this.logoutButton = page.locator('text=/logout|sign out/i')
  }

  async sendMessage(message: string) {
    await this.messageInput.fill(message)
    await this.page.waitForTimeout(500) // Brief pause for UI to update
    
    // Try keyboard shortcut first (common in chat interfaces)
    await this.messageInput.press('Enter')
    await this.page.waitForTimeout(1000)
    
    // If that doesn't work, try to find and click an enabled send button
    const enabledSendButtons = await this.page.locator('button:not(.Mui-disabled)').all()
    for (const button of enabledSendButtons) {
      const buttonText = await button.textContent()
      if (buttonText?.toLowerCase().includes('send') || await button.locator('svg').count() > 0) {
        await button.click()
        break
      }
    }
    
    await this.waitForLoadingToFinish()
  }

  async waitForResponse() {
    // Wait for a response to appear (new content in the page)
    await this.page.waitForTimeout(2000) // Give some time for the response to start
    await this.waitForLoadingToFinish()
  }

  async getLastMessage(): Promise<string> {
    // Look for response content in the page
    const responseElements = await this.page.locator('div, p, span').filter({ hasText: /\w+/ }).all()
    if (responseElements.length === 0) {
      return ''
    }
    
    // Get the last meaningful text element
    const lastElement = responseElements[responseElements.length - 1]
    return await lastElement.textContent() || ''
  }

  async getAllMessages(): Promise<string[]> {
    // Get all text content that looks like messages/responses
    const textElements = await this.page.locator('div, p, span').filter({ hasText: /\w{3,}/ }).all()
    const messages = []
    
    for (const element of textElements) {
      const text = await element.textContent()
      if (text && text.trim().length > 5) { // Filter out very short text
        messages.push(text.trim())
      }
    }
    
    return messages
  }

  async assertOnChatPage() {
    await expect(this.messageInput).toBeVisible()
    // Check for either sample questions or the message input being available
    const sampleQuestionsVisible = await this.sampleQuestions.count() > 0
    const messageInputVisible = await this.messageInput.isVisible()
    expect(sampleQuestionsVisible || messageInputVisible).toBeTruthy()
  }
}

export class HomePage extends SutraPageObject {
  // Page elements for the legacy home page
  readonly learnTextArea: Locator
  readonly learnButton: Locator
  readonly queryInput: Locator
  readonly queryButton: Locator
  readonly metricsSection: Locator
  readonly clearButton: Locator

  constructor(page: Page) {
    super(page)
    this.learnTextArea = page.locator('textarea[placeholder*="learn"], textarea[placeholder*="knowledge"]').first()
    this.learnButton = page.locator('button', { hasText: /learn|add/i }).first()
    this.queryInput = page.locator('input[placeholder*="query"], input[placeholder*="question"]').first()
    this.queryButton = page.locator('button', { hasText: /query|ask/i }).first()
    this.metricsSection = page.locator('[data-testid="metrics"], .metrics').first()
    this.clearButton = page.locator('button', { hasText: /clear|reset/i }).first()
  }

  async learnFact(text: string) {
    await this.learnTextArea.fill(text)
    await this.learnButton.click()
    await this.waitForLoadingToFinish()
  }

  async queryKnowledge(query: string) {
    await this.queryInput.fill(query)
    await this.queryButton.click()
    await this.waitForLoadingToFinish()
  }

  async assertOnHomePage() {
    // The home page might redirect to chat, so we'll be flexible
    const isOnHome = await this.learnTextArea.isVisible({ timeout: 2000 }).catch(() => false)
    const isOnChat = await this.page.locator('textarea[placeholder*="message"]').isVisible({ timeout: 2000 }).catch(() => false)
    
    if (!isOnHome && !isOnChat) {
      throw new Error('Not on home page or chat page')
    }
  }
}

/**
 * Test utilities for common operations
 */
export class TestUtils {
  static generateRandomEmail(): string {
    const timestamp = Date.now()
    const random = Math.random().toString(36).substring(7)
    return `test_${timestamp}_${random}@example.com`
  }

  static generateRandomOrganization(): string {
    const timestamp = Date.now()
    const random = Math.random().toString(36).substring(7)
    return `Test Org ${random} ${timestamp}`
  }

  static generateRandomPassword(): string {
    const length = 12
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
    let password = ''
    for (let i = 0; i < length; i++) {
      password += charset.charAt(Math.floor(Math.random() * charset.length))
    }
    return password
  }

  static async clearLocalStorage(page: Page) {
    try {
      await page.evaluate(() => localStorage.clear())
    } catch (error) {
      // Ignore security errors - some browsers restrict localStorage access
      console.log('localStorage.clear() not available, skipping')
    }
  }

  static async clearSessionStorage(page: Page) {
    try {
      await page.evaluate(() => sessionStorage.clear())
    } catch (error) {
      // Ignore security errors - some browsers restrict sessionStorage access
      console.log('sessionStorage.clear() not available, skipping')
    }
  }

  static async clearAllStorage(page: Page) {
    await this.clearLocalStorage(page)
    await this.clearSessionStorage(page)
    
    // Also clear cookies as an alternative
    try {
      await page.context().clearCookies()
    } catch (error) {
      console.log('Cookie clearing not available, skipping')
    }
  }
}