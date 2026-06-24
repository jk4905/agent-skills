# dot-skill 工作流

使用这个指南，从 `dot-skill` 输出创建或刷新私有的 `yourself-skill`。

## 本地目录

```text
work/self-distillation/raw/
work/self-distillation/dot-skill-runs/
outputs/yourself-skill/
```

- 原始个人材料只放在 `work/self-distillation/raw/`。
- `dot-skill` 日志、生成的 Work Skill、生成的 Persona 和中间产物放在 `work/self-distillation/dot-skill-runs/`。
- `outputs/yourself-skill/` 里只保留已经校准、经过隐私审查的稳定规则。

## 入口检测

1. 先尝试 `dot-skill --help`。
2. 如果不可用，检查安装形态是否是 Claude Code skill；如果是，使用 `/create-colleague`。
3. 如果当前 shell 看不到任一入口，先定位实际安装入口，并在运行记录里写清楚，再继续。

## 蒸馏设置

- Family：`colleague`
- 目标：工作分身 / 工作判断方式
- 原始输入优先级：
  1. 长文和决策记录
  2. 工作沟通
  3. PR review 和技术反馈
  4. 用户自己写过的 prompt
  5. 日常聊天
  6. 主观自我描述

## 运行记录模板

```markdown
### YYYY-MM-DD run

- 使用入口：
- dot-skill 版本或安装来源：
- Family：
- 包含的原始材料批次：
- 生成产物：
- 已知缺口：
- 后续需要校准：
```

## 合并规则

- 把生成的人格特征改写成可执行规则。
- 只保留有支撑的稳定事实。
- 不确定观察先移到 `corrections.md` 或 `source-map.md`。
- 除非用户明确批准，否则不要把原始引文放进最终 skill。
- 永远不要包含凭证、私人身份标识、私人关系细节、健康信息、金融信息或私密聊天日志。

## 刷新规则

- 小修：先更新 `corrections.md`，如果高置信，再更新目标 reference。
- 中等更新：手动合并新的材料批次。
- 大版本更新：重新运行 `dot-skill`，与当前 references 对比后再谨慎合并。
