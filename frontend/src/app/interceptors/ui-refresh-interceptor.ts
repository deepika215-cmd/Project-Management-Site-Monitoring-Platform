import { ApplicationRef, inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { finalize } from 'rxjs';

/**
 * Angular 22 can run without Zone.js. Many existing BuildTrack pages update
 * plain component properties inside HttpClient subscriptions, so the HTTP
 * response can arrive without notifying the view. This interceptor schedules
 * one application refresh after each HTTP request completes. It keeps the
 * existing component code/API calls intact and applies the fix globally.
 */
export const uiRefreshInterceptor: HttpInterceptorFn = (req, next) => {
  const appRef = inject(ApplicationRef);

  return next(req).pipe(
    finalize(() => {
      queueMicrotask(() => {
        if (!appRef.destroyed) {
          appRef.tick();
        }
      });
    })
  );
};
