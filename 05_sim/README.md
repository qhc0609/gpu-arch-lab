# 05_sim —— 可选：周期级仿真

前三层（编译期静态分析 + 纯数学计算 + 云上取证）已经足够支撑一篇文章。
这一层是加分项：在没有 GPU 的机器上，用仿真器拿到 SM 内部的周期级数据，
比如每个 warp 卡在哪个 stall 原因上。

## 工具选择

**GPGPU-Sim** 是最成熟的选择，纯 CPU 运行，能输出：

- 每个 SM 的 warp 发射情况
- stall 原因分布（memory dependency / barrier / not selected ...）
- 实际占用率与理论占用率的差异

代价是安装麻烦：它对 gcc 版本敏感，通常需要 gcc-9 或更早，
在 openEuler 24.03（gcc 12+）上要额外准备老编译器。

**Accel-Sim** 是 GPGPU-Sim 的现代分支，支持较新的 CUDA 版本，可以优先尝试。

## 大致流程

```bash
git clone https://github.com/accel-sim/accel-sim-framework.git
cd accel-sim-framework
export CUDA_INSTALL_PATH=/usr/local/cuda
source ./gpu-simulator/setup_environment.sh
# 用官方提供的 rodinia / polybench 配置跑一个 GEMM
```

## 判断标准

如果跑通了，值得写进文章的点是这一条：

> 理论 occupancy 100% 的 kernel，实测 warp 有 40% 的时间在等内存。

这一句能把"为什么 GPU 要堆这么多计算单元"讲透——**计算单元不是用来跑满的，
是用来在等待时还有活干的**。这才是延迟隐藏的本质。

## 如果装不上

不必勉强。用 `ncu`（Nsight Compute）在云上那台 T4 上跑一次，
也能拿到 `Achieved Occupancy` 和 `Warp State Statistics`，
虽然要花几块钱，但省下的时间远比折腾仿真器划算。
