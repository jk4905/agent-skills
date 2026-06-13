---
name: llm-wiki-health-check
version: 1.0.0
description: "Periodic health check and audit of the LLM-WIKI vault. Detects structural drift, broken wikilinks, orphan entries, index desync, log rotation need, and raw/wiki/schema deviations. Report-only — no auto-fix without user confirmation. Can deliver report to Feishu on request."
metadata:
  requires: []
  trigger_warning: "Report-only: do NOT auto-fix anything without user confirmation."
---

# LLM-WIKI Health Check

Run periodically (e.g. weekly cron) to audit the vault's structural integrity and catalog accuracy.

## Vault Path

**Canonical path**: `/Users/kagami/Library/Mobile Documents/iCloud~md~obsidian/Documents/LLM-WIKI`
Do NOT read from `/Users/kagami/.hermes/llm-wiki` or any other path.

## Hard Boundaries

- **Report only**: Do NOT create, edit, move, or delete any files.
- **No shell/terminal for file writes**: Use MCP fs tools only.
- **No delegate_task subagents that create files**.
- Do not modify/delete files under `raw/` after initialization.
- Any fix must wait for explicit user confirmation.

## Audit Checklist

Run these checks in order. Report each result.

### 1. Directory Structure Compliance

Verify each domain has the required four subdirectories:

```
wiki/<domain>/sources
wiki/<domain>/entities
wiki/<domain>/concepts
wiki/<domain>/syntheses
```

Expected domains: `meta`, `_shared`, `personal`, `startup`, `investing`, `coding`.

Flag: any missing subdirectory or unexpected domain.

### 2. Page Count vs Index Entry Count

- Count `.md` files on disk (excluding `.gitkeep`)
- Count `[[wikilink]]` entries in `index.md`
- Report discrepancy (disk vs index)

### 3. Orphan Index Entries

Parse `index.md` wikilinks. For each entry `[[PageName]]`, check if `wiki/*/PageName.md` exists on disk. Flag any that don't resolve.

Common case: `[[market-reports]]` and `[[portfolio-reports]]` are directory-level entries (exist as directories under `syntheses/` with child files), not single pages. These are orphan wikilinks — fix by either creating a `README.md` directory index or removing the orphan entry from `index.md`.

### 4. Broken Wikilinks (Intra-vault)

Scan all `.md` files for `[[wikilink]]` patterns (skip external URLs `#` anchors). For each wikilink, verify the target file exists on disk.

Investing source pages (Patreon content) typically have zero internal wikilinks — this is normal. Focus checks on concept/synthesis/entity pages which are more likely to cross-link.

### 5. Frontmatter Integrity

Check all `.md` files:
- Must start with `---` (frontmatter opener)
- `domain:` field in frontmatter must match the actual directory path
- All required frontmatter fields present (`type`, `domain`, `created`, `updated`)

Flag files with missing frontmatter or domain mismatches.

### 6. log.md Health

- File size (flag if > 200KB, consider rotation)
- Entry count (`## [20` pattern count)
- Most recent entry timestamp (should be recent — within days)
- Format: must use `## [YYYY-MM-DD HH:MM]` header + `-` bullet entries

### 7. Structure Drift

Check for deviations from schema:
- Top-level `entities/`, `concepts/`, `comparisons/`, `queries/` directories (old layout — should be under `wiki/<domain>/...`)
- Files directly under `wiki/<domain>/` instead of in subdirectories
- Missing required files: `SCHEMA.md`, `CLAUDE.md`, `AGENTS.md`, `index.md`, `log.md`
- `raw/` modifications after initialization

### 8. lark-cli Version Check (for Feishu delivery)

Run `lark-cli --version` or `lark-cli im +chat-list --as bot`. If `_notice.update` appears in JSON output with version delta > 2, flag it and suggest `lark-cli update`.

## Report Format

```
## LLM-WIKI 每周体检报告

**体检时间**: YYYY-MM-DD
**Vault**: <canonical path>

### 📊 结构概览
[page counts, index counts, log size]

### ✅ 检查通过项
[items with ✅]

### ⚠️ 需要关注的项
[items with issues, specific file/page names]

### 📋 建议修复动作（待确认后执行）
| # | 修复项 | 操作内容 |
```

## Feishu Delivery

If the user asks to deliver the report to Feishu:
1. Pre-flight: `lark-cli im +chat-list --as bot` — empty list means bot has no groups
2. If empty, inform user the bot must be invited to a group before messages can be sent
3. Send report as text message via `lark-cli im +messages-send --as bot --chat-id <id> --msg-type text --content "<report>"`

## Trigger

- User asks "LLM-WIKI 体检", "每周 wiki 检查", "wiki audit", "check wiki health"
- Scheduled weekly cron job
- Any `[[wikilink]]` integrity question