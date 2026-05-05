# Extend

How to add new rules, skills, tools, or employer-specific extensions to your fork.

## Adding a New Rule

Rules are auto-loaded standards. Add a new rule when you've found a class of mistake that should be impossible, or a class of correctness check that should always run.

1. Create `.claude/rules/NN-<topic>.md` (numbered to set load order). Numbers 00-07 are taken; 08-99 are available.
2. Lead with `# <Topic>` and a one-line purpose.
3. Use `ALWAYS`, `NEVER`, `MUST` for non-negotiable items.
4. Keep it concise — bullets, not paragraphs. Reference operating procedures for detailed rationale.
5. Add a one-liner to `.claude/rules/00-README.md` "Rule Files in This Directory" list.
6. Update `AGENTS.md` "The Rules" table if the rule is high-stakes enough to call out at the agent's onboarding.

Test: open a fresh Claude Code session and verify the agent honours the new rule without you mentioning it.

## Adding a New Skill

Skills are invokable workflows. Add one when you have a recurring multi-step task that doesn't fit an existing skill.

1. Create the directory: `.claude/skills/<skill-name>/`.
2. Create `SKILL.md` with frontmatter:
   ```yaml
   ---
   name: "skill-name"
   description: "When this skill should be used and what it does. The agent reads this to decide when to invoke autonomously."
   user_invocable: true
   ---
   ```
3. Document: prerequisites, MCP tools needed, quick-start invocations, the workflow (numbered steps), output structure, quality checklist, integration with other skills.
4. Make sure the workflow uses **config / per-user data**, never hardcoded values.
5. Reference relevant rules in the SKILL.md (which rules the workflow honours).
6. If there's an associated long-form methodology, add a procedure under `operating-procedures/` and link from the SKILL.md.

Test: invoke `/<skill-name>` in a fresh session. Verify it picks up the active user, reads the right config files, and produces the expected output.

## Adding a New Tool

Tools are Python CLIs that skills shell out to. Add one when:
- You need to crunch data the agent can't do efficiently in-context (e.g., generate `.docx`, scrape job boards, run vector search).
- The work is stateful (writes files, calls external APIs).
- The work is reusable across multiple skills.

1. Create `tools/<tool-name>/`.
2. Add a `README.md` with usage, dependencies, and example invocations.
3. Use named arguments (`--user`, `--job-file`, `--output-dir`) — never positional. The agent passes them by name.
4. Use absolute paths in arguments, never relative. The agent's working directory varies.
5. Print machine-readable output to stdout (JSON for structured data; otherwise plain text). Errors go to stderr.
6. Exit with non-zero on failure so the agent can detect it.
7. Add the dependency to your `pyproject.toml` / `requirements.txt`.

Test: invoke from the command line with the same arguments the agent would use. Then invoke from inside a skill via `Bash`.

## Adding a New Operating Procedure

Procedures are long-form methodology docs. Add one when:
- A skill workflow has substantive rationale that doesn't fit in a concise SKILL.md.
- You've accumulated lessons learned over several sessions worth preserving.
- The methodology is broad enough to be useful across multiple skills.

1. Create `operating-procedures/<TOPIC>-v1.md` (or vN if it's a new version of an existing procedure).
2. Lead with version, last-updated date, document type ("Reference (for humans + AI agents)"), purpose, companion rules / skills.
3. Structure as a step-by-step walkthrough with examples.
4. Use fictional company / person names if you include examples.
5. Add an entry to `operating-procedures/00-README-PROCEDURES.md`.
6. Reference the procedure from the related SKILL.md.

## Adding an Employer Extension (the "Sia pattern")

Sometimes you'll have a specific employer for whom you're building heavy custom artefacts (custom resume styling, employer-specific deck templates, engagement-tracker spreadsheets, etc.). Rather than polluting the main system, build it as an **employer extension**.

Pattern:
1. Create `tools/employer-extensions/<employer-slug>/`.
2. Inside, organise as needed — typically: `content.py` (employer-specific bullet points and overrides), `render_resume.py` (employer-specific Word styling), `render_deck.py` (employer-specific slide template), `tracker.py` (engagement spreadsheet generator).
3. Use the slug as a namespace — `import` from your extension as `tools.employer_extensions.acme_consulting.content`.
4. Document in `tools/employer-extensions/<slug>/README.md`.
5. **Important**: never commit real employer names tied to a real person's hunt. Use the pattern as a structural template; the actual named extensions are user-private.

The bundled `tools/employer-extension-example/` directory shows the pattern with a fictional employer (Phase 4).

## Adding Multi-User Support

Most of the system is already multi-user-ready (the `users` table, `user_id` columns, per-user directories). To onboard a new user to your shared system:

1. Run `/onboard-user` — handles the full intake (8 phases).
2. Verify they have their own slug (`config/user-profile.yaml` `slug`) and per-user directories.
3. Set `JOB_HUNT_USER=<their-slug>` in `.env` when operating on their behalf.

For details, see [`MULTI-USER.md`](MULTI-USER.md).

## Adding a New Database Backend

The system defaults to NocoDB but is structured to support alternative backends:

1. Re-implement the schema in your backend of choice (Postgres directly, Airtable, Supabase, etc.). The shape lives in `infrastructure/init-db/02-jobhunt-schema.sql` (Phase 4) — adapt as needed.
2. Build or install an MCP server with a unique prefix (`mcp__postgres__`, `mcp__airtable__`, etc.).
3. Set `NOCODB_MCP_PREFIX` in `.env` to your new prefix.
4. Update `.claude/rules/01-database-standards.md` examples — the file is named `database-standards` (not `nocodb-standards`) precisely so it can be re-targeted. Adapt the MCP usage patterns to your backend's API.
5. Re-implement the v3 Link API pattern (`01-database-standards.md` Rule 8) if your backend has equivalent system-managed FK columns.

## Forking vs PRing

If your extension is broadly useful (a new region preset, a new fit-score adjustment pattern, a fix), open a PR — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

If your extension is specific to your situation (a custom employer extension, a heavily personalised insight library, a region preset for a market not in the original target list), keep it in your fork. The template is the foundation, not the whole house.
