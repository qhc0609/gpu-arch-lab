#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# probe.sh —— 在云上按量 GPU 实例里跑一次，把物理参数取证回来
#
# 建议：选最便宜的 T4 实例即可，跑完立刻释放，成本通常在几块钱以内。
# ---------------------------------------------------------------------------
set -euo pipefail

echo "===== 1. 驱动与设备 ====="
nvidia-smi --query-gpu=name,compute_cap,memory.total,clocks.max.sm --format=csv

echo
echo "===== 2. 关键规格 ====="
nvidia-smi --query-gpu=name,compute_cap,power.limit,power.max_limit --format=csv

echo
echo "===== 3. 拓扑 ====="
nvidia-smi topo -m || echo "（单卡实例无拓扑信息）"

echo
echo "===== 4. deviceQuery 详细输出 ====="
if [ ! -x ./device_query ]; then
    echo "先编译：nvcc -arch=sm_$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | tr -d '.') device_query.cu -o device_query"
    exit 1
fi
./device_query

echo
echo "===== 5. 建议截图留存 ====="
echo "  - nvidia-smi 顶部表格（GPU 型号 + 显存）"
echo "  - device_query 的 SM 数量与每 SM 寄存器数"
echo "这两张图就是文章里唯一的真机证据。"
