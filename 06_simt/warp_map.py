#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
warp_map.py —— 不需要显卡，用公式复现 threadIdx / blockIdx / warp / lane 的映射

CUDA 里全局线程号的定义是：
    gid = blockIdx.x * blockDim.x + threadIdx.x

反过来：
    block  = gid // blockDim.x
    thread = gid  % blockDim.x
    warp   = gid // 32          # 每 32 个连续线程组成一个 warp
    lane   = gid  % 32          # 在 warp 内的位置

运行：python3 warp_map.py
"""

GRID = 2      # 2 个 block
BLOCK = 64    # 每个 block 64 线程 = 2 个 warp


def simulate(grid, block):
    total = grid * block
    warps = total // 32
    print(f"launch <<<grid={grid}, block={block}>>>  "
          f"共 {total} 线程, {warps} 个 warp\n")
    print(f"{'gid':>4} {'block':>5} {'thread':>6} {'warp':>4} {'lane':>4}")
    print("-" * 34)
    for gid in range(total):
        block_id = gid // block
        thread_id = gid % block
        warp = gid // 32
        lane = gid % 32
        # 每 32 行打一条分隔，方便肉眼看出 warp 边界
        print(f"{gid:>4} {block_id:>5} {thread_id:>6} {warp:>4} {lane:>4}")
        if lane == 31:
            print("-" * 34)


if __name__ == "__main__":
    simulate(GRID, BLOCK)
