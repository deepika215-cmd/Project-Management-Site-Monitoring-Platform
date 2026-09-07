import { ApplicationRef, NgZone, inject } from '@angular/core';
import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError, finalize, throwError, timeout } from 'rxjs';

/**
 * Global async/UI guard for the BuildTrack frontend.
 *
 * The application contains many pages that update ordinary component fields
 * inside HttpClient subscriptions. This interceptor makes those updates render
 * immediately on the first navigation/click and prevents any request from
 * leaving a page stuck on "Loading..." or "Saving..." forever.
 */
export const uiRefreshInterceptor: HttpInterceptorFn = (req, next) => {
  const appRef = inject(ApplicationRef);
  const zone = inject(NgZone);

  return next(req).pipe(
    // Apply the safety timeout to GET and write requests alike. Individual
    // pages may use a shorter timeout, but no request can hang indefinitely.
    timeout({ first: 12000 }),
    catchError((error: unknown) => {
      if ((error as any)?.name === 'TimeoutError') {
        return throwError(() => new HttpErrorResponse({
          status: 0,
          statusText: 'Request Timeout',
          url: req.url,
          error: {
            detail: 'The backend did not respond within 12 seconds. Check that FastAPI is running on http://localhost:8000.'
          }
        }));
      }
      return throwError(() => error);
    }),
    finalize(() => {
      // Run a refresh after the current async turn. NgZone + ApplicationRef
      // covers both zone-aware and legacy component code in this project.
      zone.run(() => {
        setTimeout(() => {
          if (!appRef.destroyed) {
            appRef.tick();
          }
        }, 0);
      });
    })
  );
};
