// ---------------------------------------------------------------------------
// regs.cu —— 观察寄存器预算如何决定 SM 的驻留能力
//
// 编译（不需要 GPU）：
//   nvcc -arch=sm_80 -Xptxas -v regs.cu -o /dev/null
//
// 两个 kernel 的算法完全一样，只差 __launch_bounds__ 的第二个参数：
//
//   bound6: 每 SM 至少 6 个 block -> 65536/(256*6)=42.67 -> 对齐 8 -> 40 个寄存器
//   bound8: 每 SM 至少 8 个 block -> 65536/(256*8)=32    -> 对齐 8 -> 32 个寄存器
//
// 所以 ptxas 报的寄存器数是算得出来的，不是碰运气。
// 注意：__launch_bounds__ 的优先级高于 -maxrregcount，两者不要混用。
// ---------------------------------------------------------------------------
#include <cstdio>

#define BODY                                                     \
    int i = blockIdx.x * blockDim.x + threadIdx.x;               \
    if (i >= n) return;                                          \
    float x0 = a[i],    y0 = b[i];                               \
    float x1 = x0 * y0, y1 = x0 + y0;                            \
    float x2 = x1 - y1, y2 = x1 * 0.5f;                          \
    float x3 = x2 * y2, y3 = x2 + y2;                            \
    float x4 = x3 / (y3 + 1.0f);                                 \
    float x5 = x4 * x4, y4 = x4 - y3;                            \
    float x6 = x5 + y4, y5 = x5 * y4;                            \
    float x7 = x6 - y5, y6 = x6 + y5;                            \
    c[i] = x7 + y6 + x3 + y3;

__global__ void __launch_bounds__(256, 6)
heavy_bound6(const float* __restrict__ a, const float* __restrict__ b,
             float* __restrict__ c, int n)
{
    BODY
}

__global__ void __launch_bounds__(256, 8)
heavy_bound8(const float* __restrict__ a, const float* __restrict__ b,
             float* __restrict__ c, int n)
{
    BODY
}

int main()
{
    // 无卡机器上只做编译检查，不 launch。
    std::printf("compile-only demo: nvcc -arch=sm_80 -Xptxas -v regs.cu\n");
    return 0;
}
