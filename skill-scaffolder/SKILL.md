---
name: skill-scaffolder
description: 创建符合标准规范的 Agent Skill 脚手架。当用户需要新建技能、初始化技能目录、生成技能模板或咨询技能创建规范时触发。
---

# Skill Scaffolder (技能脚手架生成器)

这是 Agent 创建新技能的权威参考文档。包含完整的规范定义、最佳实践和生成工具。

---

## 一、Skill 规范定义

### 1.1 目录结构规范

每个 Skill **必须**遵循以下目录结构：

```
<skill-name>/
├── SKILL.md              # [必需] 主指令文件
├── scripts/              # [可选] 辅助脚本目录
│   └── *.py / *.js / ... # 扩展 Agent 能力的脚本
├── references/           # [可选] 参考资料目录
│   └── *.md / *.txt      # 技术文档、API 规范等
├── examples/             # [可选] 示例目录
│   └── *.md / *.json     # 使用示例、参考实现
└── assets/               # [可选] 资源目录
    └── *.png / *.json    # 模板、配置、图像等资源
```

### 1.2 SKILL.md 文件规范

#### 1.2.1 必需组成部分

**YAML Frontmatter (必需)**

```yaml
---
name: skill-name           # 必需: 1-64字符，仅限小写字母、数字、连字符
description: 技能描述       # 必需: 1-1024字符，说明功能和触发场景
---
```

| 字段 | 规则 | 示例 |
|------|------|------|
| `name` | `^[a-z0-9-]+$`，1-64字符 | `excel-handler`, `api-tester` |
| `description` | 1-1024字符，禁止XML标签 | 用于处理Excel文件的技能 |

#### 1.2.2 可选 Frontmatter 字段

```yaml
---
name: my-skill
description: 技能描述
license: MIT                        # 可选: 许可证
version: 1.0.0                      # 可选: 语义化版本号
compatibility:                      # 可选: 环境要求
  os: [windows, linux, macos]
  python: ">=3.8"
  node: ">=18.0"
metadata:                           # 可选: 自定义元数据
  author: your-name
  category: development-tools
  tags: [excel, data, automation]
---
```

#### 1.2.3 Markdown 正文结构

遵循**渐进式披露**原则（Progressive Disclosure）：Agent 仅在需要时才加载详细内容。

```markdown
# 技能名称

简短的技能总体说明（1-2句话）。

## Instructions

明确的执行步骤，使用编号列表：

1. **步骤一标题**：
   - 子步骤说明
   - 验证条件

2. **步骤二标题**：
   - 子步骤说明

## Configuration (可选)

配置参数说明。

## Examples

**User:** 用户输入示例
**Agent:** Agent 响应示例

## Error Handling (可选)

常见错误及处理方式。

## References (可选)

相关链接和参考资料。
```

### 1.3 脚本规范

#### 1.3.1 脚本设计原则

| 原则 | 说明 |
|------|------|
| **幂等性** | 重复执行产生相同结果 |
| **原子性** | 要么全部成功，要么全部回滚 |
| **错误处理** | 提供清晰的错误信息和退出码 |
| **无副作用输入验证** | 在执行前验证所有输入 |

#### 1.3.2 Python 脚本模板

```python
#!/usr/bin/env python3
"""
脚本名称: <name>
功能描述: <description>
使用方法: python <script>.py --arg1 value1 --arg2 value2
"""
import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='脚本功能描述')
    parser.add_argument('--name', required=True, help='必需参数说明')
    parser.add_argument('--output', default='./', help='可选参数说明')
    args = parser.parse_args()
    
    try:
        # 执行逻辑
        print(f"✅ 成功: {args.name}")
        return 0
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

---

## 二、Agent 执行指令

当用户请求创建新 Skill 时，执行以下步骤：

### 步骤 1: 信息收集

向用户确认以下信息：

| 字段 | 必需 | 验证规则 |
|------|------|----------|
| **name** | ✅ | `^[a-z0-9-]+$`，1-64字符 |
| **description** | ✅ | 1-1024字符，无XML标签 |
| **category** | ❌ | 建议分类（见 2.4） |

**收集问题模板：**
> 请提供新技能的信息：
> 1. **name** (技能名称): 仅限小写字母、数字和连字符
> 2. **description** (功能描述): 简明说明功能和触发场景
> 3. **category** (可选): 技能分类

### 步骤 2: 输入验证

```python
# Name 验证
import re
def validate_name(name: str) -> bool:
    pattern = r'^[a-z0-9-]+$'
    return bool(re.match(pattern, name)) and 1 <= len(name) <= 64

# Description 验证
def validate_description(desc: str) -> bool:
    has_xml = bool(re.search(r'<[^>]+>', desc))
    return not has_xml and 1 <= len(desc) <= 1024
```

如验证失败，拒绝并提示用户修正。

### 步骤 3: 执行生成

运行生成脚本：

```bash
python "<SKILL_SCAFFOLDER_PATH>/scripts/generate_skill.py" \
    --name "<NAME>" \
    --description "<DESCRIPTION>" \
    --output "<OUTPUT_PATH>"
```

**参数说明：**
- `--name`: 技能名称
- `--description`: 技能描述
- `--output`: 输出目录路径（默认当前目录）

### 步骤 4: 反馈与引导

生成完成后，向用户展示：

1. **生成的目录结构**
2. **下一步建议**：
   - 编辑 `SKILL.md` 添加具体指令
   - 如需脚本能力，在 `scripts/` 中添加
   - 参考本规范完善技能

---

## 三、技能分类参考

| 分类 | 说明 | 示例 |
|------|------|------|
| `data-processing` | 数据处理与转换 | excel-handler, csv-parser |
| `code-generation` | 代码生成与重构 | api-generator, test-writer |
| `testing` | 测试与验证 | unit-tester, e2e-runner |
| `documentation` | 文档生成与管理 | doc-generator, readme-maker |
| `devops` | 部署与运维 | docker-helper, ci-config |
| `api-integration` | API 集成与调用 | rest-client, graphql-helper |
| `file-management` | 文件操作与管理 | file-organizer, backup-tool |
| `automation` | 工作流自动化 | task-scheduler, batch-runner |

---

## 四、最佳实践

### 4.1 Description 编写指南

> [!TIP]
> 好的 description 应该包含**关键词触发条件**，帮助 Agent 准确识别何时使用该技能。

**✅ 好的示例：**
```yaml
description: 用于读取、解析和处理 Excel (.xlsx, .xls) 文件数据的技能。当用户需要导入Excel、分析电子表格或转换Excel格式时触发。
```

**❌ 差的示例：**
```yaml
description: 处理 Excel 文件
```

### 4.2 Instructions 编写原则

1. **明确具体**：每个步骤都应该是可执行的动作
2. **验证点清晰**：标明何时需要验证，失败时如何处理
3. **示例丰富**：提供典型输入/输出示例
4. **错误处理**：说明常见错误的解决方案

### 4.3 渐进式披露

| 加载时机 | 内容 | 目的 |
|----------|------|------|
| Agent 启动 | YAML Frontmatter | 快速索引技能 |
| 技能激活 | SKILL.md 正文 | 获取执行指令 |
| 按需加载 | scripts/, references/ | 减少上下文占用 |

---

## 五、示例

### 示例 1: 创建简单技能

**User:** 请帮我创建一个用来处理 Excel 文件的技能，名字叫 excel-handler。

**Agent:** 好的，我需要确认一下信息：
- **name**: `excel-handler` ✅ 格式正确
- **description**: 请提供功能描述，建议包含：功能、文件类型、触发场景

**User:** 用于读取和处理 Excel (.xlsx) 文件数据，支持数据提取和格式转换。

**Agent:** 正在为您创建技能结构...
```
python scripts/generate_skill.py --name "excel-handler" --description "用于读取和处理 Excel (.xlsx) 文件数据的技能，支持数据提取和格式转换。"
```

**Agent:** ✅ 技能 `excel-handler` 已创建成功！

```
excel-handler/
├── SKILL.md              # 主指令文件（已生成基础模板）
├── scripts/              # 脚本目录
└── examples/             # 示例目录
```

**下一步建议：**
1. 编辑 `excel-handler/SKILL.md` 添加具体的执行指令
2. 如需Python处理能力，可在 `scripts/` 中添加脚本

### 示例 2: 查询规范

**User:** Skill 的 name 有什么格式要求？

**Agent:** Skill name 的格式要求如下：
- **字符限制**：仅限小写字母 (a-z)、数字 (0-9) 和连字符 (-)
- **正则表达式**：`^[a-z0-9-]+$`
- **长度限制**：1-64 个字符

**有效示例：**
- ✅ `excel-handler`
- ✅ `api-tester-v2`
- ✅ `data2json`

**无效示例：**
- ❌ `Excel_Handler` (大写字母、下划线)
- ❌ `api tester` (空格)
- ❌ `数据处理` (非ASCII字符)

---

## 六、附录

### A. 完整 SKILL.md 模板

```markdown
---
name: your-skill-name
description: 简明扼要描述技能功能和触发场景。包含关键词以帮助Agent识别。
version: 1.0.0
license: MIT
---

# Your Skill Name (技能中文名)

一句话说明这个技能做什么。

## Instructions

1. **步骤一**：
   - 详细说明
   - 验证条件

2. **步骤二**：
   - 详细说明

## Configuration

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `param1` | string | ✅ | - | 参数说明 |
| `param2` | boolean | ❌ | `false` | 参数说明 |

## Examples

**User:** 用户请求示例
**Agent:** Agent 响应示例

## Error Handling

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| Error1 | 原因说明 | 解决方法 |

## References

- [相关文档](url)
```

### B. 快速参考卡片

| 项目 | 规范 |
|------|------|
| Name | `^[a-z0-9-]+$`, 1-64字符 |
| Description | 1-1024字符, 无XML |
| 必需文件 | `SKILL.md` |
| 可选目录 | `scripts/`, `references/`, `examples/`, `assets/` |