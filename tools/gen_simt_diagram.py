#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_simt_diagram.py —— 生成 simt-diagram.svg（1200x900）
三段式：① Grid→Block→Warp→Thread 层级  ② SIMD vs SIMT  ③ Warp Divergence
纯标准库，输出到项目根目录。再用浏览器/Edge headless 导出 PNG。
"""
import os

W, H = 1200, 900
OUT = os.path.join(os.path.dirname(__file__), "..", "simt-diagram.svg")

FONT = "'Microsoft YaHei','PingFang SC',sans-serif"
MONO = "Consolas,Monaco,monospace"


def rect(x, y, w, h, fill, stroke, rx=8, sw=1.2):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def txt(x, y, s, size=12, fill="#1f2937", anchor="start", weight="normal",
        family=FONT):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'font-family="{family}">{s}</text>')


def cells(x, y, n=32, cols=16, cell=12, gap=2.5, colors=None):
    """画 n 个小方块，按 cols 列换行；colors 为长度 n 的填充色列表。"""
    out = []
    for i in range(n):
        r, c = divmod(i, cols)
        cx = x + c * (cell + gap)
        cy = y + r * (cell + gap)
        f = colors[i] if colors else "#2563eb"
        out.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cell}" '
                   f'height="{cell}" rx="2" fill="{f}" stroke="#1e3a8a" '
                   f'stroke-width="0.6"/>')
    return "".join(out)


svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">')
svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>')

# 标题
svg.append(txt(40, 40, "SIMT 执行模型：一条指令，同时作用于 32 个线程", 21, "#111", weight="bold"))
svg.append(txt(40, 62, "Grid → Block → Warp → Thread 的层级，以及 SIMD / SIMT / Warp Divergence", 12, "#6b7280"))

# ============ ① 层级 ============
svg.append(txt(40, 100, "① 四级层级", 15, "#2563eb", weight="bold"))
svg.append(txt(150, 100, "一次 kernel 启动 = 一个 Grid；Grid 切 Block，Block 切 Warp，Warp 装 32 个 Thread", 12, "#6b7280"))

# Grid 外框
svg.append(rect(40, 112, 1120, 200, "#f8fafc", "#cbd5e1", rx=12, sw=1.5))
svg.append(txt(56, 136, "Grid（一次 kernel 启动，例如 &lt;&lt;&lt;grid=2, block=64&gt;&gt;&gt;）", 13, "#111", weight="bold"))

# Block 0
svg.append(rect(60, 148, 528, 152, "#ffffff", "#93c5fd", rx=8, sw=1.3))
svg.append(txt(74, 170, "Block 0", 12, "#1e40af", weight="bold"))
svg.append(rect(78, 180, 244, 110, "#eff6ff", "#bfdbfe", rx=6))
svg.append(txt(86, 198, "Warp 0 · gid 0–31", 11, "#1e40af", weight="bold"))
svg.append(cells(88, 206))
svg.append(rect(334, 180, 244, 110, "#eff6ff", "#bfdbfe", rx=6))
svg.append(txt(342, 198, "Warp 1 · gid 32–63", 11, "#1e40af", weight="bold"))
svg.append(cells(344, 206))

# Block 1
svg.append(rect(604, 148, 528, 152, "#ffffff", "#93c5fd", rx=8, sw=1.3))
svg.append(txt(618, 170, "Block 1", 12, "#1e40af", weight="bold"))
svg.append(rect(622, 180, 244, 110, "#eff6ff", "#bfdbfe", rx=6))
svg.append(txt(630, 198, "Warp 2 · gid 64–95", 11, "#1e40af", weight="bold"))
svg.append(cells(632, 206))
svg.append(rect(878, 180, 244, 110, "#eff6ff", "#bfdbfe", rx=6))
svg.append(txt(886, 198, "Warp 3 · gid 96–127", 11, "#1e40af", weight="bold"))
svg.append(cells(888, 206))

svg.append(txt(40, 336, "block 只在一个 SM 上跑；block 内每 32 个连续线程切成一个 warp；warp 是硬件调度与执行的最小单位。",
               11.5, "#6b7280"))

# ============ ② SIMD vs SIMT ============
svg.append(txt(40, 380, "② SIMD 与 SIMT", 15, "#2563eb", weight="bold"))
svg.append(txt(205, 380, "同一件事：一条指令作用到多份数据。区别在“谁负责打包”", 12, "#6b7280"))

# SIMD 面板
svg.append(rect(40, 394, 545, 205, "#f0f9ff", "#7dd3fc", rx=10))
svg.append(txt(56, 418, "SIMD — 单指令多数据（CPU 的 AVX/SSE）", 12.5, "#0c4a6e", weight="bold"))
svg.append(rect(56, 432, 150, 44, "#e0f2fe", "#38bdf8", rx=6))
svg.append(txt(131, 452, "addps", 13, "#0369a1", anchor="middle", weight="bold"))
svg.append(txt(131, 468, "xmm0, xmm1", 9.5, "#0284c7", anchor="middle", family=MONO))
svg.append('<path d="M206 454 L246 454" stroke="#0284c7" stroke-width="2" marker-end="url(#arw)"/>')
for i in range(8):
    bx = 254 + i * 40
    svg.append(rect(bx, 432, 36, 44, "#ffffff", "#7dd3fc", rx=4))
    svg.append(txt(bx + 18, 451, f"V{i}", 10, "#0369a1", anchor="middle", weight="bold"))
    svg.append(txt(bx + 18, 467, "a+b", 9, "#0284c7", anchor="middle", family=MONO))
svg.append(txt(56, 512, "一条指令 = 8 个 float 同时加（AVX-256）", 11.5, "#0369a1"))
svg.append(txt(56, 536, "程序员显式把数据打包成向量，代码里看得见向量寄存器。", 11, "#64748b"))
svg.append(txt(56, 558, "8 条数据通道，编译器/程序员决定怎么塞。", 11, "#64748b"))

# SIMT 面板
svg.append(rect(615, 394, 545, 205, "#eff6ff", "#93c5fd", rx=10))
svg.append(txt(631, 418, "SIMT — 单指令多线程（GPU 的 CUDA）", 12.5, "#1e3a8a", weight="bold"))
svg.append(rect(631, 432, 150, 44, "#dbeafe", "#60a5fa", rx=6))
svg.append(txt(706, 452, "FADD", 13, "#1d4ed8", anchor="middle", weight="bold"))
svg.append(txt(706, 468, "r = r1 + r2", 9.5, "#2563eb", anchor="middle", family=MONO))
svg.append('<path d="M781 454 L821 454" stroke="#2563eb" stroke-width="2" marker-end="url(#arw)"/>')
# 32 线程 8x4（缩小到 22px，给下方文字留出空间）
for i in range(32):
    r, c = divmod(i, 8)
    bx = 833 + c * 26
    by = 432 + r * 26
    svg.append(f'<rect x="{bx}" y="{by}" width="22" height="22" rx="4" fill="#3b82f6" stroke="#1e40af" stroke-width="0.8"/>')
    svg.append(txt(bx + 11, by + 15, "T", 10, "#ffffff", anchor="middle", weight="bold"))
svg.append(txt(631, 560, "32 个线程 = 1 个 warp，锁步执行同一条指令。", 11.5, "#1d4ed8"))
svg.append(txt(631, 582, "程序员写普通标量代码；硬件自动把线程组成 warp，对程序员透明。", 11, "#64748b"))

# ============ ③ Warp Divergence ============
svg.append(txt(40, 632, "③ Warp Divergence", 15, "#2563eb", weight="bold"))
svg.append(txt(228, 632, "同一个 warp 里的线程走了不同分支，硬件只能串行执行两条路", 12, "#6b7280"))

svg.append(rect(40, 646, 1120, 224, "#fff7ed", "#fdba74", rx=10))

# 代码
svg.append(rect(56, 662, 380, 30, "#fff", "#fdba74", rx=5))
svg.append(txt(66, 682, "if (threadIdx.x % 2) { A } else { B }", 11, "#9a3412", family=MONO))
svg.append(txt(56, 714, "32 个线程：蓝 = 走 if，灰 = 走 else（交错分布）", 10.5, "#9a3412"))
colors = ["#2563eb" if (i % 2 == 1) else "#d1d5db" for i in range(32)]
svg.append(cells(56, 722, n=32, cols=16, cell=16, gap=3, colors=colors))
svg.append(txt(56, 800, "16 个线程进 if、16 个进 else → 一个 warp 分裂成两条路径。", 11, "#9a3412"))
svg.append(txt(56, 822, "硬件不能同时执行两条路径，只能先跑一条、再跑另一条。", 11, "#9a3412"))

# 右侧：两轮串行
svg.append(txt(470, 690, "第 1 轮：执行 if 路径", 11, "#9a3412", weight="bold"))
svg.append(rect(470, 698, 380, 34, "#2563eb", "#1d4ed8", rx=5))
svg.append(txt(482, 720, "16 线程干活，另 16 个屏蔽空转", 10.5, "#ffffff"))
svg.append(txt(470, 754, "第 2 轮：执行 else 路径", 11, "#9a3412", weight="bold"))
svg.append(rect(470, 762, 380, 34, "#fb923c", "#ea580c", rx=5))
svg.append(txt(482, 784, "16 线程干活，另 16 个屏蔽空转", 10.5, "#ffffff"))

# 总耗时括号
svg.append('<path d="M862 698 L872 698 L872 796 L862 796" fill="none" stroke="#9a3412" stroke-width="1.5"/>')
svg.append(txt(884, 742, "总耗时 ≈ A + B", 12, "#9a3412", weight="bold"))
svg.append(txt(884, 762, "最坏约 2 倍", 11, "#9a3412"))
svg.append(txt(884, 782, "吞吐打折", 11, "#9a3412"))

svg.append('</svg>')

# 箭头 marker
marker = ('<defs><marker id="arw" viewBox="0 0 10 10" refX="8" refY="5" '
          'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
          '<path d="M0 0 L10 5 L0 10 z" fill="#2563eb"/></marker></defs>')
svg.insert(2, marker)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
print("written:", os.path.abspath(OUT))
