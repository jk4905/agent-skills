---
name: llm-wiki-ingest-gate
version: 1.0.0
description: "Use when kagami sends material from Feishu, URLs, files, notes, stock items, startup ideas, or asks whether something should enter LLM-WIKI. Classifies incoming material, proposes wiki action, and waits for explicit ingest confirmation before writing."
metadata:
  requires: []
  trigger_warning: "DO NOT write to LLM-WIKI until user confirms with 'ingest'. Auto-write on message intake is disabled."
---

# LLM-WIKI Ingest Gate

## Vault Path

**Canonical path**: `/Users/kagami/Library/Mobile Documents/iCloud~md~obsidian/Documents/LLM-WIKI`

When reading schema/context, only read from the canonical vault:
- `SCHEMA.md` — data model schema
- `CLAUDE.md` — agent instructions and rules
- `index.md` — wiki structure/map
- `log.md` — recent activity log (tail)

**Do NOT** read from `/Users/kagami/.hermes/llm-wiki` or any other path.

## Intake Classification

Every incoming message is classified into ONE of:

| Type | Description | Typical Action |
|------|-------------|----------------|
| `wiki` | URL, article, video, file as LLM-WIKI candidate | Propose ingest |
| `investing` | Stock ticker, company, fund, market data | Watchlist research |
| `startup` | Startup idea, opportunity, competitor analysis | Opportunity review |
| `coding` | Programming task, code review, debug request | Route to appropriate skill |
| `personal` | Life question, non-work thought | Personal growth or skip |
| `feishu` | Feishu message forwarded to agent | Classify embedded content |

## Candidate Brief Format

When generating a candidate brief for wiki ingestion, use this structure:

```markdown
# AI/Agent 候选简报

## 候选材料
- **标题**:
- **来源**:
- **为什么可能值得收录**:
- **建议 domain**:
- **风险或低质量信号**:

## 建议操作
- ingest      → 收录到 LLM-WIKI（高质量，来源可靠）
- 深入分析    → 需要交叉验证后再决定
- 跳过        → 质量不足或来源不可靠
```

**Ingest criteria**:
- Publicly accessible source (no auth required for reading)
- Content is factual, not fabricated
- Clear domain relevance to AI/Agent/LLM topics
- Source is citable and stable

**Skip criteria**:
- Internal-only or paywalled source
- Unverifiable claims ("internal document says X")
- Low-quality summary sites or AI-generated content farms
- Fabricated or hallucinated content

## Hard Boundaries

1. **No auto-write**: Never write to LLM-WIKI without explicit `ingest` confirmation from user
2. **No shell/terminal for file writes**: Use MCP fs tools or skill tools only
3. **No委派会创建文件的子任务**: delegate_task with file-creation subagents is forbidden
4. **No modify/delete files under `raw/`** after initialization
5. **No writing secrets, tokens, credentials to wiki notes**

## Ingest Execution (after user confirms `ingest`)

1. Read canonical vault's `index.md` and `log.md` (tail 50)
2. Determine target domain from `wiki/<domain>/` structure
3. Write source page under `wiki/<domain>/sources/<source-name>.md`
4. Update `index.md` with new entry
5. Append `log.md` with timestamp and action

## Feishu Delivery Note

If the user asks to deliver the candidate brief to Feishu:
- Bot must be a member of the target group chat first
- Pre-flight: run `lark-cli im +chat-list --as bot` — empty list means bot has no groups
- If empty, inform user the bot must be invited to a group before messages can be sent
- lark-cli version check: run `lark-cli --version` — suggest update if >2 versions behind

## Trigger Phrases

- "帮我收录"
- "要不要放进 wiki"
- "这个值得入 wiki 吗"
- "ingest"
- "收录到 LLM-WIKI"
- Forwarded Feishu/WeChat messages with URLs or files
- YouTube/Bilibili URLs → propose transcript ingest