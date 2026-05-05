# Migration From a Private Fork

For anyone (including the original author of `job-hunt-os`) who maintains a private fork with real PII and wants to pull in updates from this public template without leaking anything.

## The Setup

You have:
- A **private repo** with real data: real names, real employers, real message drafts, real contact lists, possibly committed history with PII.
- A **public template** (`<your-org>/job-hunt-os`) you want to pull updates from.

The risk: pulling template updates into the private repo is fine. **Pushing private data back to the template is a disaster.** This doc is about preventing the latter.

## The Pattern

### Option A: Cherry-pick updates manually (safest)

1. Watch the public template repo. When a useful update lands, `git diff` the relevant file(s).
2. Manually apply the diff to your private fork (re-typing or `git apply` from a patch).
3. Commit in your private fork with a reference: `Apply <commit> from job-hunt-os template`.
4. Never set the public template as a git remote in your private repo.

Pros: zero risk of accidental upstream push.
Cons: manual work; easy to fall behind.

### Option B: Add the template as a separate remote (more convenient, more risk)

```bash
cd <your-private-repo>
git remote add template https://github.com/<your-org>/job-hunt-os.git
git fetch template
```

Then to pull updates:
```bash
git checkout main
git pull template main --rebase --no-tags
# Resolve conflicts (your customisations vs template updates)
git push origin main   # ONLY origin, never template
```

To prevent accidental pushes to the template:
```bash
git remote set-url --push template DISABLE
```
(This makes `git push template` fail loudly.)

Pros: easy to stay current.
Cons: you must NEVER `git push template`; one slip and your private data leaks.

### Option C: Periodically rebuild a clean copy (most disciplined)

1. Run a script that:
   - Clones a fresh copy of the public template into a new directory.
   - Copies your private data files (`.env`, `config/*.yaml`, `applications/resumes/data/{slug}/`, etc.) over the fresh copy.
   - Verifies the diff is exactly your private data — no leakage in the other direction.
2. Replace your private fork's tracked files with the fresh copy.

Pros: forces a clean slate every time. Catches drift in the template's structure.
Cons: more work per update; need to maintain the script.

## What NOT to Do

- **Don't `git filter-repo` your private repo to extract a clean public version.** Filter-repo is fragile, especially with binary files (.docx). Easy to leave dangling references to deleted commits in the reflog. Recommended: build the public template from scratch (clean tree, clean history) — see `docs/PLAN.md`.
- **Don't fork the public template publicly with your real data overlaid.** Use template instantiation with `--private`:
  ```bash
  gh repo create my-job-hunt --template <your-org>/job-hunt-os --private
  ```
- **Don't share your `~/.claude.json`** if it contains real PATs or LinkedIn cookies.
- **Don't commit `.env`** — it's gitignored, but verify with `git ls-files | grep env`.

## Cross-Pollination Rules

When you find improvements in your private fork that should land in the public template:

1. **Fictionalise first**. Replace every real name / company / region with a placeholder before opening a PR.
2. **Validate with the forbidden-token grep** (see `docs/PLAN.md` Phase 2 validation gate). Run it across the diff:
   ```bash
   git diff main..<your-pr-branch> | grep -iE 'real-person|real-employer|real-region|real-token-pattern'
   ```
3. **Open the PR from a clean branch in your fork of the public template**, not from your private repo.

## Sanitisation Checklist (when contributing back)

- [ ] No real personal names anywhere
- [ ] No real employer names tied to a real person's hunt
- [ ] No real contact data (LinkedIn URLs, emails, phone numbers)
- [ ] No real region / industry assumptions baked into rules — must be config-driven
- [ ] No hardcoded NocoDB IDs, tokens, URLs
- [ ] No deprecated MCP prefixes
- [ ] No hardcoded fit-score adjustments tied to a specific person's gap analysis
- [ ] No "Why Right Person" examples with real people
- [ ] Forbidden-token grep returns zero hits

## Auditing Your Private Repo for Leaks

Periodically run:
```bash
# Check tracked files for known sensitive patterns
git grep -iE '(your-real-name|your-employer|<sensitive token pattern>)'

# Check git history for committed secrets
gitleaks detect --source . --redact

# Check that .env is not tracked
git ls-files | grep -i env  # should only show .env.example
```

If something leaked, that's a real incident. Treat it like any other security issue: rotate credentials, force-push history rewrites only if the repo is private and you can coordinate with all collaborators, document the incident.

## Recovery Path

If you accidentally pushed real PII to the public template:
1. **Don't panic, but act fast.** GitHub caches push events; even a force-push to delete the commit doesn't fully erase it.
2. Force-push history to remove the offending commit (only works if the repo is yours).
3. Rotate any credentials that were in the leaked content.
4. If you can't force-push (e.g., it's the upstream template repo, not your fork), file an immediate issue with the maintainer asking them to coordinate rotation.
5. Consider GitHub's [secret scanning push protection](https://docs.github.com/en/code-security/secret-scanning/push-protection-for-repositories-and-organizations) for future prevention.

## Origin

This template was extracted from a real, private job-hunt repo using **Option C** (rebuild from a clean tree, clean history) — not `git filter-repo`. The 60+ session summaries with names, message drafts, and contact data in the private repo's git history would have made filter-repo brittle. A clean tree, clean history was both safer and faster.

If you maintain that private fork, the canonical migration path back is the cherry-pick or rebuild approach — never set the public repo as a git remote on the private one without push-disable, and never push the private repo to the public remote.
