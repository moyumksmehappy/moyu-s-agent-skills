---
name: skill-scaffolder
description: 创建符合标准规范的 Agent Skill 脚手架。当用户需要新建技能、初始化技能目录、生成技能模板或咨询 Skill 规范时触发。
---

# Skill Scaffolder

Agent 创建 Skill 的权威规范文档。

---

## 一、Skill 规范概览

### 1.1 核心概念

Skill 是赋予 Agent 特定能力的模块化指令包。采用**渐进式披露**机制：

| 加载层级 | 时机 | 内容 |
|----------|------|------|
| **层级 1** | Agent 启动 | 仅加载 `name` + `description`（用于意图识别） |
| **层级 2** | 技能命中 | 加载 `SKILL.md` 正文（获取执行指令） |
| **层级 3** | 按需调用 | 读取附属文件或执行脚本（精简上下文占用） |

### 1.2 目录结构

```
<skill-name>/
├── SKILL.md              # [必需] 主指令文件
├── scripts/              # [可选] 可执行脚本
├── references/           # [可选] 参考文档
├── examples/             # [可选] 使用示例
└── assets/               # [可选] 资源文件
```

> [!IMPORTANT]
> 核心规则放 SKILL.md，详细资料放附属文件，实用逻辑放脚本执行（不预加载）。

---

## 二、SKILL.md 文件规范

### 2.1 YAML Frontmatter 元数据

#### 必需字段

| 字段 | 必需 | 作用 | 约束 |
|------|------|------|------|
| `name` | ✅ | 唯一标识，小写+连字符 | `^[a-z0-9-]+$`，1-64 字符 |
| `description` | ✅ | **触发条件**（最重要） | 1-1024 字符，禁止 XML |

#### 可选字段

| 字段 | 必需 | 作用 |
|------|------|------|
| `allowed-tools` | ❌ | 限制可用工具（如 `[bash, read_file]`） |
| `model` | ❌ | 指定模型（如 `claude-3-opus`） |
| `context` | ❌ | `fork` = 独立上下文 |
| `agent` | ❌ | fork 时使用的子代理 |
| `hooks` | ❌ | Skill 生命周期钩子 |
| `user-invocable` | ❌ | 是否显示在菜单（默认 `true`） |
| `license` | ❌ | 许可证 |
| `version` | ❌ | 语义化版本号 |

**示例：**

```yaml
---
name: excel-handler
description: 处理 Excel 文件。当用户需要读取、分析或转换电子表格时触发。
allowed-tools: [bash, read_file, write_file]
model: claude-3-sonnet
context: fork
user-invocable: true
version: 1.0.0
---
```

### 2.2 Markdown 正文（推荐结构）

```markdown
# 技能标题

一句话概述。

## Instructions

1. **步骤一**：具体指令
2. **步骤二**：具体指令

## Examples

**User:** 用户输入示例
**Agent:** 预期响应

## Guidelines

- 规则或约束
```

---

## 三、Agent 执行指令

当用户请求创建 Skill 时，按以下步骤执行：

### 步骤 1: 收集信息

向用户确认：

| 字段 | 必需 | 验证规则 |
|------|------|----------|
| `name` | ✅ | 正则 `^[a-z0-9-]+$`，1-64 字符 |
| `description` | ✅ | 1-1024 字符，无 XML 标签 |
| `user-guidelines` | ❌ | 用户核心准则（见第五节） |

### 步骤 2: 验证输入

- `name` 不符合规则 → 拒绝并提示修正
- `description` 含 XML 或超长 → 拒绝并提示修正

### 步骤 3: 预设用户核心准则

> [!TIP]
> 询问用户是否有特定的准则需要在 Skill 中预设，记录到 `## User Guidelines` 章节。

常见准则类型：
- **输出风格**：如"不要详细代码，只描述逻辑"
- **格式偏好**：如"使用中文输出"
- **行为约束**：如"执行前必须确认"

### 步骤 4: 生成脚手架

在目标目录创建以下结构：

```
<name>/
├── SKILL.md          # 生成基础模板（含用户准则）
├── scripts/          # 创建空目录
└── examples/         # 创建空目录
```

### 步骤 5: 输出结果

1. 展示生成的目录结构
2. 提示下一步：编辑 `SKILL.md` 添加具体指令

---

## 四、最佳实践

### 4.1 Description 编写

> [!TIP]
> 包含**关键词触发条件**，帮助 Agent 准确识别使用场景。

| 类型 | 示例 |
|------|------|
| ✅ 好 | `用于处理 Excel (.xlsx) 文件，支持数据提取和格式转换。当用户需要导入、分析或转换电子表格时触发。` |
| ❌ 差 | `处理 Excel 文件` |

### 4.2 Instructions 编写

- 每步骤是**可执行动作**
- 标明**验证点**和失败处理
- 提供**典型示例**

### 4.3 文件组织

| 内容类型 | 存放位置 |
|----------|----------|
| 核心执行规则 | `SKILL.md` |
| 详细参考资料 | `references/` |
| 使用示例 | `examples/` |
| 可执行脚本 | `scripts/` |

---

## 五、用户核心准则

> [!IMPORTANT]
> 本章节记录用户对 Skill 创建的通用准则。Agent 在创建任何 Skill 时必须遵守。

### 5.1 内容准则

| 准则 | 说明 |
|------|------|
| **不要详细代码** | 只描述逻辑流程，具体实现交给 LLM |
| **保持简洁** | 避免冗余内容，核心规则优先 |
| **声明式优先** | 使用"做什么"而非"怎么做" |

### 5.2 格式准则

| 准则 | 说明 |
|------|------|
| **使用表格** | 规则较多时用表格组织 |
| **层级清晰** | 使用标题分层，避免过深嵌套 |
| **示例精简** | 每类场景 1-2 个典型示例即可 |

### 5.3 如何添加新准则

用户可随时告知新的准则，Agent 应：
1. 记录到本章节对应分类
2. 在后续创建 Skill 时自动遵守

---

## 六、示例

### 示例 1: 创建技能

**User:** 帮我创建一个 Excel 处理技能，名字叫 excel-handler

**Agent:**
1. 确认信息：
   - `name`: excel-handler ✅
   - `description`: 请提供功能描述（建议包含：功能、触发场景）
2. 是否有特定准则需要预设？

**User:** 用于读取和处理 Excel 文件数据，不需要额外准则

**Agent:** ✅ 已创建 `excel-handler/`

```
excel-handler/
├── SKILL.md
├── scripts/
└── examples/
```

下一步：编辑 `SKILL.md` 添加具体执行指令。

### 示例 2: 查询规范

**User:** Skill name 有什么要求？

**Agent:**
- 字符：仅限 `a-z`、`0-9`、`-`
- 长度：1-64 字符
- ✅ `excel-handler`、`api-v2`
- ❌ `Excel_Handler`（大写/下划线）、`api tester`（空格）

---

## 七、SKILL.md 模板

```markdown
---
name: your-skill-name
description: 描述技能功能和触发场景，包含关键词以帮助 Agent 识别。
---

# Skill 标题

一句话概述技能功能。

## Instructions

1. **步骤一**：执行指令
2. **步骤二**：执行指令

## Examples

**User:** 用户请求示例
**Agent:** 响应示例

## Guidelines

- 约束或规则

## User Guidelines

- 用户预设的特定准则
```

---

## 八、快速参考

| 项目 | 规范 |
|------|------|
| name | `^[a-z0-9-]+$`，1-64 字符 |
| description | 1-1024 字符，无 XML |
| 必需文件 | `SKILL.md` |
| 可选目录 | `scripts/`、`references/`、`examples/`、`assets/` |
| 存放位置 | `~/.claude/skills/`（全局）或 `.claude/skills/`（项目） |
| 可选元数据 | `allowed-tools`、`model`、`context`、`agent`、`hooks`、`user-invocable` |