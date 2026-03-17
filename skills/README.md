# Skills

Skills extend the agent with extra system-prompt text. Add a subfolder per skill with a `skill.yaml` file.

## Format

**skill.yaml** (or `skill.yml`):

```yaml
name: my_skill
description: Optional short description
system_prompt: |
  Extra instructions appended to the agent's system prompt.
  Use this for domain rules, preferred notation, or task-specific guidance.
```

- **name**: Identifier for the skill (used in logs).
- **description**: Optional; for documentation only.
- **system_prompt**: Required. This text is appended to the base agent prompt; all enabled skills are merged in alphabetical order by folder name.

## Example

See `memristor_basics/skill.yaml` for a minimal skill that adds terminology and trade-off guidance.

## Enabling skills

Skills are loaded automatically from the `skills/` directory (or from the path set in `.env` as `SKILLS_DIR`). Add or remove skill folders to change which skills are active.
