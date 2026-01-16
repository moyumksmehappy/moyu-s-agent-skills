---
name: skill-scaffolder
description: 用于创建一个符合标准规范的 Agent Skill 基础架构。当用户需要新建一个智能体技能、初始化技能目录或生成技能模板时触发。
---

# Skill Scaffolder (技能脚手架)

## Instructions
当用户请求创建一个新的 Agent Skill 时，请按照以下步骤操作：

1.  **信息收集**：
    * 向用户确认新技能的 **name** (必须仅包含小写字母、数字和连字符，最大 64 字符)。
    * 向用户确认新技能的 **description** (简明扼要，说明功能和触发场景)。

2.  **验证**：
    * 检查 `name` 是否符合规范 (Regex: `^[a-z0-9-]+$`)。如果不符合，请拒绝并提示用户修正。
    * 确保 `description` 不包含 XML 标签。

3.  **执行生成**：
    * 使用以下命令运行生成脚本。确保将 `<NAME>` 和 `<DESCRIPTION>` 替换为实际值。
    
    ```bash
    python scripts/generate_skill.py --name "<NAME>" --description "<DESCRIPTION>"
    ```

4.  **反馈**：
    * 脚本执行成功后，向用户展示生成的目录结构，并告知用户下一步可以在新生成的 `SKILL.md` 中补充具体的指令。

## Examples

**User:** 请帮我创建一个用来处理 Excel 文件的技能，名字叫 excel-handler。
**Agent:** 好的，正在为您创建标准技能结构...
*(Agent executes: `python scripts/generate_skill.py --name "excel-handler" --description "用于读取和处理 Excel (.xlsx) 文件数据的技能。"`)*
**Agent:** 技能 `excel-handler` 已创建成功！包含标准的 SKILL.md 和 scripts 目录。