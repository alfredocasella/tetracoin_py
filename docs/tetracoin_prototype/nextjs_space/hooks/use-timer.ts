
'use client';

import { useEffect, useRef, useCallback } from 'react';

export function useTimer(
  isActive: boolean,
  initialTime: number,
  onTick: (time: number) => void
) {
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const timeRef = useRef(initialTime);

  useEffect(() => {
    timeRef.current = initialTime;
  }, [initialTime]);

  const startTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    intervalRef.current = setInterval(() => {
      timeRef.current = Math.max(0, timeRef.current - 1);
      onTick(timeRef.current);

      if (timeRef.current <= 0 && intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }, 1000);
  }, [onTick]);

  const stopTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (isActive) {
      startTimer();
    } else {
      stopTimer();
    }

    return () => stopTimer();
  }, [isActive, startTimer, stopTimer]);

  return { stopTimer };
}
