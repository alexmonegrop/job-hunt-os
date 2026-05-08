# Security policy

Thanks for taking the time to disclose responsibly.

## Reporting a vulnerability

If you find a security issue **in the template itself** (not in a fork or in your own deployment), please **do not open a public issue**.

Instead:

1. Open a [GitHub Security Advisory](https://github.com/alexmonegrop/job-hunt-os/security/advisories/new) (preferred — private, structured, has a CVE workflow).
2. Or email the maintainer directly at the address in the GitHub profile commit history.

I aim to acknowledge reports within 5 business days and to ship a fix or mitigation within 30 days for confirmed issues, sooner for severe ones.

## What's in scope

This template ships:

- Rule / skill / operating-procedure markdown — these are *prompts* to an AI agent, not executable code. Prompt injection or instruction-bypass risks belong here.
- Python utilities under `tools/` — input validation, file handling, dependency hygiene.
- A Docker Compose stack under `infrastructure/` — container configuration, default ports, network exposure, secrets handling.
- The schema at `infrastructure/init-db/02-jobhunt-schema.sql`.

## What's NOT in scope

- **Your own deployment.** Once you fork or instantiate the template, the secrets you put in `.env` and the data you load into NocoDB are entirely your responsibility. The template documents the gitignore patterns, the PAT-recovery flow, and the credential helpers — but it cannot enforce them on your machine.
- **Upstream dependencies.** NocoDB, Postgres, Docker, the npm MCP packages, Claude Code, and Python packages have their own disclosure channels. Please report vulnerabilities in those projects to those projects.
- **AI model behaviour.** The agent calls into Claude (or any compatible model). Hallucinations, jailbreaks, or refusals are model-vendor concerns.

## Secrets handling — the bare minimum a fork should do

If you fork this template and run it against real data, please:

1. **Never commit `.env`, `infrastructure/.env`, your real `master-experience.yaml`, your `applications/{slug}/`, `outreach/{slug}/`, or `interviews/{slug}/` directories.** They are gitignored at the user level — keep it that way.
2. **Rotate any credential that ever touches a tracked file or a public Slack/Discord/transcript.** Treat exposure as compromise.
3. **Don't re-paste your `li_at` LinkedIn cookie, your NocoDB API token, or your GitHub PAT into chat / issue / PR descriptions.** Use the Security Advisory channel for sensitive contexts.
4. **Run `tools/setup/init-nocodb.py` against a *local* NocoDB instance**, not a production cloud instance, until you've tailored the schema to your needs.

## Known security considerations (template-level)

- The Docker Compose stack ships `NC_ALLOW_LOCAL_EXTERNAL_DBS=true` to let NocoDB reach the in-network `postgres` host. This is appropriate for local dev. **Do not expose the stack to the public internet without changing this flag and the default credentials.**
- The `--auto-bootstrap` flag generates a default admin `admin@local.test`. **Change this if you ever expose the NocoDB UI to anything beyond `localhost`.**
- Playwright MCP, when configured with `--allow-unrestricted-file-access`, can read/write any file the user can. The same is true of any MCP that runs as the user. Audit your MCP config (`~/.claude.json`) before granting these capabilities to a new project.
