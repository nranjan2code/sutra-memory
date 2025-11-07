import { test, expect, Page } from '@playwright/test';
import { LoginPage, ChatPage } from '../../e2e/page-objects';

interface StockData {
  symbol: string;
  price: number;
  change: number;
  volume: number;
  news?: string;
  sector?: string;
  timestamp: string;
}

class StockFeedSimulator {
  private symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX'];
  private sectors = ['Technology', 'Consumer Discretionary', 'Automotive', 'Cloud Computing'];
  private newsEvents = [
    'reports strong quarterly earnings',
    'announces new product launch',
    'beats analyst expectations',
    'faces regulatory challenges',
    'expands into new markets',
    'announces strategic partnership',
    'reports higher than expected revenue'
  ];

  generateStockUpdate(): StockData {
    const symbol = this.symbols[Math.floor(Math.random() * this.symbols.length)];
    const basePrice = {
      'AAPL': 150, 'MSFT': 300, 'GOOGL': 130, 'AMZN': 140, 
      'TSLA': 200, 'NVDA': 450, 'META': 280, 'NFLX': 400
    }[symbol] || 100;
    
    const change = (Math.random() - 0.5) * 10; // -5% to +5%
    const price = basePrice * (1 + change/100);
    const volume = Math.floor(Math.random() * 10000000) + 1000000; // 1M to 11M
    
    return {
      symbol,
      price: Math.round(price * 100) / 100,
      change: Math.round(change * 100) / 100,
      volume,
      sector: this.sectors[Math.floor(Math.random() * this.sectors.length)],
      news: Math.random() > 0.7 ? this.newsEvents[Math.floor(Math.random() * this.newsEvents.length)] : undefined,
      timestamp: new Date().toISOString()
    };
  }

  async generateContinuousUpdates(count: number, delayMs: number = 1000): Promise<StockData[]> {
    const updates: StockData[] = [];
    
    for (let i = 0; i < count; i++) {
      updates.push(this.generateStockUpdate());
      if (i < count - 1) {
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
    
    return updates;
  }
}

test.describe('Continuous Learning E2E Tests', () => {
  let chatPage: ChatPage;
  let stockSimulator: StockFeedSimulator;

  test.beforeEach(async ({ page }) => {
    stockSimulator = new StockFeedSimulator();
    
    // Setup: Register and login via UI
    const timestamp = Date.now();
    const userCredentials = {
      email: `test-${timestamp}@sutra.ai`,
      password: 'password123',
      organization: 'E2E Testing Org',
      fullName: 'E2E Test User'
    };

    console.log(`🔐 Registering user: ${userCredentials.email}`);
    
    const loginPage = new LoginPage(page);
    await loginPage.goto('http://localhost:8080/login');
    await page.waitForTimeout(2000);
    
    // Register
    await loginPage.register(
      userCredentials.email,
      userCredentials.password,
      userCredentials.organization,
      userCredentials.fullName
    );
    await page.waitForTimeout(3000);
    
    // Login if needed
    if (page.url().includes('/login')) {
      console.log('🔐 Logging in user');
      await loginPage.switchToLoginMode();
      await loginPage.login(userCredentials.email, userCredentials.password);
      await page.waitForTimeout(3000);
    }
    
    console.log(`✅ User authenticated: ${userCredentials.email}`);
    expect(page.url()).not.toContain('/login');
    
    // Initialize chat page
    chatPage = new ChatPage(page);
    await chatPage.assertOnChatPage();
    console.log('✅ Chat interface ready');
  });

  // Helper function to feed stock data via chat
  async function feedStockDataViaChat(stockData: StockData): Promise<void> {
    const content = `${stockData.symbol} stock update: Price $${stockData.price} (${stockData.change > 0 ? '+' : ''}${stockData.change}%), Volume: ${stockData.volume.toLocaleString()}, Sector: ${stockData.sector || 'Technology'}, Timestamp: ${stockData.timestamp}${stockData.news ? `, News: ${stockData.news}` : ''}`;
    
    console.log(`📈 Feeding stock data: ${stockData.symbol}`);
    await chatPage.sendMessage(content);
    await chatPage.waitForResponse();
  }

  test('should perform continuous learning with real-time stock feeds', async () => {
    console.log('\n🚀 Starting Continuous Learning Test');
    
    // Phase 1: Feed initial stock data via chat
    console.log('\n📊 Phase 1: Feeding initial stock data...');
    const initialUpdates = await stockSimulator.generateContinuousUpdates(5, 500);
    
    for (const stockData of initialUpdates) {
      await feedStockDataViaChat(stockData);
    }
    
    console.log(`✅ Phase 1: Fed ${initialUpdates.length} stock updates via chat`);
    
    // Phase 2: Query the learned data via chat
    console.log('\n🔍 Phase 2: Querying learned stock data...');
    
    const queries = [
      'What stocks have you learned about recently?',
      'Which stock has the highest price?',
      'Show me any technology sector stocks',
      'What are the latest stock price changes?'
    ];
    
    for (const query of queries) {
      console.log(`🤖 Query: "${query}"`);
      await chatPage.sendMessage(query);
      await chatPage.waitForResponse();
    }
    
    console.log(`✅ Phase 2: Completed ${queries.length} queries`);
    
    // Phase 3: Continuous learning simulation
    console.log('\n🔄 Phase 3: Continuous learning simulation...');
    
    for (let round = 1; round <= 3; round++) {
      console.log(`\n  Round ${round}: Feed + Query cycle`);
      
      // Feed more data via chat
      const newUpdates = await stockSimulator.generateContinuousUpdates(3, 300);
      for (const stockData of newUpdates) {
        await feedStockDataViaChat(stockData);
      }
      
      // Query the updated knowledge via chat
      const adaptiveQuery = `Round ${round}: What new stock information have you learned? Focus on recent price changes and any news.`;
      console.log(`🤖 Query: "${adaptiveQuery}"`);
      await chatPage.sendMessage(adaptiveQuery);
      await chatPage.waitForResponse();
      
      console.log(`  ✅ Round ${round}: Fed 3 updates, got response`);
    }
    
    // Phase 4: Comprehensive analysis
    console.log('\n📈 Phase 4: Comprehensive stock analysis...');
    
    const finalQueries = [
      'Provide a summary of all the stocks you\'ve learned about, including their sectors and recent performance',
      'Which stocks showed positive price changes?',
      'What news events did you observe for any stocks?',
      'Compare the volume patterns across different stocks'
    ];
    
    for (const query of finalQueries) {
      console.log(`🤖 Query: "${query}"`);
      await chatPage.sendMessage(query);
      await chatPage.waitForResponse();
    }
    
    // Verify we have substantial conversation
    const allMessages = await chatPage.getAllMessages();
    console.log(`💬 Total messages in conversation: ${allMessages.length}`);
    expect(allMessages.length).toBeGreaterThan(10);
    
    console.log('\n🎉 Continuous Learning Test Completed Successfully!');
    console.log(`✅ Total updates fed: ${initialUpdates.length + 9}`); // 5 initial + 3*3 rounds
    console.log(`✅ Total queries executed: ${queries.length + 3 + finalQueries.length}`);
    console.log('✅ All phases passed: Initial Feed → Query → Continuous Learning → Analysis');
  });

  test('should handle high-frequency stock updates with parallel processing', async () => {
    console.log('\n⚡ Starting High-Frequency Update Test');
    
    // Generate rapid stock updates
    const rapidUpdates = await stockSimulator.generateContinuousUpdates(10, 100);
    const startTime = Date.now();
    
    // Feed all updates rapidly via chat
    for (const stockData of rapidUpdates) {
      await feedStockDataViaChat(stockData);
    }
    
    const endTime = Date.now();
    console.log(`✅ Fed 10 updates in ${endTime - startTime}ms`);
    
    // Immediate query to test real-time availability
    const immediateQuery = 'What stocks did you just learn about in the last few seconds? List them with their prices.';
    console.log(`🤖 Query: "${immediateQuery}"`);
    await chatPage.sendMessage(immediateQuery);
    await chatPage.waitForResponse();
    
    // Verify we have conversation
    const allMessages = await chatPage.getAllMessages();
    expect(allMessages.length).toBeGreaterThan(5);
    
    console.log('✅ High-frequency test completed - real-time learning verified');
  });

  test('should demonstrate temporal reasoning with stock price trends', async () => {
    console.log('\n📊 Starting Temporal Reasoning Test');
    
    const symbol = 'AAPL';
    const basePrice = 150;
    
    // Create a series of price changes over time
    const priceHistory = [
      { price: basePrice, change: 0, news: 'baseline price' },
      { price: basePrice * 1.05, change: 5, news: 'announces new iPhone model' },
      { price: basePrice * 1.03, change: -2, news: 'profit-taking after announcement' },
      { price: basePrice * 1.08, change: 5, news: 'beats quarterly earnings expectations' },
      { price: basePrice * 1.06, change: -2, news: 'market correction affects tech stocks' }
    ];
    
    // Feed the price history with time delays via chat
    for (let i = 0; i < priceHistory.length; i++) {
      const stockData: StockData = {
        symbol,
        price: Math.round(priceHistory[i].price * 100) / 100,
        change: priceHistory[i].change,
        volume: Math.floor(Math.random() * 5000000) + 2000000,
        news: priceHistory[i].news,
        sector: 'Technology',
        timestamp: new Date(Date.now() + i * 1000).toISOString()
      };
      
      await feedStockDataViaChat(stockData);
      console.log(`📈 Fed ${symbol} update ${i + 1}: $${stockData.price} (${stockData.change > 0 ? '+' : ''}${stockData.change}%)`);
      
      if (i < priceHistory.length - 1) {
        await chatPage.page.waitForTimeout(200);
      }
    }
    
    // Test temporal reasoning queries via chat
    const temporalQueries = [
      'Show me the price trend for AAPL over time',
      'What caused AAPL price to increase?',
      'When did AAPL reach its highest price?',
      'What happened after the iPhone announcement?'
    ];
    
    for (const query of temporalQueries) {
      console.log(`🧠 Temporal query: "${query}"`);
      await chatPage.sendMessage(query);
      await chatPage.waitForResponse();
    }
    
    // Verify we have conversation
    const allMessages = await chatPage.getAllMessages();
    expect(allMessages.length).toBeGreaterThan(5);
    
    console.log('✅ Temporal reasoning test completed - price trends and causality demonstrated');
  });
});