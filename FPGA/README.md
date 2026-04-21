# FPGA 工具验证目录

本目录用于进行最小化 FPGA/Verilog 工具链验证，包含：

1. `iverilog` 编译+仿真
2. 生成波形 `counter.vcd` / `counter.fst`
3. 使用 `gtkwave` 打开波形，并导出窗口截图 `waveform.png`
4. 使用脚本校验时序是否符合设计预期

> 注意：仓库**不提交**任何仿真产物（二进制/波形/截图）。
> 运行后生成文件统一放在 `out/`（默认）目录。

## 例程说明

- 设计文件：`counter.v`
- 测试平台：`tb_counter.v`
- 功能：4-bit 计数器，复位释放后在时钟上升沿每 10ns 加 1。

## 运行步骤

```bash
./run_demo.sh
./validate_timing.py
```

你也可以自定义输出目录：

```bash
./run_demo.sh out_test
./validate_timing.py out_test/sim.log
```

## 输出文件（默认在 `out/`）

- `sim.log`：仿真日志
- `counter.vcd` / `counter.fst`：波形文件
- `waveform.png`：gtkwave 波形截图

