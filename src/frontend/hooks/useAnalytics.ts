import { trackEvent } from '../utils/analytics';

/**
 * React hook for common analytics events.
 */
export function usePageView(pageName: string) {
  trackEvent('page_viewed', { page: pageName });
}

export function useButtonClick(buttonId: string) {
  return () => trackEvent('button_clicked', { button_id: buttonId });
}
