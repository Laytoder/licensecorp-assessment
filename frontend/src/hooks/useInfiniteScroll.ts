import { useEffect, useRef, useCallback } from 'react';

interface UseInfiniteScrollProps {
  onIntersect: () => void;
  enabled?: boolean;
  threshold?: number;
  rootMargin?: string;
}

export const useInfiniteScroll = ({
  onIntersect,
  enabled = true,
  threshold = 0.1,
  rootMargin = '200px',
}: UseInfiniteScrollProps) => {
  const observerRef = useRef<IntersectionObserver | null>(null);
  const targetRef = useRef<HTMLDivElement | null>(null);

  const setTarget = useCallback((element: HTMLDivElement | null) => {
    targetRef.current = element;
  }, []);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    observerRef.current = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting) {
          onIntersect();
        }
      },
      {
        threshold,
        rootMargin,
      }
    );

    const currentTarget = targetRef.current;
    if (currentTarget) {
      observerRef.current.observe(currentTarget);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [enabled, onIntersect, threshold, rootMargin]);

  return { setTarget };
}; 