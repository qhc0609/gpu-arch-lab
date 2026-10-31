// ---------------------------------------------------------------------------
// mma.cu —— 同一个矩阵乘，两种实现，用来对比 CUDA Core 与 Tensor Core 的指令形态
//
//   gemm_fma  : 标量循环，SASS 里是一串 FFMA（CUDA Core 一条一条算）
//   gemm_wmma : 调用 wmma API，SASS 里是 HMMA.16816.F32（Tensor Core 一条算一小块）
//
// 编译（不需要 GPU）：
//   nvcc -arch=sm_80 -cubin mma.cu -o mma.cubin
//   nvdisasm -c mma.cubin | grep -E "FFMA|HMMA"
// ---------------------------------------------------------------------------
#include <mma.h>
#include <cuda_fp16.h>

using namespace nvcuda;

// ---- 版本 A：纯标量，走 CUDA Core ----
// 每个线程算一个输出元素，内层循环做 K 次乘加
__global__ void gemm_fma(const half* __restrict__ A,
                         const half* __restrict__ B,
                         float* __restrict__ C,
                         int M, int N, int K)
{
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    if (row >= M || col >= N) return;

    float acc = 0.0f;
    for (int k = 0; k < K; ++k) {
        acc += __half2float(A[row * K + k]) * __half2float(B[k * N + col]);
    }
    C[row * N + col] = acc;
}

// ---- 版本 B：wmma，走 Tensor Core ----
// 一个 warp 负责输出矩阵里的一块 16x16
// 前提：M、N 是 16 的倍数，K 是 16 的倍数
__global__ void gemm_wmma(const half* __restrict__ A,
                          const half* __restrict__ B,
                          float* __restrict__ C,
                          int M, int N, int K)
{
    int tiles_n   = N / 16;
    int global_warp = (blockIdx.x * blockDim.x + threadIdx.x) >> 5;
    int tile_m    = global_warp / tiles_n;
    int tile_n    = global_warp % tiles_n;
    if (tile_m * 16 >= M) return;

    wmma::fragment<wmma::matrix_a, 16, 16, 16, half, wmma::row_major> frag_a;
    wmma::fragment<wmma::matrix_b, 16, 16, 16, half, wmma::row_major> frag_b;
    wmma::fragment<wmma::accumulator, 16, 16, 16, float>              frag_c;

    wmma::fill_fragment(frag_c, 0.0f);

    for (int k = 0; k < K; k += 16) {
        wmma::load_matrix_sync(frag_a, A + tile_m * 16 * K + k, K);
        wmma::load_matrix_sync(frag_b, B + k * N + tile_n * 16, N);
        // 这一行对应 SASS 里的 HMMA.16816.F32
        wmma::mma_sync(frag_c, frag_a, frag_b, frag_c);
    }

    wmma::store_matrix_sync(C + tile_m * 16 * N + tile_n * 16,
                            frag_c, N, wmma::mem_row_major);
}
