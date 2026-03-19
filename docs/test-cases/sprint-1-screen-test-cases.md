# Sprint 1 Screen Test Cases

## Home (#1)
- Anonymous user opens `/` and sees hero copy plus `Get Started` and `Log In`.
- Authenticated user opens `/` and is redirected to `/dashboard`.
- Home layout is visually distinct from the dashboard.

## Register (#2)
- Valid registration creates a user, logs them in, and redirects to `/dashboard`.
- Duplicate email shows an inline validation error.
- Invalid email format shows an inline validation error.
- Password shorter than 8 characters shows an inline validation error.
- Non-matching passwords show an inline validation error.

## Login (#3)
- Valid login redirects to `/dashboard`.
- Wrong password shows `Invalid email or password`.
- Missing account shows `Invalid email or password`.
- Disabled user cannot log in.
- Logout redirects to `/` and clears access to `/dashboard`.

## Dashboard (#4)
- Dashboard requires authentication.
- Dashboard shows welcome copy and quick links.
- Empty state appears when no transactions exist.
- Stats appear when transactions exist: count, date range, top categories.

