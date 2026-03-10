"""
滴答清单 MCP Server 命令行工具

提供以下子命令：
- auth:   进行 OAuth 授权
- test:   测试 API 连接
- run:    启动 MCP Server
- logout: 清除本地 token
- status: 查看认证状态
"""

import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv


def _load_env():
    """从多个可能的位置加载 .env 文件"""
    # 候选路径（按优先级排列）
    candidates = [
        Path.cwd() / ".env",                                       # 当前工作目录
        Path(__file__).resolve().parent.parent.parent / ".env",     # 源码相对路径
    ]
    for env_path in candidates:
        if env_path.exists():
            load_dotenv(env_path)
            return
    # fallback
    load_dotenv()


_load_env()


@click.group()
@click.version_option(version="1.0.0")
def main():
    """滴答清单 (Dida365) MCP Server - 让 AI 控制你的滴答清单"""
    pass


@main.command()
@click.option("--client-id", envvar="DIDA_CLIENT_ID", help="OAuth Client ID")
@click.option("--client-secret", envvar="DIDA_CLIENT_SECRET", help="OAuth Client Secret")
@click.option("--redirect-uri", envvar="DIDA_REDIRECT_URI", default="http://localhost:18090/callback", help="OAuth 回调地址")
def auth(client_id: str, client_secret: str, redirect_uri: str):
    """进行 OAuth 授权，获取 Access Token"""
    from .auth import DidaAuth

    if not client_id or not client_secret:
        click.echo("❌ 缺少 Client ID 或 Client Secret。")
        click.echo("   请通过以下方式之一提供：")
        click.echo("   1. 设置环境变量 DIDA_CLIENT_ID 和 DIDA_CLIENT_SECRET")
        click.echo("   2. 创建 .env 文件")
        click.echo("   3. 使用命令行参数 --client-id 和 --client-secret")
        sys.exit(1)

    auth_manager = DidaAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
    )

    try:
        auth_manager.authenticate_interactive()
        click.echo(f"\n🎉 授权成功！Token 已安全保存到本地。")
    except Exception as e:
        import traceback
        click.echo(f"\n❌ 授权失败: {e}")
        traceback.print_exc()
        sys.exit(1)


@main.command()
def test():
    """测试 API 连接是否正常"""
    from .auth import DidaAuth
    from .client import DidaClient

    click.echo("🔍 测试滴答清单 API 连接...\n")

    auth_manager = DidaAuth()

    # 检查认证状态
    if not auth_manager.is_authenticated():
        click.echo("❌ 未找到有效的 token。请先运行 `dida-mcp auth` 进行授权。")
        sys.exit(1)

    click.echo("✅ Token 已加载")

    # 测试 API 调用
    try:
        client = DidaClient(auth_manager)
        projects = client.get_projects()
        click.echo(f"✅ API 连接成功！找到 {len(projects)} 个项目：")
        for p in projects:
            click.echo(f"   📁 {p.get('name', '未知')} (ID: {p.get('id', '')})")
        client.close()
    except Exception as e:
        click.echo(f"❌ API 连接失败: {e}")
        sys.exit(1)

    click.echo(f"\n🎉 一切正常！MCP Server 可以启动了。")


@main.command()
def run():
    """启动 MCP Server"""
    from .server import run_server

    run_server()


@main.command()
def logout():
    """清除本地存储的 token"""
    from .auth import DidaAuth

    auth_manager = DidaAuth()
    auth_manager.logout()


@main.command()
def status():
    """查看当前认证状态"""
    from .auth import DidaAuth, TOKEN_FILE

    auth_manager = DidaAuth()
    if auth_manager.is_authenticated():
        click.echo("✅ 已认证")
        click.echo(f"   Token 文件: {TOKEN_FILE}")
    else:
        click.echo("❌ 未认证")
        click.echo("   请运行 `dida-mcp auth` 进行授权。")


if __name__ == "__main__":
    main()
