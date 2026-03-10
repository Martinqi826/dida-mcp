# 滴答清单 (dida-mcp) — OpenClaw TOOLS.md 参考

> 将以下内容追加到你的 `~/.openclaw/workspace/TOOLS.md` 中，
> OpenClaw AI 就能通过 mcporter 调用滴答清单工具。

---

## 滴答清单 (dida-mcp)

通过 mcporter 接入的滴答清单 MCP Server。使用 `mcporter call` 命令调用。

### 可用工具 (13 个)

**项目管理：**
- `mcporter call dida-mcp.get_projects` — 获取所有项目列表
- `mcporter call dida-mcp.get_project_detail project_id=<id>` — 获取项目详情及任务
- `mcporter call dida-mcp.create_project name=<名称>` — 创建新项目（可选 color）
- `mcporter call dida-mcp.delete_project project_id=<id>` — 删除项目（不可恢复）

**任务管理：**
- `mcporter call dida-mcp.get_all_tasks` — 获取所有未完成任务
- `mcporter call dida-mcp.create_task title=<标题>` — 创建任务（可选 project_id, content, due_date, priority, tags）
- `mcporter call dida-mcp.update_task task_id=<id> project_id=<id>` — 更新任务（可选 title, content, due_date, priority, tags）
- `mcporter call dida-mcp.complete_task task_id=<id> project_id=<id>` — 完成任务
- `mcporter call dida-mcp.delete_task task_id=<id> project_id=<id>` — 删除任务（不可恢复）

**高级查询：**
- `mcporter call dida-mcp.get_tasks_due_today` — 今天到期的任务
- `mcporter call dida-mcp.get_overdue_tasks` — 所有逾期任务
- `mcporter call dida-mcp.get_tasks_by_priority priority=<0|1|3|5>` — 按优先级筛选（0=无, 1=低, 3=中, 5=高）
- `mcporter call dida-mcp.search_tasks query=<关键词>` — 搜索任务

### 注意事项
- 日期格式：ISO 8601，如 `2026-03-15T09:00:00+0800`
- 更新/完成/删除任务需要同时提供 task_id 和 project_id
- 不指定 project_id 创建任务会放入收集箱
- 用 `--output json` 可获取 JSON 格式输出
