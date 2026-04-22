# ADC128S102 驱动优化验证

本目录用于验证 `b128s102rh_core` 的功能行为，重点检查：

- SPI 16-edge frame 时序
- `req_ch` 与 `ret_ch` 的一帧 pipeline 对齐关系
- 12bit 数据采样位序
- 连续多帧下 `done/data/ret_ch` 一致性

## 文件说明

- `b128s102rh_core.v`：待优化/验证的核心 RTL
- `adc128s102_model.v`：用于仿真的 ADC 行为模型
- `tb_b128s102rh_core.v`：测试平台（含 scoreboard）
- `run_adc_demo.sh`：一键仿真脚本
- `validate_adc.py`：仿真日志自动校验脚本

## 运行方式

```bash
./run_adc_demo.sh
./validate_adc.py out/adc_sim.log
```

## 产物

默认输出到 `out/`：

- `adc_simv`：仿真可执行文件
- `adc_sim.log`：仿真日志
- `adc128s102.vcd` / `adc128s102.fst`：波形文件
