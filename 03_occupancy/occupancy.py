#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
occupancy.py —— 纯 CPU 计算 SM 的占用率，不需要任何 GPU

思路：SM 的寄存器、shared memory、warp 槽位都是固定值，
      给定每个线程用多少寄存器、每个 block 多少线程，
      就能算出这个 SM 最多同时驻留几个 block、多少个 warp。

用法：
    python3 occupancy.py                    # 打印默认曲线
    python3 occupancy.py --arch sm_86 --threads 256
    python3 occupancy.py --regs 40 --threads 512 --arch sm_90
"""

import argparse

# 各架构 SM 的硬件资源上限（来自 CUDA C Programming Guide 的
# "Compute Capability Technical Specifications" 表）
ARCH = {
    "sm_75": dict(regs=65536, smem=65536, warps=32, blocks=16, threads=1024),   # T4 / RTX 20
    "sm_80": dict(regs=65536, smem=163840, warps=64, blocks=32, threads=2048),  # A100
    "sm_86": dict(regs=65536, smem=102400, warps=48, blocks=16, threads=1536),  # A10 / RTX 30
    "sm_89": dict(regs=65536, smem=102400, warps=48, blocks=32, threads=1536),  # RTX 40
    "sm_90": dict(regs=65536, smem=233472, warps=64, blocks=32, threads=2048),  # H100
}

WARP = 32
REG_ALLOC_UNIT = 8   # 寄存器按 warp 粒度（256 个）分配，折合每线程 8 个的倍数


def occupancy(regs_per_thread: int, threads_per_block: int,
              smem_per_block: int = 0, arch: str = "sm_80") -> dict:
    c = ARCH[arch]

    warps_per_block = (threads_per_block + WARP - 1) // WARP

    # 寄存器分配向上取整到分配粒度
    regs_rounded = ((regs_per_thread + REG_ALLOC_UNIT - 1) // REG_ALLOC_UNIT) * REG_ALLOC_UNIT
    regs_per_block = regs_rounded * threads_per_block

    by_regs  = c["regs"] // regs_per_block if regs_per_block else c["blocks"]
    by_smem  = c["smem"] // smem_per_block if smem_per_block else c["blocks"]
    by_warps = c["warps"] // warps_per_block if warps_per_block else c["blocks"]
    by_limit = c["blocks"]

    blocks = max(0, min(by_regs, by_smem, by_warps, by_limit))
    active_warps = blocks * warps_per_block

    return {
        "arch": arch,
        "regs_rounded": regs_rounded,
        "blocks": blocks,
        "active_warps": active_warps,
        "max_warps": c["warps"],
        "occupancy": active_warps / c["warps"],
        "bound_by": min(
            [("regs", by_regs), ("smem", by_smem),
             ("warps", by_warps), ("blocks", by_limit)],
            key=lambda kv: kv[1],
        )[0],
    }


def bar(ratio: float, width: int = 40) -> str:
    filled = int(round(ratio * width))
    return "#" * filled + "." * (width - filled)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", default="sm_80", choices=sorted(ARCH))
    ap.add_argument("--threads", type=int, default=256)
    ap.add_argument("--smem", type=int, default=0, help="每 block 的 shared memory 字节数")
    ap.add_argument("--regs", type=int, default=None, help="只算单个寄存器取值")
    args = ap.parse_args()

    if args.regs is not None:
        r = occupancy(args.regs, args.threads, args.smem, args.arch)
        print(f"arch={r['arch']}  threads/block={args.threads}  "
              f"regs/thread={args.regs} (对齐后 {r['regs_rounded']})")
        print(f"  每 SM 驻留 block 数 : {r['blocks']}")
        print(f"  活跃 warp 数        : {r['active_warps']} / {r['max_warps']}")
        print(f"  占用率              : {r['occupancy']*100:.1f}%  [{bar(r['occupancy'])}]")
        print(f"  瓶颈                : {r['bound_by']}")
        return

    print(f"架构 {args.arch}  每 block {args.threads} 线程  "
          f"shared mem {args.smem} 字节\n")
    print(f"{'regs':>6} {'blocks':>7} {'warps':>7} {'occupancy':>10}  瓶颈")
    print("-" * 62)
    for regs in (24, 32, 40, 48, 64, 96, 128, 168, 255):
        r = occupancy(regs, args.threads, args.smem, args.arch)
        print(f"{regs:>6} {r['blocks']:>7} {r['active_warps']:>7} "
              f"{r['occupancy']*100:>9.1f}%  {r['bound_by']}")


if __name__ == "__main__":
    main()
