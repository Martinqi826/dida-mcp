"""
滴答清单 (Dida365) OAuth 认证模块

实现 OAuth 2.0 认证流程：
1. 引导用户访问授权页面
2. 获取 authorization code
3. 交换 access token
4. 本地持久化存储 token
"""

from __future__ import annotations

import json
import os
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# 滴答清单 (dida365) API 地址
DIDA_AUTH_URL = "https://dida365.com/oauth/authorize"
DIDA_TOKEN_URL = "https://dida365.com/oauth/token"
DIDA_API_BASE = "https://api.dida365.com"

# Token 存储路径
CONFIG_DIR = Path.home() / ".dida-mcp"
TOKEN_FILE = CONFIG_DIR / "token.json"


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """处理 OAuth 回调的 HTTP 请求处理器"""

    authorization_code: Optional[str] = None

    def do_GET(self):
        """处理 GET 请求，提取 authorization code"""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "code" in params:
            OAuthCallbackHandler.authorization_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>&#x2705; &#x6388;&#x6743;&#x6210;&#x529f;&#xff01;</h1>"
                b"<p>&#x4f60;&#x53ef;&#x4ee5;&#x5173;&#x95ed;&#x6b64;&#x9875;&#x9762;&#x4e86;&#x3002;</p></body></html>"
            )
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            error = params.get("error", ["unknown"])[0]
            self.wfile.write(
                f"<html><body><h1>&#x274c; &#x6388;&#x6743;&#x5931;&#x8d25;</h1>"
                f"<p>&#x9519;&#x8bef;: {error}</p></body></html>".encode()
            )

    def log_message(self, format, *args):
        """静默日志"""
        pass


class DidaAuth:
    """滴答清单 OAuth 认证管理器"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        self.client_id = client_id or os.getenv("DIDA_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("DIDA_CLIENT_SECRET", "")
        self.redirect_uri = redirect_uri or os.getenv(
            "DIDA_REDIRECT_URI", "http://localhost:18090/callback"
        )
        self._token_data: Optional[Dict] = None

    def get_auth_url(self, scope: str = "tasks:read tasks:write") -> str:
        """生成 OAuth 授权 URL"""
        params = {
            "client_id": self.client_id,
            "scope": scope,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": "dida_mcp_auth",
        }
        return f"{DIDA_AUTH_URL}?{urlencode(params)}"

    def exchange_token(self, code: str) -> dict:
        """用 authorization code 换取 access token"""
        form_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "scope": "tasks:write tasks:read",
        }

        encoded_body = urlencode(form_data).encode("utf-8")

        req = Request(
            DIDA_TOKEN_URL,
            data=encoded_body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )

        try:
            with urlopen(req) as resp:
                raw = resp.read().decode("utf-8")
                token_data = json.loads(raw)
        except HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Token 交换失败: HTTP {e.code}\n{body[:300]}"
            ) from e

        token_data["obtained_at"] = int(time.time())
        self._save_token(token_data)
        self._token_data = token_data
        return token_data

    def authenticate_interactive(self) -> dict:
        """
        交互式 OAuth 认证流程：
        1. 启动本地 HTTP 服务器监听回调
        2. 打开浏览器授权
        3. 捕获 authorization code
        4. 交换 access token
        """
        # 解析 redirect_uri 获取端口
        parsed = urlparse(self.redirect_uri)
        port = parsed.port or 18090

        # 更新 redirect_uri 为本地服务器
        self.redirect_uri = f"http://localhost:{port}/callback"

        auth_url = self.get_auth_url()
        print(f"\n🔐 正在打开浏览器进行授权...")
        print(f"   如果浏览器没有自动打开，请手动访问：")
        print(f"   {auth_url}\n")

        webbrowser.open(auth_url)

        # 启动本地服务器等待回调
        OAuthCallbackHandler.authorization_code = None
        server = HTTPServer(("localhost", port), OAuthCallbackHandler)
        server.timeout = 120  # 2 分钟超时

        print(f"⏳ 等待授权回调（端口 {port}，超时 120 秒）...")

        while OAuthCallbackHandler.authorization_code is None:
            server.handle_request()

        server.server_close()
        code = OAuthCallbackHandler.authorization_code

        if not code:
            raise RuntimeError("未能获取 authorization code")

        print(f"✅ 获取到授权码，正在换取 token...")
        token_data = self.exchange_token(code)
        print(f"✅ 认证成功！Token 已保存到 {TOKEN_FILE}")
        return token_data

    def get_access_token(self) -> str:
        """获取可用的 access token"""
        if self._token_data and "access_token" in self._token_data:
            return self._token_data["access_token"]

        # 尝试从文件加载
        token_data = self._load_token()
        if token_data and "access_token" in token_data:
            self._token_data = token_data
            return token_data["access_token"]

        # 尝试从环境变量加载
        env_token = os.getenv("DIDA_ACCESS_TOKEN", "")
        if env_token:
            return env_token

        raise RuntimeError(
            "未找到有效的 access token。请先运行 `dida-mcp auth` 进行授权。"
        )

    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        try:
            token = self.get_access_token()
            return bool(token)
        except RuntimeError:
            return False

    def logout(self):
        """清除本地存储的 token"""
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
            print("✅ 已清除本地 token")
        self._token_data = None

    def _save_token(self, token_data: dict):
        """保存 token 到本地文件"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(json.dumps(token_data, indent=2))

    def _load_token(self) -> Optional[dict]:
        """从本地文件加载 token"""
        if TOKEN_FILE.exists():
            try:
                return json.loads(TOKEN_FILE.read_text())
            except (json.JSONDecodeError, OSError):
                return None
        return None
