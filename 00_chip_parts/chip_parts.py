#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chip_parts.py —— 回答"GPU 内部由哪些硬件组成"
把芯片拆成 4 类，逐类说明它在数据链路上干什么。不需要 GPU，纯讲解。

运行：python3 chip_parts.py
"""

# 一次推理请求的数据流：
# 显存(存模型) -> 显存控制器(搬运) -> L2(暂存热点) -> SM(计算) -> 写回
PARTS = [
    ("计算类", [
        "SM（核心，负责真正算数）",
        "L2 缓存（跨 SM 共享，暂存热点数据）",
    ]),
    ("存储类", [
        "HBM 显存（几十~几十GB，装模型权重）",
        "显存控制器（决定数据搬运效率，带宽瓶颈）",
    ]),
    ("控制类", [
        "GigaThread 引擎（把任务拆成 block，分配给各 SM）",
        "Warp Scheduler（每个 SM 内部，决定哪些 warp 上机执行）",
    ]),
    ("互联类", [
        "NVLink（多卡之间的高速通道，替代 PCIe）",
        "PCIe / 总线（和 CPU 交换数据）",
    ]),
]


def main():
    print("GPU 内部硬件构成（按职责分 4 类）\n")
    for group, items in PARTS:
        print(f"【{group}】")
        for it in items:
            print(f"   - {it}")
        print()

    print("关键认知：")
    print("  1. 显存带宽常常比算力先到顶 —— 所以有 L2 缓存")
    print("  2. 多卡要通信就有互联 —— NVLink 是它的升级形态")
    print("  3. 所有调度最终落到 SM 上的 Warp Scheduler")


if __name__ == "__main__":
    main()
