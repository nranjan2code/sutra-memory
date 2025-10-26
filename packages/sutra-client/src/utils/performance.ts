/**
 * Performance Monitoring Utilities
 * 
 * Tracks Core Web Vitals and custom performance metrics.
 */

import { onCLS, onINP, onFCP, onLCP, onTTFB, Metric } from 'web-vitals'

/**
 * Report performance metrics to console (development) or analytics (production)
 */
function sendToAnalytics(metric: Metric) {
  // In development, log to console
  if (typeof window !== 'undefined') {
    console.log('[Performance]', {
      name: metric.name,
      value: metric.value,
      rating: metric.rating,
      delta: metric.delta,
    })
  }

  // In production, you would send to your analytics service
  // Example: analytics.track('web-vital', { ...metric })
}

/**
 * Initialize performance monitoring
 * Call this once when the app starts
 */
export function initPerformanceMonitoring() {
  // Track Core Web Vitals
  onCLS(sendToAnalytics)  // Cumulative Layout Shift
  onINP(sendToAnalytics)  // Interaction to Next Paint (replaces FID)
  onFCP(sendToAnalytics)  // First Contentful Paint
  onLCP(sendToAnalytics)  // Largest Contentful Paint
  onTTFB(sendToAnalytics) // Time to First Byte
}

/**
 * Measure custom performance metrics
 */
export function measurePerformance(label: string, fn: () => void) {
  const start = performance.now()
  fn()
  const end = performance.now()
  const duration = end - start

  console.log(`[Performance] ${label}: ${duration.toFixed(2)}ms`)

  return duration
}

/**
 * Mark performance timing
 */
export function markPerformance(name: string) {
  performance.mark(name)
}

/**
 * Measure performance between two marks
 */
export function measureBetweenMarks(name: string, startMark: string, endMark: string) {
  try {
    performance.measure(name, startMark, endMark)
    const measure = performance.getEntriesByName(name)[0]
    
    console.log(`[Performance] ${name}: ${measure.duration.toFixed(2)}ms`)
    
    return measure.duration
  } catch (error) {
    console.error('Performance measurement failed:', error)
    return 0
  }
}
