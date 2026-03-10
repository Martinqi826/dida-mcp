# dida-skill 🦞✅

**滴答清单 (Dida365) MCP Server** — 让 AI 助手控制你的滴答清单。

适用于 [OpenClaw (龙虾)](https://openclaw.ai)、[Claude Desktop](https://claude.ai)、[CodeBuddy](https://www.codebuddy.ai/) 以及任何支持 MCP 协议的 AI 客户端。

## ✨ 功能

| 类别 | 工具 | 说明 |
|------|------|------|
| 📁 项目管理 | `get_projects` | 列出所有项目（清单） |
| | `get_project_detail` | 查看项目详情及其任务 |
| | `create_project` | 创建新项目 |
| | `delete_project` | 删除项目 |
| ✅ 任务管理 | `get_all_tasks` | 获取所有未完成任务 |
| | `create_task` | 创建新任务 |
| | `update_task` | 更新任务信息 |
| | `complete_task` | 标记任务完成 |
| | `delete_task` | 删除任务 |
| 🔍 高级查询 | `get_tasks_due_today` | 今天到期的任务 |
| | `get_overdue_tasks` | 所有逾期任务 |
| | `get_tasks_by_priority` | 按优先级筛选 |
| | `search_tasks` | 关键词搜索 |

## 🚀 快速开始

### 1. 创建滴答清单应用

1. 访问 [developer.dida365.com/manage](https://developer.dida365.com/manage)
2. 创建一个新应用
3. 记下 **Client ID** 和 **Client Secret**
4. 设置 **OAuth Redirect URL** 为 `http://localhost:18090/callback`

### 2. 安装

```bash
git clone https://github.com/Martinqi826/dida-skill.git
cd dida-skill
pip install -e .
```

### 3. 配置

```bash
cp .env.example .env
```

编辑 `.env`，填入你自己的凭据：

```env
DIDA_CLIENT_ID=你的_Client_ID
DIDA_CLIENT_SECRET=你的_Client_Secret
DIDA_REDIRECT_URI=http://localhost:18090/callback
```

### 4. 授权

```bash
dida-mcp auth
```

浏览器会自动打开，登录你的滴答清单账号并授权。成功后 Token 会保存到 `~/.dida-mcp/token.json`。

### 5. 验证

```bash
dida-mcp test
```

看到 `✅ API 连接成功！` 就说明一切就绪。

---

## 🦞 配置到 OpenClaw（龙虾）

OpenClaw 目前不原生支持 MCP Server 注入，需要通过 **mcporter** 桥接。

### 第一步：安装 mcporter

```bash
npm install -g mcporter
```

### 第二步：注册 dida-mcp 到 mcporter

```bash
mcporter add dida-mcp \
  --command "dida-mcp" \
  --args "run" \
  --env DIDA_CLIENT_ID=你的_Client_ID \
  --env DIDA_CLIENT_SECRET=你的_Client_Secret \
  --env DIDA_REDIRECT_URI=http://localhost:18090/callback
```

或者手动编辑 `~/.mcporter/mcporter.json`：

```json
{
  "mcpServers": {
    "dida-mcp": {
      "command": "dida-mcp",
      "args": ["run"],
      "description": "滴答清单 MCP Server",
      "env": {
        "DIDA_CLIENT_ID": "你的_Client_ID",
        "DIDA_CLIENT_SECRET": "你的_Client_Secret",
        "DIDA_REDIRECT_URI": "http://localhost:18090/callback"
      }
    }
  }
}
```

### 第三步：启用 mcporter skill

确认 `~/.openclaw/openclaw.json` 中有：

```json
{
  "skills": {
    "entries": {
      "mcporter": {
        "enabled": true
      }
    }
  }
}
```

### 第四步：添加工具说明到 TOOLS.md

将 [`openclaw/TOOLS.md`](./openclaw/TOOLS.md) 的内容追加到 `~/.openclaw/workspace/TOOLS.md` 中。

这一步很关键——OpenClaw AI 会在启动时读取 TOOLS.md，从而知道可以通过 `mcporter call dida-mcp.*` 来操作你的滴答清单。

### 第五步：重启 Gateway 并验证

```bash
openclaw gateway restart
```

在 OpenClaw 中开一个**新对话**，输入：

```
帮我看看我的滴答清单有哪些项目
```

AI 就会调用 `mcporter call dida-mcp.get_projects` 并返回结果。

---

## 🤖 配置到 Claude Desktop / CodeBuddy

在 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "dida-mcp": {
      "command": "dida-mcp",
      "args": ["run"],
      "env": {
        "DIDA_CLIENT_ID": "你的_Client_ID",
        "DIDA_CLIENT_SECRET": "你的_Client_Secret"
      }
    }
  }
}
```

---

## 💬 使用示例

配置完成后，你可以对 AI 说：

- 🗂️ "帮我看看我的滴答清单有哪些项目"
- ✅ "创建一个新任务：明天下午3点和客户开会，优先级高"
- ✔️ "把'写周报'标记为完成"
- 🔍 "搜索包含'会议'的任务"
- 📁 "创建一个叫'工作'的新项目"
- ⚠️ "我有哪些逾期任务？"
- 🔺 "列出所有高优先级任务"
- 📅 "今天有什么到期的？"

---

## 📖 CLI 命令

| 命令 | 说明 |
|------|------|
| `dida-mcp auth` | OAuth 授权（首次使用必须执行） |
| `dida-mcp test` | 测试 API 连接 |
| `dida-mcp run` | 启动 MCP Server（stdio 模式） |
| `dida-mcp status` | 查看认证状态 |
| `dida-mcp logout` | 清除本地 token |

---

## 🔧 项目结构

```
dida-skill/
├── pyproject.toml              # 项目配置
├── LICENSE                     # MIT 许可证
├── README.md                   # 本文档
├── .env.example                # 环境变量示例
├── .gitignore                  # Git 忽略规则
├── openclaw/
│   └── TOOLS.md                # OpenClaw TOOLS.md 参考内容
└── src/
    └── dida_mcp/
        ├── __init__.py         # 包初始化
        ├── auth.py             # OAuth 2.0 认证模块
        ├── client.py           # 滴答清单 API 客户端
        ├── server.py           # MCP Server 实现 (JSON-RPC over stdio)
        └── cli.py              # 命令行工具
```

---

## ⚠️ 注意事项

- 本项目使用滴答清单**中国版**（dida365.com）的 Open API
- 国际版 TickTick 用户需自行修改 API 地址（`ticktick.com`）
- Access Token 存储在 `~/.dida-mcp/token.json`，请妥善保管
- **请勿将 `.env` 文件提交到 git**，你的 Client Secret 是私密的
- 删除项目或任务的操作不可恢复
- 优先级数值：`0`=无、`1`=低、`3`=中、`5`=高
- 日期格式为 ISO 8601，如 `2026-03-15T09:00:00+0800`

---

## 🤝 Contributing

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/awesome`)
3. 提交更改 (`git commit -m 'Add awesome feature'`)
4. 推送到分支 (`git push origin feature/awesome`)
5. 创建 Pull Request

---

## 📄 License

[MIT](./LICENSE)
