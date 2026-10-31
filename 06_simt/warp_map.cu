// ---------------------------------------------------------------------------
// warp_map.cu —— 观察 threadIdx / blockIdx / warp / lane 的关系
//
// 编译（需要 nvcc，不需要运行时有 GPU 也行，但要有卡才能跑）：
//   nvcc -arch=sm_80 warp_map.cu -o warp_map
// 运行：
//   ./warp_map
//
// 这里启动 <<<grid=2, block=64>>>：
//   2 个 block，每 block 64 线程 = 2 个 warp
//   总共 128 线程 = 4 个 warp
//
// 为了输出有序，kernel 只负责算，主机端按 gid 顺序打印。
// 想验证和 06_simt/warp_map.py 完全一致，对比两边输出即可。
// ---------------------------------------------------------------------------
#include <cstdio>

__global__ void fill_map(int* gid, int* warp, int* lane, int n)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;  // 全局线程号
    if (i < n) {
        gid[i]  = i;
        warp[i] = i / 32;      // 每 32 个连续线程一个 warp
        lane[i] = i % 32;      // warp 内位置
    }
}

int main()
{
    const int BLOCK = 64;
    const int GRID  = 2;
    const int N     = BLOCK * GRID;

    int *d_gid, *d_warp, *d_lane;
    cudaMalloc(&d_gid,  N * sizeof(int));
    cudaMalloc(&d_warp, N * sizeof(int));
    cudaMalloc(&d_lane, N * sizeof(int));

    fill_map<<<GRID, BLOCK>>>(d_gid, d_warp, d_lane, N);
    cudaDeviceSynchronize();

    int h_gid[N], h_warp[N], h_lane[N];
    cudaMemcpy(h_gid,  d_gid,  N * sizeof(int), cudaMemcpyDeviceToHost);
    cudaMemcpy(h_warp, d_warp, N * sizeof(int), cudaMemcpyDeviceToHost);
    cudaMemcpy(h_lane, d_lane, N * sizeof(int), cudaMemcpyDeviceToHost);

    printf("launch <<<grid=%d, block=%d>>>  %d threads, %d warps\n\n",
           GRID, BLOCK, N, N / 32);
    printf("%4s %5s %6s %4s %4s\n", "gid", "block", "thread", "warp", "lane");
    printf("----------------------------------\n");
    for (int i = 0; i < N; ++i) {
        printf("%4d %5d %6d %4d %4d\n",
               h_gid[i], i / BLOCK, i % BLOCK, h_warp[i], h_lane[i]);
        if (h_lane[i] == 31)
            printf("----------------------------------\n");
    }

    cudaFree(d_gid);
    cudaFree(d_warp);
    cudaFree(d_lane);
    return 0;
}
