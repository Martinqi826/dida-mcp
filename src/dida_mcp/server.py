"""
滴答清单 (Dida365) MCP Server

手动实现 MCP 协议（JSON-RPC over stdio），不依赖 mcp 包。
兼容 Python 3.9+。

提供以下工具：
- 项目（清单）管理：列出、创建、删除
- 任务管理：创建、更新、完成、删除
- 高级查询：今日到期、已过期、按优先级、搜索
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any, Dict, List, Optional

from .auth import DidaAuth
from .client import DidaClient

logger = logging.getLogger("dida-mcp")

# 全局客户端（延迟初始化）
_client: Optional[DidaClient] = None


def get_client() -> DidaClient:
    """获取或初始化滴答清单客户端"""
    global _client
    if _client is None:
        auth = DidaAuth()
        _client = DidaClient(auth)
    return _client


def format_task(task: Dict) -> str:
    """格式化任务为可读文本"""
    priority_map = {0: "无", 1: "低", 3: "中", 5: "高"}
    status = "✅" if task.get("status", 0) != 0 else "⬜"
    priority = priority_map.get(task.get("priority", 0), "无")
    title = task.get("title", "无标题")
    project_name = task.get("_projectName", "")
    due_date = task.get("dueDate", "")
    tags = task.get("tags", [])

    lines = [f"{status} {title}"]
    if project_name:
        lines.append(f"   📁 清单: {project_name}")
    if due_date:
        lines.append(f"   📅 截止: {due_date}")
    if priority != "无":
        lines.append(f"   🔺 优先级: {priority}")
    if tags:
        lines.append(f"   🏷️  标签: {', '.join(tags)}")

    task_id = task.get("id", "")
    project_id = task.get("projectId", task.get("_projectId", ""))
    if task_id:
        lines.append(f"   🆔 任务ID: {task_id}")
    if project_id:
        lines.append(f"   📂 项目ID: {project_id}")

    return "\n".join(lines)


def format_project(project: Dict) -> str:
    """格式化项目为可读文本"""
    name = project.get("name", "无名称")
    project_id = project.get("id", "")
    color = project.get("color", "")
    kind = project.get("kind", "")

    lines = [f"📁 {name}"]
    if project_id:
        lines.append(f"   🆔 ID: {project_id}")
    if color:
        lines.append(f"   🎨 颜色: {color}")
    if kind:
        lines.append(f"   📋 类型: {kind}")

    return "\n".join(lines)


# ==================== 工具定义 ====================

TOOLS = [
    {
        "name": "get_projects",
        "description": "获取所有项目（清单）列表。返回所有项目的名称、ID、颜色等信息。",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_project_detail",
        "description": "获取指定项目的详细信息及其所有任务。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "项目ID"}
            },
            "required": ["project_id"],
        },
    },
    {
        "name": "create_project",
        "description": "创建新的项目（清单）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "项目名称"},
                "color": {
                    "type": "string",
                    "description": "项目颜色（可选，如 '#FF6347'）",
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "delete_project",
        "description": "删除指定的项目（清单）。⚠️ 此操作不可恢复。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "要删除的项目ID",
                }
            },
            "required": ["project_id"],
        },
    },
    {
        "name": "get_all_tasks",
        "description": "获取所有未完成的任务列表，包含任务的标题、截止日期、优先级、所属清单等信息。",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "create_task",
        "description": "创建新任务。可以指定标题、所属项目、截止日期、优先级、标签等。不指定项目则放入收集箱。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "任务标题"},
                "project_id": {
                    "type": "string",
                    "description": "项目ID（可选，不填则放入收集箱）",
                },
                "content": {
                    "type": "string",
                    "description": "任务内容/描述（可选）",
                },
                "start_date": {
                    "type": "string",
                    "description": "开始日期（可选，ISO 8601格式，如 '2026-03-15T09:00:00+0800'）",
                },
                "due_date": {
                    "type": "string",
                    "description": "截止日期（可选，ISO 8601格式，如 '2026-03-15T18:00:00+0800'）",
                },
                "priority": {
                    "type": "integer",
                    "description": "优先级（0=无, 1=低, 3=中, 5=高）",
                    "enum": [0, 1, 3, 5],
                },
                "is_all_day": {
                    "type": "boolean",
                    "description": "是否全天任务（可选）",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "标签列表（可选）",
                },
            },
            "required": ["title"],
        },
    },
    {
        "name": "update_task",
        "description": "更新已有任务的信息，如标题、截止日期、优先级等。需要提供 task_id 和 project_id。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "任务ID"},
                "project_id": {"type": "string", "description": "项目ID"},
                "title": {"type": "string", "description": "新标题（可选）"},
                "content": {"type": "string", "description": "新内容（可选）"},
                "due_date": {
                    "type": "string",
                    "description": "新截止日期（可选，ISO 8601格式）",
                },
                "priority": {
                    "type": "integer",
                    "description": "新优先级（0=无, 1=低, 3=中, 5=高）",
                    "enum": [0, 1, 3, 5],
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "新标签列表（可选）",
                },
            },
            "required": ["task_id", "project_id"],
        },
    },
    {
        "name": "complete_task",
        "description": "将指定任务标记为已完成。需要提供 task_id 和 project_id。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "任务ID"},
                "project_id": {"type": "string", "description": "项目ID"},
            },
            "required": ["task_id", "project_id"],
        },
    },
    {
        "name": "delete_task",
        "description": "删除指定任务。⚠️ 此操作不可恢复。需要提供 task_id 和 project_id。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "任务ID"},
                "project_id": {"type": "string", "description": "项目ID"},
            },
            "required": ["task_id", "project_id"],
        },
    },
    {
        "name": "get_tasks_due_today",
        "description": "获取今天到期的所有任务。",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_overdue_tasks",
        "description": "获取所有已过期（逾期）的任务。",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_tasks_by_priority",
        "description": "按优先级获取任务。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "priority": {
                    "type": "integer",
                    "description": "优先级（0=无, 1=低, 3=中, 5=高）",
                    "enum": [0, 1, 3, 5],
                }
            },
            "required": ["priority"],
        },
    },
    {
        "name": "search_tasks",
        "description": "搜索任务。可以按标题、内容、标签进行模糊搜索。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"}
            },
            "required": ["query"],
        },
    },
]


# ==================== 工具调用分发 ====================


def dispatch_tool(name: str, args: Dict[str, Any]) -> str:
    """分发工具调用"""
    client = get_client()

    # ===== 项目管理 =====
    if name == "get_projects":
        projects = client.get_projects()
        if not projects:
            return "📭 没有找到任何项目。"
        lines = ["📋 共 %d 个项目：\n" % len(projects)]
        for p in projects:
            lines.append(format_project(p))
            lines.append("")
        return "\n".join(lines)

    elif name == "get_project_detail":
        data = client.get_project_with_tasks(args["project_id"])
        project = data.get("project", data)
        tasks = data.get("tasks", [])

        lines = ["📁 项目详情：\n"]
        lines.append("   名称: %s" % project.get("name", "未知"))
        lines.append("   ID: %s" % project.get("id", ""))
        lines.append("\n📝 任务列表（%d 个）：\n" % len(tasks))

        for task in tasks:
            task["_projectId"] = args["project_id"]
            lines.append(format_task(task))
            lines.append("")

        if not tasks:
            lines.append("   （空）")

        return "\n".join(lines)

    elif name == "create_project":
        project = client.create_project(
            name=args["name"],
            color=args.get("color"),
        )
        return "✅ 项目创建成功！\n\n%s" % format_project(project)

    elif name == "delete_project":
        client.delete_project(args["project_id"])
        return "✅ 项目 %s 已删除。" % args["project_id"]

    # ===== 任务管理 =====
    elif name == "get_all_tasks":
        tasks = client.get_all_tasks()
        if not tasks:
            return "🎉 没有待办任务，一切都完成了！"
        lines = ["📝 共 %d 个待办任务：\n" % len(tasks)]
        for task in tasks:
            lines.append(format_task(task))
            lines.append("")
        return "\n".join(lines)

    elif name == "create_task":
        task = client.create_task(
            title=args["title"],
            project_id=args.get("project_id"),
            content=args.get("content"),
            start_date=args.get("start_date"),
            due_date=args.get("due_date"),
            priority=args.get("priority", 0),
            is_all_day=args.get("is_all_day"),
            tags=args.get("tags"),
        )
        return "✅ 任务创建成功！\n\n%s" % format_task(task)

    elif name == "update_task":
        update_fields = {
            k: v
            for k, v in args.items()
            if k not in ("task_id", "project_id") and v is not None
        }
        task = client.update_task(
            task_id=args["task_id"],
            project_id=args["project_id"],
            **update_fields,
        )
        return "✅ 任务已更新！\n\n%s" % format_task(task)

    elif name == "complete_task":
        client.complete_task(
            project_id=args["project_id"],
            task_id=args["task_id"],
        )
        return "✅ 任务 %s 已标记为完成！" % args["task_id"]

    elif name == "delete_task":
        client.delete_task(
            project_id=args["project_id"],
            task_id=args["task_id"],
        )
        return "✅ 任务 %s 已删除。" % args["task_id"]

    # ===== 高级查询 =====
    elif name == "get_tasks_due_today":
        tasks = client.get_tasks_due_today()
        if not tasks:
            return "🎉 今天没有到期的任务！"
        lines = ["📅 今天到期的任务（%d 个）：\n" % len(tasks)]
        for task in tasks:
            lines.append(format_task(task))
            lines.append("")
        return "\n".join(lines)

    elif name == "get_overdue_tasks":
        tasks = client.get_overdue_tasks()
        if not tasks:
            return "✅ 没有逾期任务！"
        lines = ["⚠️ 逾期任务（%d 个）：\n" % len(tasks)]
        for task in tasks:
            lines.append(format_task(task))
            lines.append("")
        return "\n".join(lines)

    elif name == "get_tasks_by_priority":
        priority_map = {0: "无", 1: "低", 3: "中", 5: "高"}
        priority = args["priority"]
        tasks = client.get_tasks_by_priority(priority)
        label = priority_map.get(priority, str(priority))
        if not tasks:
            return "📋 没有优先级为「%s」的任务。" % label
        lines = ["🔺 优先级「%s」的任务（%d 个）：\n" % (label, len(tasks))]
        for task in tasks:
            lines.append(format_task(task))
            lines.append("")
        return "\n".join(lines)

    elif name == "search_tasks":
        tasks = client.search_tasks(args["query"])
        if not tasks:
            return "🔍 没有找到包含「%s」的任务。" % args["query"]
        lines = [
            "🔍 搜索「%s」找到 %d 个任务：\n" % (args["query"], len(tasks))
        ]
        for task in tasks:
            lines.append(format_task(task))
            lines.append("")
        return "\n".join(lines)

    else:
        return "❌ 未知工具: %s" % name


# ==================== MCP JSON-RPC over stdio ====================


def send_response(response: Dict):
    """通过 stdout 发送 JSON-RPC 响应"""
    msg = json.dumps(response, ensure_ascii=False)
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def handle_request(request: Dict) -> Optional[Dict]:
    """处理 JSON-RPC 请求"""
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params", {})

    # initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False},
                },
                "serverInfo": {
                    "name": "dida-mcp",
                    "version": "1.0.0",
                },
            },
        }

    # notifications (no id) - don't send response
    elif method == "notifications/initialized":
        return None

    elif method == "notifications/cancelled":
        return None

    # tools/list
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS},
        }

    # tools/call
    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        try:
            result_text = dispatch_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {"type": "text", "text": result_text}
                    ],
                    "isError": False,
                },
            }
        except Exception as e:
            error_text = "❌ 调用工具 '%s' 失败: %s" % (tool_name, str(e))
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {"type": "text", "text": error_text}
                    ],
                    "isError": True,
                },
            }

    # ping
    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {},
        }

    # unknown method
    else:
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": "Method not found: %s" % method,
                },
            }
        return None


def run_server():
    """启动 MCP Server（stdio 模式）"""
    sys.stderr.write("🚀 滴答清单 MCP Server 已启动\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            sys.stderr.write("⚠️ 收到无效的 JSON: %s\n" % line[:100])
            sys.stderr.flush()
            continue

        response = handle_request(request)
        if response is not None:
            send_response(response)
