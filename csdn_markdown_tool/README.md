# CSDN 转 Markdown 工具

该目录用于将 CSDN 文章提取为较干净的 Markdown，并保留来源信息。

## 工具目录说明

- `csdn_to_markdown.py`：主脚本，支持直连抓取、可选 Playwright 渲染与 r.jina.ai 兜底。
- `result_132397061.md`：示例链接转换后的输出文件。
- `tests/test_markdown_quality.py`：结果质量回归测试（嵌套围栏、Verilog 连续性）。

## 基本运行命令

```bash
python3 csdn_markdown_tool/csdn_to_markdown.py \
  "https://blog.csdn.net/qq_46140768/article/details/132397061" \
  -o csdn_markdown_tool/result_132397061.md
```

## 可选参数

- `--cookies cookies.txt`：附带 Cookie Header（文本文件中写完整 Cookie 字符串）。
- `--use-playwright`：启用 Playwright 渲染页面后再提取。
- `--no-jina-fallback`：禁用 r.jina.ai 兜底；直连失败时直接报错退出。

## 质量检查命令

```bash
python3 -m pytest csdn_markdown_tool/tests/test_markdown_quality.py
```
