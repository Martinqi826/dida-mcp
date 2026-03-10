"""
滴答清单 (Dida365) Open API 客户端

基于官方 Open API 实现，支持：
- 项目（清单）管理
- 任务 CRUD
- 任务搜索和筛选
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from .auth import DIDA_API_BASE, DidaAuth

# API 端点
OPEN_API = f"{DIDA_API_BASE}/open/v1"


class DidaClient:
    """滴答清单 API 客户端"""

    def __init__(self, auth: Optional[DidaAuth] = None):
        self.auth = auth or DidaAuth()
        self._http_client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """获取或创建 HTTP 客户端"""
        if self._http_client is None or self._http_client.is_closed:
            token = self.auth.get_access_token()
            self._http_client = httpx.Client(
                base_url=OPEN_API,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._http_client

    def close(self):
        """关闭 HTTP 客户端"""
        if self._http_client and not self._http_client.is_closed:
            self._http_client.close()

    # ==================== 项目（清单）管理 ====================

    def get_projects(self) -> List[Dict]:
        """获取所有项目（清单）列表"""
        response = self.client.get("/project")
        response.raise_for_status()
        return response.json()

    def get_project(self, project_id: str) -> Dict:
        """获取指定项目的详细信息"""
        response = self.client.get(f"/project/{project_id}")
        response.raise_for_status()
        return response.json()

    def get_project_with_tasks(self, project_id: str) -> Dict:
        """获取指定项目及其所有任务"""
        response = self.client.get(f"/project/{project_id}/data")
        response.raise_for_status()
        return response.json()

    def create_project(
        self,
        name: str,
        color: Optional[str] = None,
        view_mode: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> Dict:
        """创建新项目（清单）"""
        data: Dict[str, Any] = {"name": name}
        if color:
            data["color"] = color
        if view_mode:
            data["viewMode"] = view_mode
        if folder_id:
            data["folderId"] = folder_id

        response = self.client.post("/project", json=data)
        response.raise_for_status()
        return response.json()

    def update_project(self, project_id: str, **kwargs) -> Dict:
        """更新项目信息"""
        data: Dict[str, Any] = {}
        field_map = {
            "name": "name",
            "color": "color",
            "view_mode": "viewMode",
            "folder_id": "folderId",
        }
        for key, api_key in field_map.items():
            if key in kwargs and kwargs[key] is not None:
                data[api_key] = kwargs[key]

        response = self.client.post(f"/project/{project_id}", json=data)
        response.raise_for_status()
        return response.json()

    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        response = self.client.delete(f"/project/{project_id}")
        response.raise_for_status()
        return True

    # ==================== 任务管理 ====================

    def get_task(self, project_id: str, task_id: str) -> Dict:
        """获取指定任务的详细信息"""
        response = self.client.get(f"/project/{project_id}/task/{task_id}")
        response.raise_for_status()
        return response.json()

    def create_task(
        self,
        title: str,
        project_id: Optional[str] = None,
        content: Optional[str] = None,
        desc: Optional[str] = None,
        start_date: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: int = 0,
        is_all_day: Optional[bool] = None,
        time_zone: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict:
        """
        创建新任务

        Args:
            title: 任务标题
            project_id: 项目ID（不填则放入收集箱）
            content: 任务内容/描述
            desc: 纯文本描述
            start_date: 开始日期 (ISO 8601, 例如: "2026-03-15T09:00:00+0800")
            due_date: 截止日期 (ISO 8601)
            priority: 优先级 (0=无, 1=低, 3=中, 5=高)
            is_all_day: 是否全天任务
            time_zone: 时区（例如 "Asia/Shanghai"）
            tags: 标签列表
        """
        data: Dict[str, Any] = {"title": title}

        if project_id:
            data["projectId"] = project_id
        if content:
            data["content"] = content
        if desc:
            data["desc"] = desc
        if start_date:
            data["startDate"] = start_date
        if due_date:
            data["dueDate"] = due_date
        if priority:
            data["priority"] = priority
        if is_all_day is not None:
            data["isAllDay"] = is_all_day
        if time_zone:
            data["timeZone"] = time_zone
        else:
            data["timeZone"] = "Asia/Shanghai"
        if tags:
            data["tags"] = tags

        response = self.client.post("/task", json=data)
        response.raise_for_status()
        return response.json()

    def update_task(
        self, task_id: str, project_id: str, **kwargs
    ) -> Dict:
        """
        更新任务

        Args:
            task_id: 任务ID
            project_id: 项目ID
            **kwargs: 要更新的字段
        """
        data: Dict[str, Any] = {"id": task_id, "projectId": project_id}
        field_map = {
            "title": "title",
            "content": "content",
            "desc": "desc",
            "start_date": "startDate",
            "due_date": "dueDate",
            "priority": "priority",
            "is_all_day": "isAllDay",
            "time_zone": "timeZone",
            "tags": "tags",
        }
        for key, api_key in field_map.items():
            if key in kwargs and kwargs[key] is not None:
                data[api_key] = kwargs[key]

        response = self.client.post(f"/task/{task_id}", json=data)
        response.raise_for_status()
        return response.json()

    def complete_task(self, project_id: str, task_id: str) -> bool:
        """将任务标记为完成"""
        response = self.client.post(
            f"/project/{project_id}/task/{task_id}/complete"
        )
        response.raise_for_status()
        return True

    def delete_task(self, project_id: str, task_id: str) -> bool:
        """删除任务"""
        response = self.client.delete(
            f"/project/{project_id}/task/{task_id}"
        )
        response.raise_for_status()
        return True

    # ==================== 高级查询 ====================

    def get_all_tasks(self) -> List[Dict]:
        """获取所有未完成的任务（通过遍历项目）"""
        projects = self.get_projects()
        all_tasks: List[Dict] = []
        for project in projects:
            try:
                project_data = self.get_project_with_tasks(project["id"])
                tasks = project_data.get("tasks", [])
                for task in tasks:
                    task["_projectName"] = project.get("name", "")
                    task["_projectId"] = project["id"]
                all_tasks.extend(tasks)
            except httpx.HTTPStatusError:
                continue
        return all_tasks

    def get_tasks_due_today(self) -> List[Dict]:
        """获取今天到期的任务"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        all_tasks = self.get_all_tasks()
        return [
            task
            for task in all_tasks
            if task.get("dueDate", "").startswith(today)
        ]

    def get_overdue_tasks(self) -> List[Dict]:
        """获取已过期的任务"""
        now = datetime.now(timezone.utc)
        all_tasks = self.get_all_tasks()
        overdue: List[Dict] = []
        for task in all_tasks:
            due = task.get("dueDate")
            if due and task.get("status", 0) == 0:
                try:
                    due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
                    if due_dt < now:
                        overdue.append(task)
                except ValueError:
                    continue
        return overdue

    def get_tasks_by_priority(self, priority: int) -> List[Dict]:
        """按优先级获取任务 (0=无, 1=低, 3=中, 5=高)"""
        all_tasks = self.get_all_tasks()
        return [task for task in all_tasks if task.get("priority", 0) == priority]

    def search_tasks(self, query: str) -> List[Dict]:
        """搜索任务（按标题和内容模糊匹配）"""
        query_lower = query.lower()
        all_tasks = self.get_all_tasks()
        results: List[Dict] = []
        for task in all_tasks:
            title = task.get("title", "").lower()
            content = task.get("content", "").lower()
            tags = [t.lower() for t in task.get("tags", [])]
            if (
                query_lower in title
                or query_lower in content
                or any(query_lower in tag for tag in tags)
            ):
                results.append(task)
        return results
