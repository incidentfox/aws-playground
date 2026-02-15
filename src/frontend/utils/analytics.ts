/**
 * Generic analytics wrapper.
 * Replace the console.log with your analytics provider.
 */
export function trackEvent(name: string, properties?: Record<string, unknown>) {
  if (typeof window !== 'undefined') {
    console.log(`[analytics] ${name}`, properties);
    // TODO: Replace with your analytics provider:
    // amplitude.track(name, properties);
    // mixpanel.track(name, properties);
    // posthog.capture(name, properties);
  }
}
