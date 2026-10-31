CUDA_ARCH ?= sm_80
NVCC      ?= nvcc
NVDISASM  ?= nvdisasm
PYTHON    ?= python3

.PHONY: help check regs sass mma occupancy clean

help:
	@echo "make check      - 检查 nvcc / ptxas / nvdisasm 是否就绪"
	@echo "make regs       - 对比不同寄存器上限下的编译输出"
	@echo "make sass       - 反汇编，看 FFMA 与 HMMA"
	@echo "make occupancy  - 计算 SM 占用率（纯 CPU）"
	@echo "make clean      - 清理产物"

check:
	@which $(NVCC) || (echo "nvcc 未安装，先跑 01_env/setup_cuda_openeuler.sh"; exit 1)
	@$(NVCC) --version | tail -2
	@which $(NVDISASM) || echo "警告：nvdisasm 缺失，SASS 实验无法进行"
	@echo "nvidia-smi:"; which nvidia-smi || echo "  未找到（正常，本机无 GPU）"

# 两个 kernel 只差 __launch_bounds__，观察编译器如何按预算分配寄存器
# 注意：__launch_bounds__ 优先级高于 -maxrregcount，不要混用
regs:
	@$(NVCC) -arch=$(CUDA_ARCH) -Xptxas -v 02_ptx_sass/regs.cu -o /dev/null 2>&1 \
		| grep -E "Compiling entry|Used [0-9]+ registers|spill"

# 生成 cubin 再反汇编，对比两种矩阵乘的指令形态
sass:
	@$(NVCC) -arch=$(CUDA_ARCH) -cubin 02_ptx_sass/mma.cu -o /tmp/mma.cubin
	@echo "=== FFMA 出现次数（CUDA Core 路径）==="
	@$(NVDISASM) -c /tmp/mma.cubin | grep -c "FFMA" || true
	@echo "=== HMMA 出现次数（Tensor Core 路径）==="
	@$(NVDISASM) -c /tmp/mma.cubin | grep -c "HMMA" || true
	@echo
	@echo "=== 抽取几行看看 ==="
	@$(NVDISASM) -c /tmp/mma.cubin | grep -E "FFMA|HMMA" | head -8

# 不需要 GPU
occupancy:
	@$(PYTHON) 03_occupancy/occupancy.py --arch $(CUDA_ARCH) --threads 256

clean:
	@rm -f /tmp/mma.cubin
