# dida-mcp 推广文案合集

> 以下是为各个推广渠道准备好的文案，直接复制粘贴即可使用。

---

## 📌 一、已完成的平台提交

| 平台 | 状态 | 链接 |
|------|------|------|
| awesome-mcp-servers (17k+ ⭐) | ✅ PR 已提交 | [PR #3002](https://github.com/punkpeye/awesome-mcp-servers/pull/3002) |
| mcp.so | ✅ Issue 已提交 | [Issue #750](https://github.com/chatmcp/mcpso/issues/750) |
| GitHub Release v1.0.0 | ✅ 已发布 | [Release](https://github.com/Martinqi826/dida-mcp/releases/tag/v1.0.0) |
| GitHub Topics 标签 | ✅ 已添加 | mcp, mcp-server, dida365, ticktick 等 10 个 |

---

## 📌 二、需要手动提交的平台

### Smithery（4900+ MCP Servers）
👉 https://smithery.ai/servers/new

> Smithery 要求 Streamable HTTP 接口。我们的 dida-mcp 是 stdio 模式，需要先部署一个 HTTP 包装层才能上架 Smithery。**建议后续版本支持 HTTP 模式后再提交。**

### PulseMCP（1700+ MCP Servers）
👉 https://www.pulsemcp.com/submit

提交 URL 填写：`https://github.com/Martinqi826/dida-mcp`
> PulseMCP 会从官方 MCP 注册表每日抓取，也可以直接提交 GitHub URL。

### Glama（18000+ MCP Servers）
👉 https://glama.ai/mcp/servers → 点击 "Add Server"

提交 URL 填写：`https://github.com/Martinqi826/dida-mcp`

---

## 📌 三、中文社区推广文案

---

### 🔹 V2EX（发到 /t/create/share 或 /t/create/dev）

**标题：** `开源了一个滴答清单 MCP Server，让 AI 帮你管理 Todo`

**正文：**

```
各位好，最近做了一个开源项目 dida-mcp，分享给大家。

## 这是什么

dida-mcp 是一个基于 MCP 协议的滴答清单（Dida365）服务端，让 AI 助手可以直接操作你的滴答清单。

简单来说，配置好之后你可以对 AI 说：

- "帮我看看今天有什么到期的任务"
- "创建一个新任务：明天下午3点和客户开会，优先级高"  
- "把'写周报'标记为完成"
- "我有哪些逾期任务？"

AI 就会调用滴答清单 API 帮你完成这些操作。

## 为什么做这个

市面上已经有几个 TickTick 的 MCP Server，但都是针对国际版（ticktick.com），中国版滴答清单（dida365.com）的 API 端点不同，没法直接用。所以做了这个专门支持中国版的。

## 特性

- 13 个 AI 工具：项目管理、任务管理、高级查询（今日到期/逾期/优先级/搜索）
- OAuth 2.0 认证，安全可靠
- 支持 Claude Desktop、CodeBuddy、OpenClaw（龙虾）及任何 MCP 客户端
- Python 3.9+，纯 Python 无重依赖
- MIT 开源

## 链接

- GitHub: https://github.com/Martinqi826/dida-mcp
- 5 分钟快速上手，README 里有详细教程

欢迎 Star ⭐ 和反馈！
```

---

### 🔹 掘金（写文章）

**标题：** `5 分钟让 AI 管理你的滴答清单 — 开源 dida-mcp MCP Server`

**正文：**

```markdown
## 前言

你有没有想过，直接对 AI 说「帮我看看今天有什么到期的任务」，然后 AI 就自动去你的滴答清单里查？

最近 MCP（Model Context Protocol）火了，它让 AI 不仅能聊天，还能调用外部工具。我用 Python 写了一个滴答清单的 MCP Server —— **dida-mcp**，让 Claude、CodeBuddy 等 AI 客户端可以直接操作滴答清单。

## 效果演示

配置完成后，你可以对 AI 说：

| 你说的话 | AI 做的事 |
|---------|----------|
| "今天有什么到期的？" | 调用 `get_tasks_due_today`，返回今日任务列表 |
| "创建任务：周五下午开会" | 调用 `create_task`，在滴答清单创建任务 |
| "把'写周报'完成掉" | 调用 `complete_task`，标记任务完成 |
| "搜索包含'会议'的任务" | 调用 `search_tasks`，返回匹配结果 |

## 为什么需要 dida-mcp

市面上已有的 TickTick MCP Server 都是针对**国际版**（ticktick.com），而中国版滴答清单（dida365.com）API 端点不同。**dida-mcp 是首个支持中国版滴答清单的 MCP Server。**

## 功能覆盖

共 **13 个 AI 工具**：

- 📁 **项目管理**：创建/查看/删除项目
- ✅ **任务管理**：创建/更新/完成/删除任务
- 🔍 **高级查询**：今日到期、逾期任务、按优先级筛选、关键词搜索

## 5 分钟快速上手

### 1. 克隆安装

```bash
git clone https://github.com/Martinqi826/dida-mcp.git
cd dida-mcp
pip install -e .
```

### 2. 获取 OAuth 凭据

访问 [developer.dida365.com/manage](https://developer.dida365.com/manage)，创建应用获取 Client ID 和 Secret。

### 3. 配置并授权

```bash
cp .env.example .env
# 编辑 .env 填入凭据
dida-mcp auth    # 浏览器自动打开授权
dida-mcp test    # 验证连接
```

### 4. 接入 AI 客户端

在 Claude Desktop / CodeBuddy 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "dida-mcp": {
      "command": "dida-mcp",
      "args": ["run"]
    }
  }
}
```

搞定！现在对 AI 说「帮我看看我的滴答清单」试试。

## 技术栈

- Python 3.9+，纯 Python 实现
- JSON-RPC over stdio（标准 MCP 协议）
- OAuth 2.0 认证
- MIT 开源

## 链接

- **GitHub**: [github.com/Martinqi826/dida-mcp](https://github.com/Martinqi826/dida-mcp)

如果觉得有用，欢迎 Star ⭐ 支持一下！有问题也欢迎提 Issue。
```

---

### 🔹 即刻 App（发到 #开源 #效率工具 #AI 话题）

```
🦞 开源了一个让 AI 管理滴答清单的 MCP Server！

对 AI 说「帮我看看今天有什么到期的任务」，它就会自动去你的滴答清单里查。

dida-mcp — 首个支持中国版滴答清单的 MCP Server：
✅ 13 个 AI 工具（任务/项目/查询）
✅ 支持 Claude Desktop、CodeBuddy 等
✅ Python 实现，5 分钟上手
✅ MIT 开源

GitHub 👉 github.com/Martinqi826/dida-mcp

#开源 #MCP #AI #效率工具 #滴答清单
```

---

### 🔹 知乎（回答相关问题 or 发想法）

**适合回答的问题：**
- "如何用 AI 提高工作效率？"
- "MCP 协议有什么好用的工具？"
- "滴答清单有什么进阶用法？"

**回答模板：**

```
分享一个我做的开源项目 —— dida-mcp。

简单来说，它是一个 MCP Server，让 AI 助手（Claude、CodeBuddy 等）可以直接操作你的滴答清单。

配置好之后的体验是这样的：

> 你：帮我看看今天有什么到期的
> AI：你今天有 3 个任务到期：1. 写周报（高优先级）2. 回复客户邮件 3. 整理会议纪要
> 你：把写周报完成掉
> AI：✅ 已将「写周报」标记为完成

为什么做这个呢？因为现有的 TickTick MCP Server 都不支持中国版滴答清单（API 不同），所以我用 Python 写了这个专门针对 dida365.com 的版本。

13 个 AI 工具覆盖：任务增删改查、项目管理、逾期查询、优先级筛选、关键词搜索。

MIT 开源，5 分钟上手：github.com/Martinqi826/dida-mcp
```

---

## 📌 四、英文社区推广文案

---

### 🔹 Reddit — r/MCP 或 r/ClaudeAI

**Title:** `dida-mcp: MCP Server for Dida365 (Chinese TickTick) - Let AI manage your tasks`

**Body:**

```
Hey everyone!

I built **dida-mcp**, an open-source MCP server for **Dida365** (滴答清单) — the Chinese version of TickTick.

### Why?
There are existing TickTick MCP servers, but they all target the international version (ticktick.com). Dida365 uses a different API endpoint (dida365.com), so Chinese users couldn't use those. This fills that gap.

### What it does
13 AI tools for:
- 📁 **Project management**: Create, view, delete projects
- ✅ **Task management**: Create, update, complete, delete tasks
- 🔍 **Smart queries**: Tasks due today, overdue tasks, filter by priority, keyword search

### Compatible with
- Claude Desktop ✅
- CodeBuddy ✅
- OpenClaw ✅
- Any MCP client ✅

### Quick setup
```bash
git clone https://github.com/Martinqi826/dida-mcp.git
cd dida-mcp && pip install -e .
dida-mcp auth  # OAuth login
dida-mcp test  # Verify connection
```

**GitHub**: https://github.com/Martinqi826/dida-mcp

MIT licensed, Python 3.9+, no heavy dependencies. Stars welcome! ⭐
```

---

### 🔹 Hacker News — Show HN

**Title:** `Show HN: dida-mcp – MCP Server for Dida365 (TickTick China), 13 AI tools for task management`

**Body:**

```
I built an MCP server for Dida365 (the Chinese version of TickTick, a popular todo app with 40M+ users).

Existing TickTick MCP servers only work with the international version (ticktick.com). Dida365 uses different API endpoints at dida365.com, so I built this to fill the gap for Chinese users.

Features:
- 13 tools: projects CRUD, tasks CRUD + complete, smart queries (due today, overdue, by priority, search)
- OAuth 2.0 authentication
- Works with Claude Desktop, CodeBuddy, or any MCP-compatible client
- Python 3.9+, MIT licensed

GitHub: https://github.com/Martinqi826/dida-mcp
```

---

### 🔹 Twitter/X

```
🚀 Just open-sourced dida-mcp — an MCP Server for Dida365 (Chinese TickTick)

Let AI assistants manage your todo list:
🗂 Projects CRUD
✅ Tasks CRUD + complete
🔍 Smart queries (due today, overdue, priority, search)

Works with Claude Desktop, CodeBuddy & any MCP client.

13 AI tools | Python | MIT

⭐ github.com/Martinqi826/dida-mcp

#MCP #AI #OpenSource #Productivity
```

---

## 📌 五、待办提醒

### 手动操作清单

- [ ] **上传 Social Preview 封面图**
  - 👉 https://github.com/Martinqi826/dida-mcp/settings
  - 文件位置：项目根目录 `social-preview.png`

- [ ] **提交到 PulseMCP**
  - 👉 https://www.pulsemcp.com/submit
  - 填入 URL：`https://github.com/Martinqi826/dida-mcp`

- [ ] **提交到 Glama**
  - 👉 https://glama.ai/mcp/servers → "Add Server"
  - 填入 URL：`https://github.com/Martinqi826/dida-mcp`

- [ ] **发帖到 V2EX**
  - 👉 https://v2ex.com/new/share
  - 复制上面 V2EX 文案

- [ ] **发文到掘金**
  - 👉 https://juejin.cn/editor/drafts/new
  - 复制上面掘金文案

- [ ] **发到即刻 App**
  - 话题：#开源 #效率工具 #AI
  - 复制上面即刻文案

- [ ] **发到知乎**
  - 回答相关问题 or 发想法
  - 复制上面知乎文案

- [ ] **发到 Reddit**
  - 👉 https://www.reddit.com/r/mcp/submit 或 r/ClaudeAI
  - 复制上面 Reddit 文案

- [ ] **发到 Hacker News**
  - 👉 https://news.ycombinator.com/submit
  - 复制上面 HN 文案

- [ ] **发到 Twitter/X**
  - 复制上面 Twitter 文案
