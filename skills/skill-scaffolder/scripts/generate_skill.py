#!/usr/bin/env python3
"""
Skill Scaffolder Generator
==========================

生成符合标准规范的 Agent Skill 目录结构。

Usage:
    python generate_skill.py --name "skill-name" --description "技能描述"
    python generate_skill.py --name "skill-name" --description "技能描述" --output "./skills"

Author: Skill Scaffolder
"""
import argparse
import re
import sys
from pathlib import Path
from datetime import datetime


# =============================================================================
# 验证函数
# =============================================================================

def validate_name(name: str) -> tuple[bool, str]:
    """验证 skill name 是否符合规范"""
    if not name:
        return False, "Name 不能为空"
    
    if len(name) > 64:
        return False, f"Name 长度超过限制 (当前: {len(name)}, 最大: 64)"
    
    pattern = r'^[a-z0-9-]+$'
    if not re.match(pattern, name):
        return False, f"Name 只能包含小写字母、数字和连字符 (regex: {pattern})"
    
    return True, "OK"


def validate_description(description: str) -> tuple[bool, str]:
    """验证 description 是否符合规范"""
    if not description:
        return False, "Description 不能为空"
    
    if len(description) > 1024:
        return False, f"Description 长度超过限制 (当前: {len(description)}, 最大: 1024)"
    
    # 检查XML标签
    if re.search(r'<[^>]+>', description):
        return False, "Description 不能包含 XML 标签"
    
    return True, "OK"


# =============================================================================
# 模板生成
# =============================================================================

def generate_skill_md(name: str, description: str) -> str:
    """生成 SKILL.md 模板内容"""
    return f'''---
name: {name}
description: {description}
version: 1.0.0
---

# {name.replace("-", " ").title()}

{description}

## Instructions

当用户请求相关操作时，按以下步骤执行：

1. **步骤一**：
   - 子步骤说明
   - 验证条件

2. **步骤二**：
   - 子步骤说明

## Configuration

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `param1` | string | ✅ | - | 参数说明 |

## Examples

**User:** 用户请求示例

**Agent:** Agent 响应示例

## Error Handling

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 错误示例 | 原因说明 | 解决方法 |

## References

- 添加相关参考链接
'''


def generate_readme(name: str, description: str) -> str:
    """生成 examples/README.md 内容"""
    return f'''# {name} Examples

本目录包含 `{name}` 技能的使用示例。

## 示例列表

- 添加您的示例文件

## 如何使用

1. 查看示例文件
2. 根据示例修改参数
3. 参考 SKILL.md 获取完整指令
'''


# =============================================================================
# 主逻辑
# =============================================================================

def create_skill_scaffold(name: str, description: str, output_dir: Path) -> Path:
    """创建 skill 脚手架目录结构"""
    skill_dir = output_dir / name
    
    # 检查目录是否已存在
    if skill_dir.exists():
        raise FileExistsError(f"目录已存在: {skill_dir}")
    
    # 创建目录结构
    directories = [
        skill_dir,
        skill_dir / "scripts",
        skill_dir / "examples",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    # 生成文件
    files = {
        skill_dir / "SKILL.md": generate_skill_md(name, description),
        skill_dir / "examples" / "README.md": generate_readme(name, description),
        skill_dir / "scripts" / ".gitkeep": "# 在此添加辅助脚本\n",
    }
    
    for filepath, content in files.items():
        filepath.write_text(content, encoding="utf-8")
    
    return skill_dir


def main():
    parser = argparse.ArgumentParser(
        description='生成符合标准规范的 Agent Skill 目录结构',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python generate_skill.py --name "excel-handler" --description "用于处理 Excel 文件的技能"
  python generate_skill.py --name "api-tester" --description "API 测试工具" --output "./my-skills"
        '''
    )
    
    parser.add_argument(
        '--name', '-n',
        required=True,
        help='Skill 名称 (仅限小写字母、数字和连字符, 最大64字符)'
    )
    
    parser.add_argument(
        '--description', '-d',
        required=True,
        help='Skill 描述 (最大1024字符, 不能包含XML标签)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='.',
        help='输出目录路径 (默认: 当前目录)'
    )
    
    args = parser.parse_args()
    
    # 验证输入
    valid, msg = validate_name(args.name)
    if not valid:
        print(f"❌ Name 验证失败: {msg}", file=sys.stderr)
        return 1
    
    valid, msg = validate_description(args.description)
    if not valid:
        print(f"❌ Description 验证失败: {msg}", file=sys.stderr)
        return 1
    
    output_path = Path(args.output).resolve()
    
    if not output_path.exists():
        print(f"📁 创建输出目录: {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        skill_path = create_skill_scaffold(args.name, args.description, output_path)
        
        print(f"\n✅ Skill '{args.name}' 创建成功!")
        print(f"\n📂 目录结构:")
        print(f"   {skill_path.name}/")
        print(f"   ├── SKILL.md          # 主指令文件")
        print(f"   ├── scripts/          # 辅助脚本目录")
        print(f"   │   └── .gitkeep")
        print(f"   └── examples/         # 示例目录")
        print(f"       └── README.md")
        print(f"\n📍 完整路径: {skill_path}")
        print(f"\n🚀 下一步:")
        print(f"   1. 编辑 {skill_path.name}/SKILL.md 添加具体的执行指令")
        print(f"   2. 在 scripts/ 目录添加辅助脚本 (如需要)")
        print(f"   3. 在 examples/ 目录添加使用示例")
        
        return 0
        
    except FileExistsError as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        print(f"   提示: 如需覆盖，请先删除现有目录", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ 未知错误: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
