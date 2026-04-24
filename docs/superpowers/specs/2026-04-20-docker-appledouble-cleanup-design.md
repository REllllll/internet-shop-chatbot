# Docker AppleDouble Cleanup Design

## Goal

Remove all existing macOS AppleDouble metadata files (`._*`) from the repository and prevent them from polluting Git status and Docker build contexts again.

## Scope

This change covers:

- one-time cleanup of all current `._*` files in the repository
- repo-level ignore rules so `._*` files do not show up as untracked changes
- Docker ignore rules for all Compose build contexts so `docker compose build` does not fail when these files exist locally

This change does not attempt to alter macOS or external-drive behavior outside the repository.

## Approach

### Option 1: Repo hygiene at source

Delete existing `._*` files, add Git ignore patterns, and exclude them from Docker contexts.

Pros:

- fixes the current build failure
- prevents recurrence in Git and Docker workflows
- keeps the fix local to the repo

Cons:

- cannot stop macOS from recreating `._*` files on disk

### Option 2: Cleanup during builds

Run cleanup commands inside Docker builds or helper scripts.

Pros:

- can mask local pollution during some workflows

Cons:

- reactive rather than preventive
- still leaves the repo dirty locally
- can fail before the cleanup step because Docker must send the build context first

### Recommendation

Use Option 1. The failure happens while Docker is preparing the build context, so the reliable fix is to exclude `._*` files before they are sent and to clean the current copies from disk.

## Implementation

1. Add root-level `.gitignore` rules for `._*` and `**/._*`.
2. Ensure each Docker build context excludes AppleDouble files:
   - `frontend/.dockerignore`
   - `backend/.dockerignore`
   - `docker/.dockerignore`
   - any nested build context used by `docker/docker-compose.yml`
3. Remove all existing `._*` files from the repository tree.
4. Verify with:
   - `find . -name '._*'`
   - `git status --short`
   - `docker compose -f docker/docker-compose.yml build`

## Risks

- Existing local processes are unaffected; this is a filesystem hygiene change.
- New `._*` files may still be created by macOS later, but they should no longer affect Git or Docker builds after this change.

## Success Criteria

- `find . -name '._*'` returns no matches immediately after cleanup.
- `docker compose -f docker/docker-compose.yml build` no longer fails because of AppleDouble files in build contexts.
- Future `._*` files are ignored by Git and excluded from Docker contexts.
