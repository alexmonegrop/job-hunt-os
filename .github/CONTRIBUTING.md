# Contributing

Thanks for considering a contribution. This template is meant to evolve — but it's also opinionated, so read this before opening a PR.

## Quick principles

- **The system is opinionated by design.** PRs that *replace* a workflow with a clearly better one are welcome. PRs that *add* a parallel "way of doing it" without removing existing ones are usually rejected. Workflow proliferation is a maintenance tax.
- **No PII in commits.** Never commit names, emails, message drafts, or contact data. The `.gitignore` is permissive about user-content directories — keep it that way. If you find yourself wanting to commit a real example, make it fictional first (Jane Demo style).
- **Sanitise as you go.** If a rule, skill, doc, or operating procedure still contains a real person's name or company, that's a bug — file an issue or PR with the fix.
- **Test against a fresh instance.** New rules and skills should work against a clean schema, not assume a populated one. If your skill assumes "Target Companies has at least 30 records", flag that as a precondition in the SKILL.md.
- **Maintain the four-layer split.** Don't put workflow steps in rules. Don't put always-true invariants in skills. See `docs/ARCHITECTURE.md`.

## What kinds of PR are welcome

### Welcome
- Bug fixes (typos, broken links, mis-described behaviour)
- New skills that fill a clear gap (e.g., "linkedin-post-drafting" if it's currently missing)
- Improvements to existing rules / procedures based on real session learnings
- New regions / industries (add to `config/*.example.yaml`, not the rules)
- Documentation improvements
- The deferred Phase 4 work (Python tooling, Docker Compose stack, init scripts) — this is the biggest open chunk

### Less welcome
- Cosmetic refactors of working code
- Adding a "configurable everything" option for something already at the right level of opinion
- New workflow patterns that overlap with existing skills (instead, suggest improving the existing one)
- Reformatting markdown for personal style preferences

## Issues vs PRs

- **Issues**: feature ideas, bug reports, regional / industry adaptation requests, "have you considered…" questions.
- **PRs**: code / doc changes. Reference an issue if one exists. Keep PRs scoped — one logical change per PR.

## Dev environment

Same as the user setup (`docs/SETUP.md`). For testing:
- Point your `.env` at a throwaway NocoDB instance (a separate Docker stack or a free NocoDB Cloud project).
- Use `JOB_HUNT_USER=jane-demo` to test against the bundled fictional data.
- Run forbidden-token grep before committing — see `docs/PLAN.md` Phase 2 validation gate.

## PR checklist

Before opening a PR:
- [ ] Forbidden-token grep returns zero hits in `.claude/`, `operating-procedures/`, `reference-files/`, and any other tracked directories. Tokens to grep: real personal names, real employer names tied to a person, hardcoded NocoDB IDs / tokens / URLs, deprecated MCP prefixes (`*BlackHills*`, etc.).
- [ ] All new files end with a newline.
- [ ] Any new config knobs have an entry in `*.example.yaml`.
- [ ] Any new rules / skills are referenced from the index files (`.claude/rules/00-README.md`, etc.) and from `AGENTS.md` if relevant.
- [ ] Any new procedures are listed in `operating-procedures/00-README-PROCEDURES.md`.
- [ ] You've tested against `jane-demo` (where applicable).
- [ ] No real `.env` values, PATs, cookies, or other secrets are anywhere in the diff.

## Commit messages

Use a milestone or component prefix: `M5: ...`, `rules: ...`, `skill(cold-outreach): ...`. Imperative mood ("Fix typo", not "Fixed typo"). Reference issues with `#NN`.

## Reporting security issues

If you find a security issue (e.g., a leaked credential pattern, a vulnerability in the apply skill that could damage real applications), do NOT open a public issue. Email the maintainer directly.

## Review etiquette

- Reviews are about correctness and fit, not preference. If you disagree with a review comment, push back with reasoning — that's a conversation, not a confrontation.
- Maintainer will sometimes close PRs without merging. That's fine — fork and run your own version. The opinionated nature of this template means not everything fits everyone.

## License

By contributing you agree your contribution is licensed under MIT (see [`LICENSE`](../LICENSE)).
