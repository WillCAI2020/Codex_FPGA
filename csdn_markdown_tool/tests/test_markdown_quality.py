from pathlib import Path
import re


RESULT_FILE = Path(__file__).resolve().parents[1] / "result_132397061.md"


def test_no_nested_fence():
    content = RESULT_FILE.read_text(encoding="utf-8")
    assert "```\n```" not in content


def test_verilog_fragment_continuous():
    content = RESULT_FILE.read_text(encoding="utf-8")
    # 关键片段应连续，而不是 token 逐行拆开
    assert re.search(r"reg\s*\[\s*2\s*:\s*0\s*\]\s*r_Channel\s*;", content)
    assert re.search(r"always@\s*\(\s*posedge\s+Clk\s+or\s+negedge\s+Rst_n\s*\)", content)
