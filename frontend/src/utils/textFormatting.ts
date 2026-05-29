/**
 * Formats field names with support for subscripts and other formatting
 * Supports syntax like: CO_{2}, H_{2}O, PM_{2.5}, etc.
 */
export const formatFieldName = (field: string): string => {
  // First replace underscores with spaces and convert to uppercase
  let formatted = field.replace(/_/g, ' ').toUpperCase()
  return formatted
}

/**
 * Helper function to process field names with subscript syntax
 * Converts patterns like CO_2 to CO_{2} for proper parsing
 */
export const preprocessFieldName = (field: string): string => {
  // Replace common patterns like CO_2, PM_2.5, etc.
  // Convert CO_2 to CO_{2}, but be careful with longer names
  return field
    .replace(/([A-Za-z]+)_(\d+(?:\.\d+)?)/g, '$1_{$2}') // Match letters followed by underscore and numbers
    .replace(/_/g, ' ') // Replace remaining underscores with spaces
    .toUpperCase()
}

/**
 * Formats field names with Unicode subscript characters for common environmental measurements
 * Handles chemical formulas and particle measurements automatically
 */
export const formatWithUnicodeSubscripts = (field: string): string => {
  const subscriptMap: Record<string, string> = {
    '0': '₀',
    '1': '₁',
    '2': '₂',
    '3': '₃',
    '4': '₄',
    '5': '₅',
    '6': '₆',
    '7': '₇',
    '8': '₈',
    '9': '₉',
    '.': '.' // Keep dots as-is
  }

  const superscriptMap: Record<string, string> = {
    '0': '⁰',
    '1': '¹',
    '2': '²',
    '3': '³',
    '4': '⁴',
    '5': '⁵',
    '6': '⁶',
    '7': '⁷',
    '8': '⁸',
    '9': '⁹',
    '.': '.' // Keep dots as-is
  }

  let formatted = field

  // First handle LaTeX-style subscripts: CO_{2} -> CO₂
  formatted = formatted.replace(/_{([^}]+)}/g, (_match, subscriptContent) => {
    const cleanedContent = subscriptContent.replace(/_/g, '')
    return cleanedContent
      .split('')
      .map((char: string) => subscriptMap[char] || char)
      .join('')
  })

  // Then handle LaTeX-style superscripts: m^{3} -> m³
  formatted = formatted.replace(/\^{([^}]+)}/g, (_match, superscriptContent) => {
    const cleanedContent = superscriptContent.replace(/[\^_]/g, '')
    return cleanedContent
      .split('')
      .map((char: string) => superscriptMap[char] || char)
      .join('')
  })

  // Then handle underscore notation: CO_2 -> CO₂ (but only if not already processed)
  formatted = formatted.replace(/([A-Za-z]+)_(\d+(?:\.\d+)?)/g, (_match, chemical, number) => {
    const subscriptNumber = number
      .split('')
      .map((char: string) => subscriptMap[char] || char)
      .join('')
    return chemical + subscriptNumber
  })

  // Handle remaining underscores (those not part of subscripts) and convert to uppercase
  formatted = formatted.replace(/_/g, ' ')

  // Replace patterns like "CO 2" with "CO₂" (space-separated)
  formatted = formatted.replace(/\b([A-Z]+)\s+(\d+(?:\.\d+)?)\b/g, (_match, chemical, number) => {
    const subscriptNumber = number
      .split('')
      .map((char: string) => subscriptMap[char] || char)
      .join('')
    return chemical + subscriptNumber
  })

  return formatted
}
