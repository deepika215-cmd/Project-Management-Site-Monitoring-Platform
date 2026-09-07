import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, withRouterConfig } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

import { routes } from './app.routes';
import { authInterceptor } from './interceptors/auth-interceptor';
import { uiRefreshInterceptor } from './interceptors/ui-refresh-interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    // This project uses many HttpClient subscriptions that assign values directly
    // to component fields. Angular 22 is zoneless by default, so enabling
    // Zone.js-based change detection makes every page refresh immediately when
    // API responses, timers and other async work finish.
    provideZoneChangeDetection({ eventCoalescing: false, runCoalescing: false }),
    provideRouter(routes, withRouterConfig({ onSameUrlNavigation: 'reload' })),
    provideHttpClient(withInterceptors([authInterceptor, uiRefreshInterceptor]))
  ]
};
