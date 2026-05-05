# Contributing

> ⏳ Stub — full guide lands in Phase 7. See [`docs/PLAN.md`](PLAN.md).

## Quick principles

- **The system is opinionated by design.** PRs that add new "ways of doing it" without removing existing ones are likely to be rejected. PRs that *replace* a workflow with a clearly better one are welcome.
- **No PII in commits.** Never commit names, emails, message drafts, or contact data. The `.gitignore` is permissive about user content directories — keep it that way.
- **Sanitise as you go.** If a rule, skill, or doc still contains a real person's name or company, that's a bug — file an issue or PR.
- **Test against a fresh NocoDB instance.** New rules and skills should work against a clean schema, not assume a populated one.

## Issues vs PRs

- **Issues**: feature ideas, bug reports, regional/industry adaptation requests.
- **PRs**: code changes, doc improvements. Reference an issue if one exists. Keep PRs scoped — one logical change per PR.

## Dev environment

Same as the user setup (`docs/SETUP.md`). For testing, point your `.env` at a throwaway NocoDB instance (a separate Docker stack or a free Supabase project) so you don't pollute your real data.
