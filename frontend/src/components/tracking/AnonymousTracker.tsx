'use client';

import { useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';
import axios from 'axios';

interface TrackingProps {
  children?: React.ReactNode;
}

export default function AnonymousTracker({ children }: TrackingProps) {
  const pathname = usePathname();
  const startTime = useRef(Date.now());
  const sessionId = useRef<string | null>(null);

  useEffect(() => {
    // Get or create session ID from cookie
    const cookies = document.cookie.split(';').reduce((acc, cookie) => {
      const [key, value] = cookie.trim().split('=');
      acc[key] = value;
      return acc;
    }, {} as Record<string, string>);
    
    sessionId.current = cookies['anon_session'] || null;
  }, []);

  // Track page views
  useEffect(() => {
    const trackPageView = async () => {
      const loadTime = Date.now() - startTime.current;
      
      try {
        const response = await axios.post(
          'http://localhost:8000/api/v1/anonymous/track-event',
          {
            event_type: 'page_view',
            page: pathname,
            load_time: loadTime,
            metadata: {
              referrer: document.referrer || null,
              language: navigator.language,
              timestamp: new Date().toISOString()
            }
          },
          {
            headers: {
              'screen-size': `${window.screen.width}x${window.screen.height}`
            },
            withCredentials: true
          }
        );
        
        // Store session ID from response
        if (response.data.session_id) {
          sessionId.current = response.data.session_id;
          // Set cookie for future requests
          document.cookie = `anon_session=${response.data.session_id}; path=/; max-age=2592000`; // 30 days
        }
      } catch (error) {
        console.error('Error tracking page view:', error);
      }
    };

    trackPageView();
  }, [pathname]);

  // Track user interactions
  useEffect(() => {
    const trackInteraction = async (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      const component = target.getAttribute('data-track') || 
                       target.closest('[data-track]')?.getAttribute('data-track');
      
      if (!component) return;

      try {
        await axios.post(
          'http://localhost:8000/api/v1/anonymous/track-event',
          {
            event_type: 'click',
            component: component,
            page: pathname,
            metadata: {
              text: target.textContent?.slice(0, 50),
              tagName: target.tagName
            }
          },
          { withCredentials: true }
        );
      } catch (error) {
        console.error('Error tracking interaction:', error);
      }
    };

    document.addEventListener('click', trackInteraction);
    return () => document.removeEventListener('click', trackInteraction);
  }, [pathname]);

  // Track time on page
  useEffect(() => {
    return () => {
      const timeSpent = Math.round((Date.now() - startTime.current) / 1000);
      
      axios.post(
        'http://localhost:8000/api/v1/anonymous/track-event',
        {
          event_type: 'page_exit',
          page: pathname,
          value: timeSpent.toString(),
          metadata: {
            time_spent_seconds: timeSpent
          }
        },
        { withCredentials: true }
      ).catch(() => {});
    };
  }, [pathname]);

  return <>{children}</>;
}
