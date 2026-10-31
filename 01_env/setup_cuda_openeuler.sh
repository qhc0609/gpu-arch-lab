#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# 在没有 GPU 的机器上装 CUDA Toolkit（只装编译器，不装驱动）
#
# 适用：VMware / 物理机，无 NVIDIA 显卡，openEuler 22.03 / 24.03
# 用途：只为了拿到 nvcc / ptxas / nvdisasm 三个工具做静态分析
# ---------------------------------------------------------------------------
set -euo pipefail

CUDA_VER="${CUDA_VER:-12.4.1}"
CUDA_RUN="cuda_${CUDA_VER}_535.104.05_linux.run"
CUDA_URL="https://developer.download.nvidia.com/compute/cuda/${CUDA_VER}/local_installers/${CUDA_RUN}"

echo "==> [1/4] 安装编译依赖"
sudo dnf install -y gcc gcc-c++ make wget

echo "==> [2/4] 检查磁盘空间（需要约 5GB）"
df -h /usr/local | tail -1

echo "==> [3/4] 下载 CUDA runfile"
if [ ! -f "/tmp/${CUDA_RUN}" ]; then
    wget -O "/tmp/${CUDA_RUN}" "${CUDA_URL}"
fi
chmod +x "/tmp/${CUDA_RUN}"

echo "==> [4/4] 静默安装 toolkit（--toolkit 表示只装编译工具，跳过驱动）"
sudo sh "/tmp/${CUDA_RUN}" --silent --toolkit --override

# 写入环境变量
if ! grep -q "cuda/bin" /etc/profile.d/cuda.sh 2>/dev/null; then
    sudo tee /etc/profile.d/cuda.sh >/dev/null <<'EOF'
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
EOF
fi

echo
echo "==> 安装完成，执行 source /etc/profile.d/cuda.sh 或重新登录"
echo "==> 验证："
echo "    nvcc --version      # 应有输出"
echo "    nvidia-smi          # 大概率 command not found，这是正常的"
echo
echo "说明：没有驱动意味着不能运行 kernel，但可以编译到 PTX/SASS，"
echo "      本文所有静态分析实验都不需要显卡。"
