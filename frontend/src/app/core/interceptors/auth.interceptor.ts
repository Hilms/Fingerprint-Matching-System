import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { catchError, switchMap, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);

  const accessToken = auth.get_access_token();

  //  IMPORTANT: do NOT attach token to refresh endpoint
  const isRefreshRequest = req.url.includes('/auth/refresh');

  // attach access token to ALL normal requests
  if (accessToken && !isRefreshRequest) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  }

  // send request to backend
  return next(req).pipe(
    catchError(err => {
      // refresh endpoint failed
      // do NOT try to refresh again or we'll create an infinite loop.
      if (req.url.includes('/auth/refresh')) {
        return throwError(() => err);
      }

      // handle expired access token ONLY
      if (err.status === 401) {
        const refreshToken = auth.get_refresh_token();

        if (!refreshToken) {
          auth.logout();
          return throwError(() => err);
        }

        return auth.refresh_token().pipe(
          switchMap((res: any) => {
            auth.store_access_token(res.access_token);

            const retryReq = req.clone({
              setHeaders: {
                Authorization: `Bearer ${res.access_token}`,
              },
            });

            return next(retryReq);
          }),
        );
      }

      // REAL errors (403, 500, etc.)
      return throwError(() => err);
    })
  );
};
