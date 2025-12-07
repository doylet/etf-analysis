/**
 * Performance Validation Suite
 * Professional Design System - Performance Requirements Testing
 */

interface PerformanceMetrics {
  dataIdentificationTime: number
  interactionFrameRate: number
  componentRenderTime: number
  themeSwichingTime: number
  scrollPerformance: number
}

interface PerformanceResult {
  passed: boolean
  metrics: PerformanceMetrics
  issues: string[]
  recommendations: string[]
}

class PerformanceValidator {
  private observer: PerformanceObserver | null = null
  private metrics: PerformanceMetrics = {
    dataIdentificationTime: 0,
    interactionFrameRate: 0,
    componentRenderTime: 0,
    themeSwichingTime: 0,
    scrollPerformance: 0,
  }

  /**
   * Test if users can identify portfolio total value within 3 seconds
   */
  async testDataIdentificationTime(): Promise<number> {
    return new Promise((resolve) => {
      const startTime = performance.now()
      
      // Wait for MetricCard components to be visible and styled
      const checkVisibility = () => {
        const metricCards = document.querySelectorAll('[data-component="metric-card"], .metric-card')
        const portfolioValueCard = Array.from(metricCards).find(card => 
          card.textContent?.toLowerCase().includes('portfolio') ||
          card.textContent?.toLowerCase().includes('total') ||
          card.textContent?.toLowerCase().includes('value')
        )
        
        if (portfolioValueCard) {
          const computedStyle = window.getComputedStyle(portfolioValueCard as Element)
          const isVisible = computedStyle.opacity !== '0' && 
                           computedStyle.visibility !== 'hidden' &&
                           computedStyle.display !== 'none'
          
          if (isVisible) {
            const endTime = performance.now()
            const identificationTime = endTime - startTime
            resolve(identificationTime)
          } else {
            requestAnimationFrame(checkVisibility)
          }
        } else {
          requestAnimationFrame(checkVisibility)
        }
      }
      
      requestAnimationFrame(checkVisibility)
      
      // Timeout after 5 seconds
      setTimeout(() => {
        resolve(5000) // Failed requirement
      }, 5000)
    })
  }

  /**
   * Test interaction frame rate (should maintain 60fps)
   */
  async testInteractionFrameRate(): Promise<number> {
    return new Promise((resolve) => {
      const frameRates: number[] = []
      let lastTime = performance.now()
      let animationId: number
      
      const measureFrame = (currentTime: number) => {
        const delta = currentTime - lastTime
        const fps = 1000 / delta
        frameRates.push(fps)
        lastTime = currentTime
        
        if (frameRates.length < 60) { // Test for 1 second at 60fps
          animationId = requestAnimationFrame(measureFrame)
        } else {
          // Calculate average fps during interactions
          const averageFps = frameRates.reduce((a, b) => a + b, 0) / frameRates.length
          resolve(averageFps)
        }
      }
      
      // Trigger interactions during measurement
      const triggerInteractions = () => {
        const buttons = document.querySelectorAll('button')
        const cards = document.querySelectorAll('.metric-card, [data-component="metric-card"]')
        
        // Simulate hover events
        buttons.forEach((button, index) => {
          setTimeout(() => {
            button.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }))
            setTimeout(() => {
              button.dispatchEvent(new MouseEvent('mouseleave', { bubbles: true }))
            }, 100)
          }, index * 50)
        })
        
        cards.forEach((card, index) => {
          setTimeout(() => {
            card.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }))
            setTimeout(() => {
              card.dispatchEvent(new MouseEvent('mouseleave', { bubbles: true }))
            }, 100)
          }, index * 75)
        })
      }
      
      animationId = requestAnimationFrame(measureFrame)
      triggerInteractions()
      
      // Cleanup timeout
      setTimeout(() => {
        cancelAnimationFrame(animationId)
        resolve(0) // Failed if timeout
      }, 2000)
    })
  }

  /**
   * Test component render time
   */
  async testComponentRenderTime(): Promise<number> {
    const startTime = performance.now()
    
    // Create and render a MetricCard dynamically
    const container = document.createElement('div')
    container.style.position = 'absolute'
    container.style.top = '-9999px'
    document.body.appendChild(container)
    
    try {
      // Simulate React component creation
      const metricCard = document.createElement('div')
      metricCard.className = 'metric-card p-6 bg-white rounded-lg border shadow-sm'
      metricCard.innerHTML = `
        <div class="text-sm text-gray-600 mb-2">Portfolio Value</div>
        <div class="text-2xl font-bold tabular-nums">$1,234,567.89</div>
        <div class="text-green-600 flex items-center gap-1">
          <span>+$12,345.67</span>
          <span>(+1.2%)</span>
        </div>
      `
      
      container.appendChild(metricCard)
      
      // Force layout and styling
      metricCard.offsetHeight
      
      const endTime = performance.now()
      document.body.removeChild(container)
      
      return endTime - startTime
    } catch (error) {
      document.body.removeChild(container)
      return 1000 // Failed
    }
  }

  /**
   * Test theme switching performance
   */
  async testThemeSwitchingTime(): Promise<number> {
    const startTime = performance.now()
    
    // Simulate theme switch by toggling dark class
    const root = document.documentElement
    const originalClass = root.className
    
    root.classList.toggle('dark')
    
    // Wait for CSS transitions to complete
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const endTime = performance.now()
    
    // Restore original theme
    root.className = originalClass
    
    return endTime - startTime
  }

  /**
   * Test scroll performance with large datasets
   */
  async testScrollPerformance(): Promise<number> {
    return new Promise((resolve) => {
      const frameRates: number[] = []
      let lastTime = performance.now()
      let animationId: number
      
      const measureFrame = (currentTime: number) => {
        const delta = currentTime - lastTime
        const fps = 1000 / delta
        frameRates.push(fps)
        lastTime = currentTime
        
        if (frameRates.length < 30) { // Test for 0.5 seconds
          animationId = requestAnimationFrame(measureFrame)
        } else {
          const averageFps = frameRates.reduce((a, b) => a + b, 0) / frameRates.length
          resolve(averageFps)
        }
      }
      
      // Create scrollable content
      const scrollContainer = document.createElement('div')
      scrollContainer.style.cssText = `
        position: absolute;
        top: -9999px;
        width: 300px;
        height: 200px;
        overflow-y: scroll;
      `
      
      // Add many items to scroll through
      for (let i = 0; i < 100; i++) {
        const item = document.createElement('div')
        item.style.cssText = `
          height: 50px;
          padding: 10px;
          border-bottom: 1px solid #e5e7eb;
          background: ${i % 2 === 0 ? '#f9fafb' : '#ffffff'};
        `
        item.textContent = `Item ${i + 1} - Portfolio Data`
        scrollContainer.appendChild(item)
      }
      
      document.body.appendChild(scrollContainer)
      
      // Start measuring and trigger scrolling
      animationId = requestAnimationFrame(measureFrame)
      
      // Simulate smooth scrolling
      let scrollTop = 0
      const scrollStep = () => {
        scrollTop += 10
        scrollContainer.scrollTop = scrollTop
        
        if (scrollTop < scrollContainer.scrollHeight - scrollContainer.clientHeight) {
          setTimeout(scrollStep, 16) // ~60fps
        }
      }
      
      scrollStep()
      
      // Cleanup
      setTimeout(() => {
        cancelAnimationFrame(animationId)
        document.body.removeChild(scrollContainer)
        if (frameRates.length === 0) resolve(0)
      }, 1000)
    })
  }

  /**
   * Run comprehensive performance test suite
   */
  async validate(): Promise<PerformanceResult> {
    const issues: string[] = []
    const recommendations: string[] = []
    
    try {
      // Test data identification time (should be < 3000ms)
      this.metrics.dataIdentificationTime = await this.testDataIdentificationTime()
      if (this.metrics.dataIdentificationTime > 3000) {
        issues.push(`Data identification time: ${this.metrics.dataIdentificationTime.toFixed(0)}ms (should be < 3000ms)`)
        recommendations.push('Consider optimizing MetricCard component rendering or improve visual hierarchy')
      }
      
      // Test interaction frame rate (should be ≥ 60fps)
      this.metrics.interactionFrameRate = await this.testInteractionFrameRate()
      if (this.metrics.interactionFrameRate < 60) {
        issues.push(`Interaction frame rate: ${this.metrics.interactionFrameRate.toFixed(1)}fps (should be ≥ 60fps)`)
        recommendations.push('Optimize CSS animations and transitions, consider reducing animation complexity')
      }
      
      // Test component render time (should be < 100ms)
      this.metrics.componentRenderTime = await this.testComponentRenderTime()
      if (this.metrics.componentRenderTime > 100) {
        issues.push(`Component render time: ${this.metrics.componentRenderTime.toFixed(0)}ms (should be < 100ms)`)
        recommendations.push('Optimize component structure or consider memoization for complex components')
      }
      
      // Test theme switching (should be < 300ms)
      this.metrics.themeSwichingTime = await this.testThemeSwitchingTime()
      if (this.metrics.themeSwichingTime > 300) {
        issues.push(`Theme switching time: ${this.metrics.themeSwichingTime.toFixed(0)}ms (should be < 300ms)`)
        recommendations.push('Optimize CSS custom properties or reduce the number of themed elements')
      }
      
      // Test scroll performance (should be ≥ 55fps)
      this.metrics.scrollPerformance = await this.testScrollPerformance()
      if (this.metrics.scrollPerformance < 55) {
        issues.push(`Scroll performance: ${this.metrics.scrollPerformance.toFixed(1)}fps (should be ≥ 55fps)`)
        recommendations.push('Consider virtualization for large datasets or optimize scroll handlers')
      }
      
    } catch (error) {
      issues.push(`Performance testing error: ${error}`)
      recommendations.push('Check console for detailed error information')
    }
    
    const passed = issues.length === 0
    
    return {
      passed,
      metrics: this.metrics,
      issues,
      recommendations,
    }
  }

  /**
   * Generate performance report
   */
  generateReport(result: PerformanceResult): string {
    const { passed, metrics, issues, recommendations } = result
    
    return `
# Performance Validation Report

## Overall Status: ${passed ? '✅ PASSED' : '❌ FAILED'}

## Metrics

| Requirement | Target | Actual | Status |
|-------------|--------|--------|--------|
| Data Identification Time | < 3000ms | ${metrics.dataIdentificationTime.toFixed(0)}ms | ${metrics.dataIdentificationTime < 3000 ? '✅' : '❌'} |
| Interaction Frame Rate | ≥ 60fps | ${metrics.interactionFrameRate.toFixed(1)}fps | ${metrics.interactionFrameRate >= 60 ? '✅' : '❌'} |
| Component Render Time | < 100ms | ${metrics.componentRenderTime.toFixed(0)}ms | ${metrics.componentRenderTime < 100 ? '✅' : '❌'} |
| Theme Switching Time | < 300ms | ${metrics.themeSwichingTime.toFixed(0)}ms | ${metrics.themeSwichingTime < 300 ? '✅' : '❌'} |
| Scroll Performance | ≥ 55fps | ${metrics.scrollPerformance.toFixed(1)}fps | ${metrics.scrollPerformance >= 55 ? '✅' : '❌'} |

${issues.length > 0 ? `
## Issues Found

${issues.map(issue => `- ${issue}`).join('\n')}
` : ''}

${recommendations.length > 0 ? `
## Recommendations

${recommendations.map(rec => `- ${rec}`).join('\n')}
` : ''}

## Generated: ${new Date().toISOString()}
    `.trim()
  }
}

// Usage example
export async function runPerformanceValidation(): Promise<void> {
  console.log('🔄 Starting performance validation...')
  
  const validator = new PerformanceValidator()
  const result = await validator.validate()
  
  console.log('📊 Performance Validation Results:')
  console.log(validator.generateReport(result))
  
  if (result.passed) {
    console.log('✅ All performance requirements passed!')
  } else {
    console.warn('⚠️ Some performance requirements failed. See report above.')
  }
}

// Export for testing
export { PerformanceValidator }
export type { PerformanceMetrics, PerformanceResult }