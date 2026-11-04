/**
 * Resolve the timezone used for user-facing timestamps.
 *
 * Priority:
 *   1. the IANA timezone saved on the signed-in user (from /auth/login or /me)
 *   2. the browser's timezone
 *   3. UTC, so a broken Intl implementation still renders a stable value
 */
export function getUserTimeZone() {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (user && typeof user.timezone === 'string' && user.timezone.trim()) {
      return user.timezone.trim()
    }
  } catch {
    // Corrupt localStorage should not break every date on the page.
  }

  try {
    const browserTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone
    if (browserTimeZone) return browserTimeZone
  } catch {
    // Fall through to UTC.
  }

  return 'UTC'
}
