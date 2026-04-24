# CORS Origin Config Design

## Goal

Make backend CORS origins configurable via environment while keeping local development working for both `http://localhost:3000` and `http://127.0.0.1:3000`.

## Scope

This change covers:

- replacing the hardcoded CORS origin list in the backend
- adding an environment-driven origin parser
- keeping local development functional without requiring extra configuration
- documenting the new environment variable

This change does not broaden CORS beyond explicit origins.

## Options

### Option 1: Environment-configurable origins with local defaults

Read a comma-separated env var such as `CORS_ALLOW_ORIGINS`, and fall back to:

- `http://localhost:3000`
- `http://127.0.0.1:3000`

Pros:

- fixes the current local issue
- stays explicit and safe
- supports future frontend origins without another code change

Cons:

- adds a small config parsing step

### Option 2: Hardcode two local origins

Pros:

- smallest code change

Cons:

- requires code edits for future environments

### Recommendation

Use Option 1. The behavior remains explicit, the fix covers the current localhost mismatch, and deployment-specific origins can be set through environment configuration.

## Implementation

1. Add a small helper in the backend to parse a comma-separated `CORS_ALLOW_ORIGINS` environment variable.
2. Default to `http://localhost:3000,http://127.0.0.1:3000` when the variable is unset.
3. Pass the parsed list into FastAPI `CORSMiddleware`.
4. Document the variable in project docs where local/frontend environment configuration is described.
5. Verify by testing preflight/requests from both origins.

## Risks

- If the env var is malformed, some intended origins may be omitted.
- Keeping the parser simple and trimming whitespace avoids most operator errors.

## Success Criteria

- Requests from `http://localhost:3000` succeed.
- Requests from `http://127.0.0.1:3000` also succeed.
- Additional frontend origins can be enabled without code changes by setting `CORS_ALLOW_ORIGINS`.
