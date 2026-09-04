import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {

  // =====================================================
  // GET JWT TOKEN
  // =====================================================

  const token =
    localStorage.getItem('access_token') ||
    localStorage.getItem('token');

  console.log(
    'Auth Interceptor - Token exists:',
    !!token
  );

  // =====================================================
  // NO TOKEN
  // =====================================================

  if (!token) {

    console.warn(
      'Auth Interceptor - No JWT token found'
    );

    return next(req);
  }

  // =====================================================
  // DON'T DUPLICATE AUTHORIZATION HEADER
  // =====================================================

  if (req.headers.has('Authorization')) {

    console.log(
      'Auth Interceptor - Authorization header already exists'
    );

    return next(req);
  }

  // =====================================================
  // ADD JWT TOKEN
  // =====================================================

  const authReq = req.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`
    }
  });

  console.log(
    'Auth Interceptor - Authorization header added'
  );

  return next(authReq);
};