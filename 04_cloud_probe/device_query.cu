// ---------------------------------------------------------------------------
// device_query.cu —— 读取 GPU 的物理参数（这一项必须有真卡）
//
// 编译：nvcc -arch=sm_80 device_query.cu -o device_query
// 运行：./device_query
//
// 这个程序回答的是"这台机器上的 SM 到底有多少个、每个 SM 有多少资源"，
// 是本地静态分析补不上的那一半。
// ---------------------------------------------------------------------------
#include <cstdio>
#include <cuda_runtime.h>

#define CHECK(x) do {                                              \
    cudaError_t e = (x);                                           \
    if (e != cudaSuccess) {                                        \
        std::printf("[FAIL] %s -> %s\n", #x, cudaGetErrorString(e)); \
        return 1;                                                  \
    }                                                              \
} while (0)

int main()
{
    int dev = 0;
    CHECK(cudaGetDevice(&dev));

    cudaDeviceProp p{};
    CHECK(cudaGetDeviceProperties(&p, dev));

    std::printf("GPU                 : %s\n", p.name);
    std::printf("Compute Capability  : %d.%d\n", p.major, p.minor);
    std::printf("\n--- 芯片级 ---\n");
    std::printf("SM 数量             : %d\n", p.multiProcessorCount);
    std::printf("显存                : %.1f GB\n", p.totalGlobalMem / 1073741824.0);
    std::printf("显存位宽            : %d bit\n", p.memoryBusWidth);
    std::printf("L2 缓存             : %d KB\n", p.l2CacheSize / 1024);

    std::printf("\n--- 单个 SM 内部 ---\n");
    std::printf("每 SM 寄存器        : %d 个\n", p.regsPerMultiprocessor);
    std::printf("每 SM shared memory : %zu KB\n", p.sharedMemPerMultiprocessor / 1024);
    std::printf("每 SM 最大线程      : %d\n", p.maxThreadsPerMultiProcessor);
    std::printf("每 SM 最大常驻 block: %d\n", p.maxBlocksPerMultiProcessor);
    std::printf("warp 大小           : %d 线程\n", p.warpSize);

    std::printf("\n--- 单个 block ---\n");
    std::printf("每 block 最大线程   : %d\n", p.maxThreadsPerBlock);
    std::printf("每 block 最大 shared: %zu KB\n", p.sharedMemPerBlock / 1024);

    // 由 SM 数推总核心数（FP32）
    std::printf("\n--- 推算 ---\n");
    std::printf("按每 SM 128 个 FP32 单元估算，总 CUDA Core 约 : %d\n",
                p.multiProcessorCount * 128);

    return 0;
}
