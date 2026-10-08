# CodeRunEnvWebPage

**用纯 HTML 文件模拟编程语言运行环境** —— 打开网页就能写代码、跑代码，无需安装任何编译器或解释器。

· 许可证：MIT

· 技术栈：HTML + CSS + JavaScript + WebAssembly

· 依赖后端：无（全部在浏览器本地运行）

---

# 📖 项目简介

CodeRunEnvWebPage 是一组可以直接在浏览器里打开即用的「编程语言在线运行环境」网页。所有运行能力都由 WebAssembly / JavaScript 引擎 在浏览器本地完成，不依赖任何后端服务器：代码不会被上传到任何地方，断网（首次加载完成后）也能继续使用。

目前包含两个环境。

**C,C++在线编译运行环境.html** —— C / C++ 运行环境，提供双引擎：一是 JSCPP 轻量解释器（秒开，适合基础语法），二是 Clang → WebAssembly（WASI）真编译（支持完整标准库、struct、malloc、文件 IO、C++ STL）。

**Python在线运行环境.html** —— Python 3 运行环境，基于 Pyodide（CPython 编译为 WebAssembly），是真实 CPython，支持 NumPy / Pandas / Matplotlib，并可通过 micropip 从 PyPI 装包。

另外附带一个可选的小工具 **启动本地服务器.py**，用于启动带 COOP/COEP 响应头的本地静态服务器，解锁 SharedArrayBuffer（交互式输入 + 可中断运行）。

---

# ✨ 功能特性

**通用能力**

· 📝 CodeMirror 编辑器：语法高亮、自动括号匹配、自动缩进、行号、活动行高亮

· ⌨️ 快捷键：Ctrl/⌘ + Enter 运行、Ctrl/⌘ + / 注释、Ctrl + Space 补全、Tab 缩进

· 📚 内置示例代码：C/C++ 11 个、Python 10 个，一键载入，可整段 Ctrl+Z 还原

· 🔀 可拖拽分栏：编辑区 / 输出区宽度自由调整，窄屏自动上下排列

· 🌓 明暗主题切换、⚙ 设置面板、↶ 撤回、📂 打开本地文件、💾 下载源码

· 🖥️ 逐行块渲染输出：printf / print 的换行、空行、中文都不会错乱

· 🚦 输出上限保护：超出上限自动丢弃最早的行并提示，避免万行输出卡死页面

· ⏱️ 多级超时 / 看门狗：区分「加载编译」「等待输入」「程序运行」三种阶段，只对停滞判超时，不会因为首次下载工具链慢就误杀

· 🧯 自动降级：Worker 创建失败 / 引擎加载失败时自动回退，尽量保证「还能用」

**C/C++ 环境（v4）**

· 双引擎

  · 🪶 JSCPP 轻量解释器：秒开，适合基础语法题，不支持 struct / malloc / 文件 IO / 多文件

  · ⚙️ Clang 真编译：clang(cc1) → .o → wasm-ld → .wasm → WASI 完整链路，支持完整 C 标准库、struct、malloc、文件 IO、C++ STL

· 语言 / 标准可选：C 支持 c99 / c11 / c17 / c2x，C++ 支持 c++11 / 14 / 17 / 20

· 优化级别：-O0 / -O1 / -O2 / -O3，可开启 -Wall

· 智能提示：识别代码里用到 struct / malloc / 文件 IO 等解释器不支持的特性，主动建议切换到 Clang 引擎；中文等非 ASCII 字符也会提前提醒

· 标准库缓存：29MB 的 sysroot.tar 与 95MB 工具链通过 Cache API 持久化，停止 / 重启 / 刷新后不必重下


**Python 环境（v3.1）**


· 真实 CPython：Pyodide 运行的完整 CPython，版本号实时显示

· 多 CDN 并行探测：jsDelivr / fastly / unpkg 等并行测速，自动选最快的源，支持自定义运行时地址

· 可视化预加载：把几十 MB 的运行时下载变成进度条（可跳过）

· pip 装包：内置 micropip，可从 PyPI / 清华镜像 / 阿里云镜像安装纯 Python 包

· 图形与富媒体：matplotlib.pyplot.show() 自动输出 PNG 到输出区；提供 show() 与 pyide_host（图片 / HTML / 文件下载）宿主接口

· 内核重启：exit() / quit() 导致内核退出时自动重建


**交互输入与「停止」**


直接双击 HTML（file:// 打开） —— 交互式 input() / scanf() 不可用，需在底部「预填输入」里事先写好；「⏹ 停止」可用，但主要靠超时与重启兜底。

通过 启动本地服务器.py 打开 —— 交互式输入可逐行实时发送；「⏹ 停止」立即中断（SIGINT / abort）。

原因：交互式输入与可中断运行依赖 SharedArrayBuffer，而浏览器要求页面处于 cross-origin isolated 状态才允许使用它。本地服务器脚本会附带 Cross-Origin-Opener-Policy: same-origin 与 Cross-Origin-Embedder-Policy: credentialless 响应头来满足这个条件。

---

# 🚀 快速开始


**方式一：直接双击（最简单）**


1. 下载本仓库全部文件到同一个文件夹

2. 双击 Python在线运行环境.html 或 C,C++在线编译运行环境.html

3. 等待运行时加载完成（状态灯变绿），点 ▶ 运行

缺点是 file:// 下没有 SharedArrayBuffer：交互式输入需改用底部「预填输入」，且 C/C++ 的 Clang 引擎可能因跨域限制加载失败（会自动切回轻量解释器）。


**方式二：本地服务器（推荐，功能完整）**


需要电脑上装有 Python 3。在文件所在目录打开终端：

```bash
python3 启动本地服务器.py
```

脚本会自动打开浏览器并列出目录下的所有网页。也可以指定端口和页面：

```bash
python3 启动本地服务器.py 8080                            # 指定端口
python3 启动本地服务器.py 8080 Python在线运行环境.html     # 指定端口 + 指定页面
python3 启动本地服务器.py 8000 /path/to/dir               # 指定端口 + 指定目录
```

然后访问 http://localhost:8000/ 即可，交互式输入与「停止」按钮全部解锁。

⚠️ 该脚本必须在电脑上的系统 Python 里运行，不能在上面的网页版 Python 环境里运行（浏览器没有监听端口的能力，脚本会给出提示）。

---

# 🗂️ 目录结构

```
CodeRunEnvWebPage/
├── C,C++在线编译运行环境.html    # C/C++ 运行环境（JSCPP 解释器 + Clang/WASI 真编译）
├── Python在线运行环境.html       # Python 运行环境（Pyodide / CPython on WASM）
├── 启动本地服务器.py             # 带 COOP/COEP 的本地静态服务器（解锁 SharedArrayBuffer）
├── README.md
└── LICENSE                       # MIT
```

---

# 🔧 技术原理

```
┌──────────────────────── 浏览器页面（主线程） ────────────────────────┐
│  CodeMirror 编辑器 │ 工具栏 / 示例 │ 输出面板 │ 标准输入区            │
└───────────────┬─────────────────────────────────────────────────────┘
                │ postMessage / SharedArrayBuffer + Atomics
┌───────────────▼─────────────────────────────────────────────────────┐
│                       Web Worker（执行引擎）                          │
│                                                                     │
│  C/C++：JSCPP 解释器  ── 或 ──  browsercc(Clang) + wasm-ld + WASI    │
│  Python：Pyodide（CPython → WebAssembly）                            │
└─────────────────────────────────────────────────────────────────────┘
```

· Worker 隔离：代码在 Worker 里执行，死循环不会冻结界面，且可以被 terminate() 强行终止

· 同步 stdin：Worker 用 Atomics.wait() 阻塞等待，主线程写入 SharedArrayBuffer 后 Atomics.notify() 唤醒，实现「像终端一样」的阻塞式输入

· 流式解码：输出按字节块回调，用 TextDecoder({ stream: true }) 处理跨块的 UTF-8 多字节字符，避免中文乱码

· ANSI 过滤：编译器诊断里的颜色转义序列会被剥离，并处理被切分的残缺转义序列

· 渲染节流：输出先进队列，requestAnimationFrame 批量落盘，一帧只读一次 scrollHeight

· 参数缓存保护：Emscripten 的 callMain() 会就地 unshift 修改参数数组，因此缓存一律以副本对外，避免第二次运行参数被污染

---

# ❓ 常见问题

Q：Clang 引擎一直加载失败？

*多半是以 file:// 打开或网络受限导致。Clang 需要下载约 95MB 的工具链和 29MB 标准库。请改用 启动本地服务器.py 打开，或在 ⚙ 设置里切换 CDN 源；也可直接切回轻量解释器做题。*


Q：Python 运行时加载很慢？

*Pyodide 完整运行时约几十 MB，首次加载受网速影响。设置里可切换 CDN、或勾选「跳过运行时预加载」直接启动；加载完成后会被浏览器缓存。*


Q：input() / scanf() 没反应？

*若以 file:// 打开，页面底部显示的是「预填输入」，请事先把每行输入填好再运行。用本地服务器打开则可实时逐行输入。*


Q：程序死循环了怎么办？

*Worker 模式下点「⏹ 停止」即可；页面内直跑模式下会由超时看门狗兜底。可在设置里调整超时秒数。*


Q：代码会被上传吗？

*不会。所有编译与执行都在你的浏览器本地完成，没有任何后端接口，源码只保存在浏览器 localStorage 里。*


Q：能安装任意 pip 包吗？

*只有纯 Python 包可以通过 micropip 从 PyPI 安装；含 C 扩展的包需要 Pyodide 官方预编译版本（如 numpy、pandas、matplotlib 等已内置可直接 import）。*


---

# 🤖 AI 使用声明

本项目在开发过程中大量使用了 AI 辅助生成：

· AI 工具：DeepSeek（深度求索）

· 使用范围：页面结构、样式（CSS）、JavaScript 逻辑、Web Worker 引擎胶水代码、示例代码、注释与文案等，均由 AI 参与生成与迭代

· 人工参与：需求定义、功能取舍、实际运行测试、缺陷定位与反馈迭代

因此：

1. 代码可能存在未经充分测试的边界情况或潜在缺陷，请在生产环境使用前自行评估与验证；

2. 项目中的技术方案（如 browsercc 的 -### 参数推导、WASI shim 用法等）参考了相应开源项目的公开做法，若上游 API 变更可能失效；

3. 使用者应自行确认生成内容是否符合自身所在地区或组织的相关规定。

---

# 📄 许可证

本项目基于 MIT License 开源。


---

# 🙏 致谢

本项目站在以下开源项目的肩膀上：

· JSCPP —— JavaScript 实现的 C++ 解释器

· browsercc —— 浏览器中的 Clang / LLD（WebAssembly）

· browser_wasi_shim —— 纯 JS 的 WASI 运行时

· Pyodide —— CPython 的 WebAssembly 发行版

· CodeMirror 5 —— 代码编辑器

· jsDelivr / unpkg / cdnjs —— 静态资源 CDN
