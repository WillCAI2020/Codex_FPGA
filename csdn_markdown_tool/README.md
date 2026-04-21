# CSDN 转 Markdown 工具

该目录集中放置 CSDN 转 MD 的相关文件。

## 文件说明

- `csdn_to_markdown.py`：主脚本，支持直连抓取与 r.jina.ai 自动兜底。
- `result_132397061.md`：测试链接的转换结果。

## 使用方式

```bash
python3 csdn_markdown_tool/csdn_to_markdown.py "https://blog.csdn.net/qq_46140768/article/details/132397061" -o csdn_markdown_tool/article.md
```

可选参数：

- `--cookies cookies.txt`：附带 Cookie Header。
- `--use-playwright`：使用 Playwright 渲染后抓取。
- `--no-jina-fallback`：禁用 r.jina.ai 兜底。
