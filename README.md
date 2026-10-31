# gpu-arch-lab

在没有 GPU 的机器上讲清 GPU 内部架构。

配套文章：《没有显卡，我把 GPU 拆开看了》

## 这个仓库解决什么问题

讲 SM、CUDA Core、Tensor Core，通常需要一张显卡。但把这件事拆开看，
**大部分证据其实在编译期就能拿到**：

| 证据 | 需要 GPU | 说明 |
|---|---|---|
| 寄存器用量、shared memory 分配 | 否 | `nvcc -Xptxas -v` 编译期输出 |
| CUDA Core / Tensor Core 的指令形态 | 否 | `nvdisasm` 反汇编 SASS |
| SM 的驻留能力（occupancy） | 否 | 纯数学计算 |
| SM 的物理数量、实测占用率 | 是 | 云上按量实例跑一次即可 |

所以整个流程分四层，前三层在本地虚拟机里完成。

## 目录

```
01_env/          无卡安装 CUDA Toolkit（只装编译器）
02_ptx_sass/     regs.cu 寄存器实验 / mma.cu 指令对比
03_occupancy/    纯 Python 计算 SM 占用率
04_cloud_probe/  云上取证的 deviceQuery
05_sim/          可选：GPGPU-Sim 周期级仿真
```

## 快速开始

```bash
# 1. 环境（openEuler，无 GPU）
sudo bash 01_env/setup_cuda_openeuler.sh
source /etc/profile.d/cuda.sh
make check

# 2. 寄存器实验：两个 kernel 只差 __launch_bounds__，看预算如何变成寄存器数
make regs

# 3. 指令对比：FFMA vs HMMA
make sass

# 4. 占用率曲线（纯 CPU）
make occupancy
```

云上取证部分见 `04_cloud_probe/probe.sh`，建议选最便宜的 T4 实例，
跑完立即释放。

## 关键结论

1. **SM 是资源受限的物理单元**。65536 个寄存器是硬上限，改不了。
   每个线程多用 8 个寄存器，能同时驻留的 warp 就少一批。

2. **Tensor Core 是一条指令，不是一堆小核**。SASS 里它长这样：
   `HMMA.16816.F32 R4, R8, R12, R16`，一条指令完成 16×8×16 的乘加。

3. **计算单元堆这么多，是为了在等待时还有活干**。
   occupancy 100% 不代表跑满，而是代表有足够的 warp 可以切换去掩盖内存延迟。

## 环境

- openEuler 22.03 / 24.03（VMware 虚拟机即可）
- CUDA Toolkit 12.x（只装 toolkit，不装驱动）
- Python 3.8+（occupancy 脚本只用标准库）
- 真机实验：任意 NVIDIA GPU，T4 足够

## 许可

MIT
