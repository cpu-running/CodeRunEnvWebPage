#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为「Python / C 语言在线运行环境.html」启动本地服务器（带跨域隔离响应头）。

这个脚本必须在你电脑上的 Python 里运行（命令行 / 终端），
不能在浏览器里的 Python 环境（比如刚才那个网页版）里运行 —— 浏览器没有监听端口的能力。

为什么要它？
  直接用 file:// 双击打开 HTML 时，浏览器不会把页面标记为 cross-origin isolated，
  SharedArrayBuffer 不可用，「停止运行」和「交互式 input()/scanf()」会降级为预填模式。
  本服务器加上 COOP/COEP 响应头，解锁这两个能力。

用法（在终端里）：
  python3 启动本地服务器.py                    # 端口 8000，打开后列出目录下所有网页
  python3 启动本地服务器.py 8080               # 指定端口
  python3 启动本地服务器.py 8080 C语言在线运行环境.html   # 指定端口 + 直接打开某个网页
  python3 启动本地服务器.py 8000 /path/to/dir  # 指定端口 + 网页所在目录

如果直接双击 HTML 也能用，只是少了上面两个能力，不必强行跑这个脚本。
"""

import http.server
import os
import socketserver
import sys
import threading
import urllib.parse


# ---------- 运行环境检查：浏览器 / 交互式环境 ----------
def _precheck():
    """在浏览器里的 Python（Pyodide 等）无法监听端口，提前给出友好提示。"""
    if sys.platform in ("emscripten", "wasi"):
        sys.exit(
            "❌ 当前是在浏览器里的 Python 环境，无法启动本地服务器（浏览器不允许监听端口）。\n"
            "   请在你的电脑上打开「终端 / 命令提示符」，用系统 Python 运行本脚本。\n"
            "   或者干脆直接双击 Python在线运行环境.html —— 除「停止」和交互式 input 外都能用。"
        )
    try:
        import socket  # noqa: F401
    except Exception as exc:  # pragma: no cover
        sys.exit("❌ 当前环境不支持 socket，无法启动服务器：%s" % exc)


# ---------- 确定网页所在目录（不依赖 __file__） ----------
def resolve_dir(explicit=None):
    """按优先级确定服务目录，即便 __file__ 未定义也能工作。"""
    if explicit:
        d = os.path.abspath(os.path.expanduser(explicit))
        if not os.path.isdir(d):
            sys.exit("❌ 目录不存在：%s" % d)
        return d

    candidates = []
    try:  # 正常脚本运行时有 __file__
        candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    candidates.append(os.path.abspath(sys.argv[0]) if sys.argv and sys.argv[0] else "")
    candidates.append(os.getcwd())

    # 优先选：目录里放着网页
    for d in candidates:
        if d and any(f.endswith(".html") for f in os.listdir(d)):
            return d
    for d in candidates:  # 否则退而求其次
        if d and os.path.isdir(d):
            return d
    return os.getcwd()


def build_handler(serve_dir, default_page=None):
    """default_page 为 None 时，访问 / 会列出目录下所有网页供选择。"""
    target = os.path.join(serve_dir, default_page) if default_page else None
    has_html = bool(target) and os.path.isfile(target)
    quoted = urllib.parse.quote(default_page) if default_page else ""
    pages = sorted(f for f in os.listdir(serve_dir) if f.endswith(".html"))

    class IsolatedHandler(http.server.SimpleHTTPRequestHandler):
        """带跨域隔离响应头的静态文件服务器"""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=serve_dir, **kwargs)

        def _index_page(self):
            """生成一个简单的网页列表，省得手打中文文件名"""
            items = "".join(
                '<li><a href="/%s">%s</a></li>' % (urllib.parse.quote(f), f) for f in pages
            ) or "<li>（该目录下没有 .html 文件）</li>"
            body = (
                "<meta charset='utf-8'><title>选择要打开的网页</title>"
                "<div style='font:15px/1.7 system-ui,sans-serif;max-width:640px;"
                "margin:60px auto;padding:0 20px'>"
                "<h2>📄 选择要打开的网页</h2><ul>%s</ul>"
                "<p style='color:#888'>跨域隔离响应头(COOP/COEP)已开启，"
                "SharedArrayBuffer 可用：停止运行、交互式输入均已解锁。</p></div>" % items
            )
            raw = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):  # 访问 http://localhost:端口/ 时自动跳到网页，省得手打中文名
            path = self.path.split("?", 1)[0].split("#", 1)[0]
            if path in ("/", ""):
                if has_html:
                    self.send_response(302)
                    self.send_header("Location", "/" + quoted)
                    self.end_headers()
                    return
                self._index_page()
                return
            super().do_GET()

        def do_HEAD(self):
            path = self.path.split("?", 1)[0].split("#", 1)[0]
            if path in ("/", "") and has_html:
                self.send_response(302)
                self.send_header("Location", "/" + quoted)
                self.end_headers()
                return
            super().do_HEAD()

        def end_headers(self):
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            # credentialless：允许无凭据地加载 jsDelivr / cdnjs 等第三方 CDN 资源
            self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, fmt, *args):
            sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    return IsolatedHandler


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    _precheck()

    args = [a for a in sys.argv[1:]]
    port = 8000
    explicit_dir = None
    page = None
    for a in args:
        if a.isdigit():
            port = int(a)
        elif a.endswith(".html"):
            page = a
        else:
            explicit_dir = a
    if not 1 <= port <= 65535:
        sys.exit("❌ 端口号需在 1~65535 之间")

    serve_dir = resolve_dir(explicit_dir)
    handler = build_handler(serve_dir, page)

    try:
        httpd = Server(("127.0.0.1", port), handler)
    except OSError as exc:
        if getattr(exc, "errno", None) in (48, 98, 10048):  # 端口被占用
            sys.exit("❌ 端口 %d 已被占用，换一个：python3 %s %d" % (port, "启动本地服务器.py", port + 1))
        raise

    url = "http://localhost:%d/" % port
    print("=" * 56)
    print("服务目录: %s" % serve_dir)
    print("请访问:   %s" % url)
    for f in sorted(x for x in os.listdir(serve_dir) if x.endswith(".html")):
        print("  网页:   http://localhost:%d/%s" % (port, urllib.parse.quote(f)))
    print("跨域隔离响应头(COOP/COEP)已开启 → SharedArrayBuffer 可用")
    print("            → 「⏹ 停止」与交互式输入已解锁")
    print("按 Ctrl+C 停止")
    print("=" * 56)

    try:
        import webbrowser

        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
