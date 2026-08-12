import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';
import { Api } from '../services/api';

function tokenIsValid(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
    return !payload.exp || payload.exp * 1000 > Date.now();
  } catch {
    return false;
  }
}

export const authGuard: CanActivateFn = () => {
  const router = inject(Router);
  const token = localStorage.getItem('token');

  if (!token || !tokenIsValid(token)) {
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
    return router.createUrlTree(['/login']);
  }

  return true;
};

export const roleGuard = (allowedRoles: string[]): CanActivateFn => () => {
  const router = inject(Router);
  const api = inject(Api);
  const token = localStorage.getItem('token');
  if (!token || !tokenIsValid(token)) return router.createUrlTree(['/login']);

  const cached = localStorage.getItem('currentUser');
  const normalized = allowedRoles.map(role => role.toUpperCase());

  if (cached) {
    try {
      const role = JSON.parse(cached)?.role?.toUpperCase();
      if (role && normalized.includes(role)) return true;
    } catch { /* fetch the current user below */ }
  }

  return api.getCurrentUser().pipe(
    map((user: any) => {
      localStorage.setItem('currentUser', JSON.stringify(user));
      return normalized.includes((user?.role || '').toUpperCase())
        ? true
        : router.createUrlTree(['/profile']);
    }),
    catchError(() => of(router.createUrlTree(['/login'])))
  );
};
