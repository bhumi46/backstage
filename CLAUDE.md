# CLAUDE.md

Guidance for Claude Code in this repo. Shared agent rules live in AGENTS.md and playbooks in SKILLS.md; both are imported here so there's a single source of truth.

@AGENTS.md
@SKILLS.md

## Claude-specific workflow

- **Follow [PLAN.md](PLAN.md) one step at a time.** Before starting, say which step/sub-step you're on. Don't start the next step until the current **Done when** checklist is fully ticked with evidence.
- Pick the matching playbook from SKILLS.md before writing code.
- Use plan mode for anything that touches more than one package or adds a template.
- Ask before: creating GitHub repos, pushing, opening PRs in sibling repos, or using real tokens. Those act on GitHub, not just locally.
- If `<owner>` hasn't been set yet, ask for it once and then use it everywhere.
- Never print, log or commit token values. Refer to them by env var name.
- When changing template output paths or catalog annotations, check they still match the sibling repos' layout in AGENTS.md.
- Record every new pinned version in `README.md` in the same change.
