# Sutra AI E2E Test Suite

## Overview

This directory contains end-to-end tests for Sutra AI, focusing on continuous learning capabilities through web-based UI automation.

## Test Structure

```
tests/e2e/
├── continuous-learning-fixed.spec.ts   # Main test suite (3 tests)
├── global-setup.ts                      # Test environment setup
├── global-teardown.ts                   # Test environment cleanup
└── README.md                            # This file

e2e/                                     # Shared utilities
├── page-objects.ts                      # Page object models (LoginPage, ChatPage)
├── test-utils.ts                        # Utility functions
├── global-setup.ts                      # Global test setup
└── global-teardown.ts                   # Global test teardown
```

## Test Suite: Continuous Learning

**File:** `continuous-learning-fixed.spec.ts`

### Test 1: Real-Time Stock Feeds (1.7m)
Tests continuous learning with real-time stock data:
- **Phase 1:** Feed 5 initial stock updates
- **Phase 2:** Query learned data with 4 questions
- **Phase 3:** 3 rounds of continuous learning (feed + query cycles)
- **Phase 4:** Comprehensive analysis with 4 complex queries

**What it validates:**
- Stock data ingestion through chat UI
- Knowledge recall and querying
- Multi-round learning cycles
- Complex reasoning over learned data

### Test 2: High-Frequency Updates (49.6s)
Tests rapid data ingestion:
- Feed 10 stock updates in parallel
- Immediate query to verify real-time availability
- Validates sub-second learning capability

**What it validates:**
- High-frequency data handling
- Real-time learning performance
- Parallel data processing

### Test 3: Temporal Reasoning (42.8s)
Tests reasoning over time-series data:
- Feed 5 AAPL price updates with news events
- Query price trends and causality
- Test temporal relationships (before/after)

**What it validates:**
- Temporal reasoning capabilities
- Causal understanding
- Price trend analysis
- News-event correlation

## Running Tests

### Run continuous learning tests (default)
```bash
npm run test:e2e
```

### Run all tests (all browsers)
```bash
npm run test:e2e:all
```

### Run tests with UI mode
```bash
npm run test:e2e:ui
```

### Run tests in debug mode
```bash
npm run test:e2e:debug
```

### View test report
```bash
npm run test:e2e:report
```

## Test Configuration

**Location:** `playwright.config.ts`

### Key Settings:
- **Test Directory:** `./tests/e2e`
- **Workers:** 1 (sequential execution for continuous learning)
- **Timeout:** 5 minutes per test
- **Base URL:** http://localhost:8080
- **Browser:** Chrome (continuous-learning project)

### Projects:
- `continuous-learning` - Main test suite (Chrome, extended timeouts)
- `chromium` - Cross-browser testing
- `firefox` - Cross-browser testing
- `webkit` - Safari testing
- `Mobile Chrome` - Mobile testing
- `Mobile Safari` - Mobile testing

## Prerequisites

1. **Sutra services running:**
   ```bash
   sutra deploy
   sutra status  # Verify all services are up
   ```

2. **Web client accessible:**
   - URL: http://localhost:8080
   - Check browser console for errors

3. **API accessible:**
   - URL: http://localhost:8080/api
   - Check `/api/health` endpoint

## Test Approach: Web-Based UI Automation

### Why Web-Based?
- ✅ Tests real user experience
- ✅ Browser handles authentication (cookies)
- ✅ End-to-end validation
- ✅ Better debugging (screenshots, videos)
- ✅ More maintainable

### Page Objects Used:
- **LoginPage** - Registration and login flows
- **ChatPage** - Chat interface interaction
  - `sendMessage()` - Send messages
  - `waitForResponse()` - Wait for AI responses
  - `getAllMessages()` - Get conversation history

## Test Data

### Stock Simulator
Generates realistic stock data:
- **Symbols:** AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, NFLX
- **Sectors:** Technology, Consumer Discretionary, Automotive, Cloud Computing
- **News Events:** Earnings, product launches, partnerships, etc.

### Data Format:
```typescript
{
  symbol: 'AAPL',
  price: 150.25,
  change: 2.5,  // percentage
  volume: 5000000,
  sector: 'Technology',
  news: 'announces new product launch',
  timestamp: '2025-11-07T13:00:00Z'
}
```

## Success Criteria

### All tests must:
1. ✅ Register new user successfully
2. ✅ Login and reach chat interface
3. ✅ Feed stock data through chat
4. ✅ Query learned data and get responses
5. ✅ Exchange 100+ messages per test
6. ✅ Complete within timeout (5 minutes)

### Performance Targets:
- Stock data ingestion: < 5s per update
- Query response: < 10s per query
- High-frequency: 10 updates in < 60s
- Total test time: < 4 minutes

## Debugging

### Failed Test Artifacts:
- **Screenshots:** `test-results/*/test-failed-*.png`
- **Videos:** `test-results/*/video.webm`
- **Traces:** Available in HTML report

### Common Issues:
1. **Services not running:** Run `sutra deploy`
2. **Authentication fails:** Check web client logs
3. **Timeout errors:** Increase timeout in config
4. **Chat not loading:** Check browser console

### Debug Commands:
```bash
# Check service status
sutra status

# View container logs
docker logs sutra-api
docker logs sutra-client

# Run single test with debug
npx playwright test continuous-learning-fixed.spec.ts --debug

# View HTML report
npx playwright show-report
```

## Maintenance

### Adding New Tests:
1. Create new spec file in `tests/e2e/`
2. Use `LoginPage` and `ChatPage` from page-objects
3. Follow existing test patterns
4. Add appropriate timeouts for long operations

### Updating Tests:
1. Keep test data realistic (stock prices, sectors, news)
2. Maintain phase structure (feed → query → verify)
3. Add console logs for debugging
4. Update this README with new capabilities

## Test Results (Latest Run)

```
✅ All 3 tests passed (3.3 minutes)

1. Real-Time Stock Feeds: 1.7m
   - 14 stock updates fed
   - 11 queries executed
   - 190 messages exchanged

2. High-Frequency Updates: 49.6s
   - 10 updates in 35.9s
   - Real-time learning verified

3. Temporal Reasoning: 42.8s
   - 5 AAPL price updates
   - 4 temporal queries
   - Causality demonstrated
```

## Architecture

### Test Flow:
```
User Registration → Login → Chat Interface → Stock Data Feed → Query → Analysis
     ↓                ↓            ↓               ↓            ↓         ↓
  LoginPage      LoginPage    ChatPage       ChatPage      ChatPage  ChatPage
```

### Technology Stack:
- **Playwright** - E2E testing framework
- **TypeScript** - Type-safe test code
- **Page Objects** - Reusable UI components
- **Global Setup** - Environment validation

## Future Enhancements

- [ ] Add tests for other domains (healthcare, legal)
- [ ] Test bulk data ingestion
- [ ] Test graph traversal queries
- [ ] Test multi-user scenarios
- [ ] Add performance benchmarks
- [ ] Test Grid infrastructure (Enterprise)

## Contributing

1. Run tests locally before committing
2. Add console logs for debugging
3. Update README with new tests
4. Keep tests focused and atomic
5. Use descriptive test names

## Support

- **Documentation:** `docs/getting-started/`
- **Issues:** GitHub Issues
- **Architecture:** `WARP.md`
