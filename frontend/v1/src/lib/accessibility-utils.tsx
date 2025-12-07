/**
 * Accessibility Testing Utilities
 * Professional Design System - WCAG AA Compliance Helpers
 */

import React from 'react'

// Color contrast ratio calculation
export function getContrastRatio(color1: string, color2: string): number {
  const getLuminance = (color: string): number => {
    // Convert hex to RGB
    const hex = color.replace('#', '')
    const r = parseInt(hex.substr(0, 2), 16) / 255
    const g = parseInt(hex.substr(2, 2), 16) / 255
    const b = parseInt(hex.substr(4, 2), 16) / 255
    
    // Apply gamma correction
    const toLinear = (c: number) => 
      c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
    
    const rLinear = toLinear(r)
    const gLinear = toLinear(g)
    const bLinear = toLinear(b)
    
    // Calculate luminance
    return 0.2126 * rLinear + 0.7152 * gLinear + 0.0722 * bLinear
  }
  
  const lum1 = getLuminance(color1)
  const lum2 = getLuminance(color2)
  
  const brightest = Math.max(lum1, lum2)
  const darkest = Math.min(lum1, lum2)
  
  return (brightest + 0.05) / (darkest + 0.05)
}

// WCAG compliance checker
export interface WCAGResult {
  level: 'AA' | 'AAA' | 'FAIL'
  ratio: number
  isLargeText: boolean
  passes: boolean
}

export function checkWCAGCompliance(
  foreground: string, 
  background: string, 
  isLargeText: boolean = false
): WCAGResult {
  const ratio = getContrastRatio(foreground, background)
  
  const aaThreshold = isLargeText ? 3 : 4.5
  const aaaThreshold = isLargeText ? 4.5 : 7
  
  let level: WCAGResult['level']
  if (ratio >= aaaThreshold) {
    level = 'AAA'
  } else if (ratio >= aaThreshold) {
    level = 'AA'
  } else {
    level = 'FAIL'
  }
  
  return {
    level,
    ratio,
    isLargeText,
    passes: level !== 'FAIL',
  }
}

// Accessibility testing hook
export function useAccessibilityTest() {
  const testColorContrast = React.useCallback((
    element: HTMLElement
  ): WCAGResult | null => {
    const computedStyle = window.getComputedStyle(element)
    const color = computedStyle.color
    const backgroundColor = computedStyle.backgroundColor
    
    // Convert RGB to hex (simplified)
    const rgbToHex = (rgb: string): string => {
      const match = rgb.match(/\d+/g)
      if (!match) return '#000000'
      
      const r = parseInt(match[0]).toString(16).padStart(2, '0')
      const g = parseInt(match[1]).toString(16).padStart(2, '0')
      const b = parseInt(match[2]).toString(16).padStart(2, '0')
      
      return `#${r}${g}${b}`
    }
    
    try {
      const fgHex = rgbToHex(color)
      const bgHex = rgbToHex(backgroundColor)
      
      const fontSize = parseFloat(computedStyle.fontSize)
      const fontWeight = computedStyle.fontWeight
      
      const isLargeText = fontSize >= 18 || (fontSize >= 14 && fontWeight === 'bold')
      
      return checkWCAGCompliance(fgHex, bgHex, isLargeText)
    } catch (error) {
      console.error('Error testing color contrast:', error)
      return null
    }
  }, [])
  
  const testKeyboardNavigation = React.useCallback((): boolean => {
    // Check if all interactive elements are keyboard accessible
    const interactiveElements = document.querySelectorAll(
      'button, a, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    
    let allAccessible = true
    
    interactiveElements.forEach((element) => {
      const tabIndex = element.getAttribute('tabindex')
      const isNegativeTabIndex = tabIndex === '-1'
      const isDisabled = (element as HTMLInputElement).disabled
      
      if (!isDisabled && !isNegativeTabIndex) {
        // Check if element can receive focus
        try {
          (element as HTMLElement).focus()
          if (document.activeElement !== element) {
            allAccessible = false
          }
        } catch (error) {
          allAccessible = false
        }
      }
    })
    
    return allAccessible
  }, [])
  
  const testAriaLabels = React.useCallback((): Array<{ element: Element; issue: string }> => {
    const issues: Array<{ element: Element; issue: string }> = []
    
    // Check buttons without accessible text
    const buttons = document.querySelectorAll('button')
    buttons.forEach((button) => {
      const hasText = button.textContent?.trim()
      const hasAriaLabel = button.getAttribute('aria-label')
      const hasAriaLabelledBy = button.getAttribute('aria-labelledby')
      
      if (!hasText && !hasAriaLabel && !hasAriaLabelledBy) {
        issues.push({
          element: button,
          issue: 'Button lacks accessible text (textContent, aria-label, or aria-labelledby)',
        })
      }
    })
    
    // Check images without alt text
    const images = document.querySelectorAll('img')
    images.forEach((img) => {
      const hasAlt = img.getAttribute('alt') !== null
      const isDecorative = img.getAttribute('role') === 'presentation' || img.getAttribute('alt') === ''
      
      if (!hasAlt && !isDecorative) {
        issues.push({
          element: img,
          issue: 'Image lacks alt attribute',
        })
      }
    })
    
    // Check form inputs without labels
    const inputs = document.querySelectorAll('input, select, textarea')
    inputs.forEach((input) => {
      const hasLabel = document.querySelector(`label[for="${input.id}"]`)
      const hasAriaLabel = input.getAttribute('aria-label')
      const hasAriaLabelledBy = input.getAttribute('aria-labelledby')
      
      if (!hasLabel && !hasAriaLabel && !hasAriaLabelledBy && input.id) {
        issues.push({
          element: input,
          issue: 'Form control lacks associated label',
        })
      }
    })
    
    return issues
  }, [])
  
  return {
    testColorContrast,
    testKeyboardNavigation,
    testAriaLabels,
  }
}

// Component for testing accessibility in development
export interface AccessibilityTestPanelProps {
  targetElement?: HTMLElement | null
}

export const AccessibilityTestPanel: React.FC<AccessibilityTestPanelProps> = ({ 
  targetElement 
}) => {
  const [results, setResults] = React.useState<{
    contrast: WCAGResult | null
    keyboard: boolean | null
    ariaIssues: Array<{ element: Element; issue: string }>
  }>({
    contrast: null,
    keyboard: null,
    ariaIssues: [],
  })
  
  const { testColorContrast, testKeyboardNavigation, testAriaLabels } = useAccessibilityTest()
  
  const runTests = React.useCallback(() => {
    const newResults = {
      contrast: targetElement ? testColorContrast(targetElement) : null,
      keyboard: testKeyboardNavigation(),
      ariaIssues: testAriaLabels(),
    }
    
    setResults(newResults)
  }, [targetElement, testColorContrast, testKeyboardNavigation, testAriaLabels])
  
  React.useEffect(() => {
    runTests()
  }, [runTests])
  
  return (
    <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Accessibility Test Results</h3>
      
      <div className="space-y-4">
        {/* Color Contrast Results */}
        {results.contrast && (
          <div className="p-3 bg-gray-50 rounded-md">
            <h4 className="font-medium mb-2">Color Contrast</h4>
            <div className="flex items-center gap-2">
              <span className={`
                px-2 py-1 rounded text-sm font-medium
                ${results.contrast.level === 'AAA' ? 'bg-green-100 text-green-800' : 
                  results.contrast.level === 'AA' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }
              `}>
                {results.contrast.level}
              </span>
              <span className="text-sm tabular-nums">
                Ratio: {results.contrast.ratio.toFixed(2)}:1
              </span>
              {results.contrast.isLargeText && (
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                  Large Text
                </span>
              )}
            </div>
          </div>
        )}
        
        {/* Keyboard Navigation Results */}
        <div className="p-3 bg-gray-50 rounded-md">
          <h4 className="font-medium mb-2">Keyboard Navigation</h4>
          <div className="flex items-center gap-2">
            <span className={`
              px-2 py-1 rounded text-sm font-medium
              ${results.keyboard ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}
            `}>
              {results.keyboard ? 'PASS' : 'FAIL'}
            </span>
            <span className="text-sm">
              {results.keyboard ? 
                'All interactive elements are keyboard accessible' : 
                'Some elements may not be keyboard accessible'
              }
            </span>
          </div>
        </div>
        
        {/* ARIA Issues */}
        <div className="p-3 bg-gray-50 rounded-md">
          <h4 className="font-medium mb-2">ARIA & Semantic Issues</h4>
          {results.ariaIssues.length === 0 ? (
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 rounded text-sm font-medium bg-green-100 text-green-800">
                PASS
              </span>
              <span className="text-sm">No accessibility issues found</span>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2 py-1 rounded text-sm font-medium bg-red-100 text-red-800">
                  {results.ariaIssues.length} ISSUE{results.ariaIssues.length > 1 ? 'S' : ''}
                </span>
              </div>
              <ul className="space-y-1">
                {results.ariaIssues.map((issue, index) => (
                  <li key={index} className="text-sm text-red-700 bg-red-50 p-2 rounded">
                    {issue.issue}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
      
      <button
        onClick={runTests}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
      >
        Re-run Tests
      </button>
    </div>
  )
}

// Hook to validate financial component accessibility
export function useFinancialAccessibility() {
  const validateMetricCard = React.useCallback((element: HTMLElement): string[] => {
    const issues: string[] = []
    
    // Check for proper tabular numerics
    const numerics = element.querySelectorAll('[class*="tabular"]')
    if (numerics.length === 0) {
      issues.push('Financial numbers should use tabular-nums for alignment')
    }
    
    // Check color-only information
    const percentageElements = element.querySelectorAll('[class*="text-green"], [class*="text-red"]')
    percentageElements.forEach((el) => {
      const hasIcon = el.querySelector('svg, .icon')
      const hasTextIndicator = el.textContent?.includes('+') || el.textContent?.includes('-')
      
      if (!hasIcon && !hasTextIndicator) {
        issues.push('Color-only indicators should include text or icons for accessibility')
      }
    })
    
    return issues
  }, [])
  
  return {
    validateMetricCard,
  }
}

// Performance and accessibility audit utilities
export class A11yAuditor {
  static async auditPage(): Promise<{
    score: number
    issues: Array<{ type: string; description: string; severity: 'high' | 'medium' | 'low' }>
    performance: {
      tabNavigation: number
      focusVisibility: boolean
    }
  }> {
    const issues: Array<{ type: string; description: string; severity: 'high' | 'medium' | 'low' }> = []
    
    // Check focus indicators
    const focusStyles = window.getComputedStyle(document.documentElement).getPropertyValue('--ring')
    if (!focusStyles) {
      issues.push({
        type: 'focus',
        description: 'Missing focus ring styles',
        severity: 'high',
      })
    }
    
    // Check reduced motion support
    const hasReducedMotionSupport = document.querySelector('[data-reduce-motion], .reduce-motion')
    if (!hasReducedMotionSupport) {
      issues.push({
        type: 'motion',
        description: 'No reduced motion preferences detected',
        severity: 'medium',
      })
    }
    
    // Performance test - tab navigation speed
    const startTime = performance.now()
    const focusableElements = document.querySelectorAll(
      'button, a, input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    
    let tabTime = 0
    try {
      focusableElements.forEach((element, index) => {
        if (index < 5) { // Test first 5 elements
          const elementStartTime = performance.now()
          ;(element as HTMLElement).focus()
          tabTime += performance.now() - elementStartTime
        }
      })
    } catch (error) {
      console.warn('Tab navigation test error:', error)
    }
    
    const avgTabTime = tabTime / Math.min(5, focusableElements.length)
    
    // Calculate overall score
    const maxIssues = 10
    const issueScore = Math.max(0, (maxIssues - issues.length) / maxIssues)
    const performanceScore = avgTabTime < 16 ? 1 : Math.max(0, 1 - (avgTabTime - 16) / 100)
    const score = Math.round((issueScore + performanceScore) / 2 * 100)
    
    return {
      score,
      issues,
      performance: {
        tabNavigation: avgTabTime,
        focusVisibility: !!focusStyles,
      },
    }
  }
}

export default {
  getContrastRatio,
  checkWCAGCompliance,
  useAccessibilityTest,
  useFinancialAccessibility,
  AccessibilityTestPanel,
  A11yAuditor,
}