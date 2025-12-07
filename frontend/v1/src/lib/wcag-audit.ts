/**
 * WCAG AA Compliance Audit Suite
 * Professional Design System - Comprehensive Accessibility Testing
 */

import { getContrastRatio, checkWCAGCompliance } from './accessibility-utils'

interface ComponentAuditResult {
  component: string
  passes: boolean
  issues: Array<{
    rule: string
    severity: 'error' | 'warning' | 'info'
    description: string
    element?: string
  }>
  score: number
}

interface ComplianceReport {
  overallCompliance: boolean
  overallScore: number
  componentResults: ComponentAuditResult[]
  summary: {
    totalComponents: number
    passingComponents: number
    totalIssues: number
    criticalIssues: number
  }
  recommendations: string[]
}

class WCAGAuditor {
  private issues: Array<{
    component: string
    rule: string
    severity: 'error' | 'warning' | 'info'
    description: string
    element?: string
  }> = []

  /**
   * Audit MetricCard component compliance
   */
  auditMetricCard(): ComponentAuditResult {
    const componentIssues: ComponentAuditResult['issues'] = []
    
    const metricCards = document.querySelectorAll('.metric-card, [data-component="metric-card"]')
    
    metricCards.forEach((card, index) => {
      const cardElement = card as HTMLElement
      
      // Check color contrast
      const computedStyle = window.getComputedStyle(cardElement)
      const color = computedStyle.color
      const backgroundColor = computedStyle.backgroundColor
      
      try {
        const colorHex = this.rgbToHex(color)
        const bgHex = this.rgbToHex(backgroundColor)
        const contrastResult = checkWCAGCompliance(colorHex, bgHex, false)
        
        if (!contrastResult.passes) {
          componentIssues.push({
            rule: 'WCAG 1.4.3 Contrast (Minimum)',
            severity: 'error',
            description: `Insufficient color contrast ratio: ${contrastResult.ratio.toFixed(2)}:1`,
            element: `MetricCard #${index + 1}`,
          })
        }
      } catch (error) {
        componentIssues.push({
          rule: 'WCAG 1.4.3 Contrast (Minimum)',
          severity: 'warning',
          description: 'Could not determine color contrast',
          element: `MetricCard #${index + 1}`,
        })
      }
      
      // Check for tabular numerals on financial data
      const valueElements = cardElement.querySelectorAll('[class*="text-"], .metric-value, .financial-amount')
      valueElements.forEach((valueEl) => {
        const hasTabularNums = valueEl.classList.contains('tabular-nums') || 
                              valueEl.classList.contains('font-tabular') ||
                              window.getComputedStyle(valueEl).fontVariantNumeric.includes('tabular')
        
        if (!hasTabularNums && this.containsNumbers(valueEl.textContent || '')) {
          componentIssues.push({
            rule: 'Custom: Financial Data Alignment',
            severity: 'warning',
            description: 'Financial numbers should use tabular numerals for proper alignment',
            element: `Value element in MetricCard #${index + 1}`,
          })
        }
      })
      
      // Check for semantic color coding
      const percentageElements = cardElement.querySelectorAll('.text-green-600, .text-red-600, .text-green-500, .text-red-500')
      percentageElements.forEach((el) => {
        const hasIcon = el.querySelector('svg, .icon')
        const hasTextIndicator = (el.textContent || '').includes('+') || (el.textContent || '').includes('-')
        
        if (!hasIcon && !hasTextIndicator) {
          componentIssues.push({
            rule: 'WCAG 1.4.1 Use of Color',
            severity: 'error',
            description: 'Color is used as the only visual means of conveying information',
            element: `Percentage element in MetricCard #${index + 1}`,
          })
        }
      })
      
      // Check for accessible hover states
      const isHoverable = cardElement.matches(':hover, [data-hover], .hover\\:scale-\\[1\\.02\\]')
      if (isHoverable) {
        const hasFocusIndicator = window.getComputedStyle(cardElement, ':focus').outline !== 'none' ||
                                 window.getComputedStyle(cardElement, ':focus').boxShadow.includes('ring')
        
        if (!hasFocusIndicator) {
          componentIssues.push({
            rule: 'WCAG 2.4.7 Focus Visible',
            severity: 'error',
            description: 'Interactive element lacks visible focus indicator',
            element: `MetricCard #${index + 1}`,
          })
        }
      }
    })
    
    const passes = componentIssues.filter(issue => issue.severity === 'error').length === 0
    const score = Math.max(0, 100 - (componentIssues.length * 10))
    
    return {
      component: 'MetricCard',
      passes,
      issues: componentIssues,
      score,
    }
  }

  /**
   * Audit Button component compliance
   */
  auditButtons(): ComponentAuditResult {
    const componentIssues: ComponentAuditResult['issues'] = []
    
    const buttons = document.querySelectorAll('button')
    
    buttons.forEach((button, index) => {
      // Check minimum size (44x44px for touch targets)
      const rect = button.getBoundingClientRect()
      if (rect.width < 44 || rect.height < 44) {
        componentIssues.push({
          rule: 'WCAG 2.5.5 Target Size (Level AAA)',
          severity: 'warning',
          description: `Touch target too small: ${rect.width.toFixed(0)}x${rect.height.toFixed(0)}px (should be ≥44x44px)`,
          element: `Button #${index + 1}`,
        })
      }
      
      // Check accessible text
      const hasText = button.textContent?.trim()
      const hasAriaLabel = button.getAttribute('aria-label')
      const hasAriaLabelledBy = button.getAttribute('aria-labelledby')
      
      if (!hasText && !hasAriaLabel && !hasAriaLabelledBy) {
        componentIssues.push({
          rule: 'WCAG 4.1.2 Name, Role, Value',
          severity: 'error',
          description: 'Button lacks accessible name',
          element: `Button #${index + 1}`,
        })
      }
      
      // Check color contrast
      try {
        const computedStyle = window.getComputedStyle(button)
        const colorHex = this.rgbToHex(computedStyle.color)
        const bgHex = this.rgbToHex(computedStyle.backgroundColor)
        const contrastResult = checkWCAGCompliance(colorHex, bgHex, false)
        
        if (!contrastResult.passes) {
          componentIssues.push({
            rule: 'WCAG 1.4.3 Contrast (Minimum)',
            severity: 'error',
            description: `Insufficient color contrast: ${contrastResult.ratio.toFixed(2)}:1`,
            element: `Button #${index + 1}`,
          })
        }
      } catch (error) {
        // Skip contrast check if colors can't be determined
      }
      
      // Check focus indicator
      const normalStyle = window.getComputedStyle(button)
      button.focus()
      const focusStyle = window.getComputedStyle(button)
      const hasVisibleFocus = focusStyle.outline !== 'none' || 
                             focusStyle.boxShadow.includes('ring') ||
                             focusStyle.borderColor !== normalStyle.borderColor
      
      if (!hasVisibleFocus) {
        componentIssues.push({
          rule: 'WCAG 2.4.7 Focus Visible',
          severity: 'error',
          description: 'Button lacks visible focus indicator',
          element: `Button #${index + 1}`,
        })
      }
    })
    
    const passes = componentIssues.filter(issue => issue.severity === 'error').length === 0
    const score = Math.max(0, 100 - (componentIssues.length * 10))
    
    return {
      component: 'Button',
      passes,
      issues: componentIssues,
      score,
    }
  }

  /**
   * Audit DataTable component compliance
   */
  auditDataTables(): ComponentAuditResult {
    const componentIssues: ComponentAuditResult['issues'] = []
    
    const tables = document.querySelectorAll('table, [role="table"]')
    
    tables.forEach((table, index) => {
      // Check for table headers
      const hasHeaders = table.querySelectorAll('th, [role="columnheader"]').length > 0
      if (!hasHeaders) {
        componentIssues.push({
          rule: 'WCAG 1.3.1 Info and Relationships',
          severity: 'error',
          description: 'Table lacks proper headers',
          element: `Table #${index + 1}`,
        })
      }
      
      // Check header associations
      const headers = table.querySelectorAll('th')
      headers.forEach((header, headerIndex) => {
        if (!header.getAttribute('scope') && !header.id) {
          componentIssues.push({
            rule: 'WCAG 1.3.1 Info and Relationships',
            severity: 'warning',
            description: 'Table header lacks scope attribute or id for cell association',
            element: `Table #${index + 1}, Header #${headerIndex + 1}`,
          })
        }
      })
      
      // Check for sortable indicators
      const sortableHeaders = table.querySelectorAll('[aria-sort], .sortable, [data-sortable]')
      sortableHeaders.forEach((header, headerIndex) => {
        const hasAriaSort = header.getAttribute('aria-sort')
        if (!hasAriaSort) {
          componentIssues.push({
            rule: 'WCAG 4.1.2 Name, Role, Value',
            severity: 'warning',
            description: 'Sortable column lacks aria-sort attribute',
            element: `Table #${index + 1}, Sortable Header #${headerIndex + 1}`,
          })
        }
      })
      
      // Check caption or aria-label
      const hasCaption = table.querySelector('caption')
      const hasAriaLabel = table.getAttribute('aria-label')
      const hasAriaLabelledBy = table.getAttribute('aria-labelledby')
      
      if (!hasCaption && !hasAriaLabel && !hasAriaLabelledBy) {
        componentIssues.push({
          rule: 'WCAG 2.4.6 Headings and Labels',
          severity: 'warning',
          description: 'Table lacks caption or accessible name',
          element: `Table #${index + 1}`,
        })
      }
    })
    
    const passes = componentIssues.filter(issue => issue.severity === 'error').length === 0
    const score = Math.max(0, 100 - (componentIssues.length * 10))
    
    return {
      component: 'DataTable',
      passes,
      issues: componentIssues,
      score,
    }
  }

  /**
   * Audit StatusIndicator component compliance
   */
  auditStatusIndicators(): ComponentAuditResult {
    const componentIssues: ComponentAuditResult['issues'] = []
    
    const statusElements = document.querySelectorAll('.status-indicator, [data-component="status-indicator"]')
    
    statusElements.forEach((element, index) => {
      // Check that status is not conveyed by color alone
      const hasText = element.textContent?.trim()
      const hasIcon = element.querySelector('svg, .icon')
      const hasPattern = window.getComputedStyle(element).backgroundImage !== 'none'
      
      if (!hasText && !hasIcon && !hasPattern) {
        componentIssues.push({
          rule: 'WCAG 1.4.1 Use of Color',
          severity: 'error',
          description: 'Status conveyed by color alone without text or icons',
          element: `StatusIndicator #${index + 1}`,
        })
      }
      
      // Check for role and aria-label if no text
      if (!hasText) {
        const hasRole = element.getAttribute('role')
        const hasAriaLabel = element.getAttribute('aria-label')
        
        if (!hasRole || !hasAriaLabel) {
          componentIssues.push({
            rule: 'WCAG 4.1.2 Name, Role, Value',
            severity: 'error',
            description: 'Non-text status indicator lacks proper role and aria-label',
            element: `StatusIndicator #${index + 1}`,
          })
        }
      }
    })
    
    const passes = componentIssues.filter(issue => issue.severity === 'error').length === 0
    const score = Math.max(0, 100 - (componentIssues.length * 10))
    
    return {
      component: 'StatusIndicator',
      passes,
      issues: componentIssues,
      score,
    }
  }

  /**
   * Audit overall page structure
   */
  auditPageStructure(): ComponentAuditResult {
    const componentIssues: ComponentAuditResult['issues'] = []
    
    // Check for main landmark
    const mainElement = document.querySelector('main, [role="main"]')
    if (!mainElement) {
      componentIssues.push({
        rule: 'WCAG 2.4.1 Bypass Blocks',
        severity: 'error',
        description: 'Page lacks main landmark',
      })
    }
    
    // Check heading hierarchy
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6')
    let previousLevel = 0
    
    headings.forEach((heading, index) => {
      const currentLevel = parseInt(heading.tagName.charAt(1))
      
      if (index === 0 && currentLevel !== 1) {
        componentIssues.push({
          rule: 'WCAG 2.4.6 Headings and Labels',
          severity: 'warning',
          description: 'Page should start with h1 heading',
          element: `First heading: ${heading.tagName}`,
        })
      }
      
      if (currentLevel > previousLevel + 1) {
        componentIssues.push({
          rule: 'WCAG 2.4.6 Headings and Labels',
          severity: 'warning',
          description: `Heading level jumps from h${previousLevel} to h${currentLevel}`,
          element: `Heading #${index + 1}: ${heading.textContent?.slice(0, 50)}...`,
        })
      }
      
      previousLevel = currentLevel
    })
    
    // Check for skip links
    const skipLink = document.querySelector('a[href="#main"], a[href="#content"]')
    if (!skipLink) {
      componentIssues.push({
        rule: 'WCAG 2.4.1 Bypass Blocks',
        severity: 'warning',
        description: 'Page lacks skip navigation link',
      })
    }
    
    // Check language attribute
    const htmlElement = document.documentElement
    if (!htmlElement.getAttribute('lang')) {
      componentIssues.push({
        rule: 'WCAG 3.1.1 Language of Page',
        severity: 'error',
        description: 'HTML element lacks lang attribute',
      })
    }
    
    const passes = componentIssues.filter(issue => issue.severity === 'error').length === 0
    const score = Math.max(0, 100 - (componentIssues.length * 15))
    
    return {
      component: 'Page Structure',
      passes,
      issues: componentIssues,
      score,
    }
  }

  /**
   * Run comprehensive WCAG AA compliance audit
   */
  async runFullAudit(): Promise<ComplianceReport> {
    console.log('🔍 Starting WCAG AA compliance audit...')
    
    const componentResults: ComponentAuditResult[] = [
      this.auditMetricCard(),
      this.auditButtons(),
      this.auditDataTables(),
      this.auditStatusIndicators(),
      this.auditPageStructure(),
    ]
    
    const totalComponents = componentResults.length
    const passingComponents = componentResults.filter(result => result.passes).length
    const totalIssues = componentResults.reduce((sum, result) => sum + result.issues.length, 0)
    const criticalIssues = componentResults.reduce((sum, result) => 
      sum + result.issues.filter(issue => issue.severity === 'error').length, 0
    )
    
    const overallScore = Math.round(
      componentResults.reduce((sum, result) => sum + result.score, 0) / totalComponents
    )
    
    const overallCompliance = criticalIssues === 0 && overallScore >= 80
    
    const recommendations: string[] = []
    
    if (criticalIssues > 0) {
      recommendations.push(`Fix ${criticalIssues} critical accessibility issues`)
    }
    
    if (overallScore < 90) {
      recommendations.push('Improve component accessibility to achieve higher compliance score')
    }
    
    if (!componentResults.find(r => r.component === 'MetricCard')?.passes) {
      recommendations.push('Focus on MetricCard accessibility - ensure proper color contrast and semantic markup')
    }
    
    if (!componentResults.find(r => r.component === 'Button')?.passes) {
      recommendations.push('Ensure all buttons have accessible names and visible focus indicators')
    }
    
    console.log('✅ WCAG AA compliance audit completed')
    
    return {
      overallCompliance,
      overallScore,
      componentResults,
      summary: {
        totalComponents,
        passingComponents,
        totalIssues,
        criticalIssues,
      },
      recommendations,
    }
  }

  /**
   * Generate detailed compliance report
   */
  generateReport(report: ComplianceReport): string {
    const { overallCompliance, overallScore, componentResults, summary, recommendations } = report
    
    return `
# WCAG AA Compliance Audit Report

## Overall Status: ${overallCompliance ? '✅ COMPLIANT' : '❌ NON-COMPLIANT'}
## Overall Score: ${overallScore}/100

## Summary

- **Total Components Tested**: ${summary.totalComponents}
- **Passing Components**: ${summary.passingComponents}/${summary.totalComponents}
- **Total Issues**: ${summary.totalIssues}
- **Critical Issues**: ${summary.criticalIssues}

## Component Results

${componentResults.map(result => `
### ${result.component}

**Status**: ${result.passes ? '✅ PASS' : '❌ FAIL'} | **Score**: ${result.score}/100

${result.issues.length === 0 ? '✅ No accessibility issues found' : `
**Issues (${result.issues.length})**:
${result.issues.map(issue => `
- **${issue.severity.toUpperCase()}**: ${issue.rule}
  - ${issue.description}
  ${issue.element ? `- Element: ${issue.element}` : ''}
`).join('')}
`}
`).join('')}

## Recommendations

${recommendations.length === 0 ? '✅ No recommendations - excellent accessibility!' : recommendations.map(rec => `- ${rec}`).join('\n')}

## Generated: ${new Date().toISOString()}

---

**Note**: This audit focuses on automated testing. Manual testing is recommended for comprehensive accessibility validation.
    `.trim()
  }

  /**
   * Helper method to convert RGB to Hex
   */
  private rgbToHex(rgb: string): string {
    const match = rgb.match(/\d+/g)
    if (!match) return '#000000'
    
    const r = parseInt(match[0]).toString(16).padStart(2, '0')
    const g = parseInt(match[1]).toString(16).padStart(2, '0')
    const b = parseInt(match[2]).toString(16).padStart(2, '0')
    
    return `#${r}${g}${b}`
  }

  /**
   * Helper method to check if text contains numbers
   */
  private containsNumbers(text: string): boolean {
    return /\d/.test(text)
  }
}

// Usage function
export async function runWCAGAudit(): Promise<ComplianceReport> {
  const auditor = new WCAGAuditor()
  const report = await auditor.runFullAudit()
  
  console.log('📊 WCAG AA Compliance Report:')
  console.log(auditor.generateReport(report))
  
  return report
}

export { WCAGAuditor }
export type { ComponentAuditResult, ComplianceReport }