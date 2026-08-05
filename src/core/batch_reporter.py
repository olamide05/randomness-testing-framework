import json
from pathlib import Path
from typing import List
from dataclasses import dataclass


@dataclass
class BatchReporter:
    summaries: List
    
    def _collect_tests(self) -> List[str]:
        """Get all unique test names across all runs."""
        tests = set()
        for s in self.summaries:
            for t in s.tests:
                tests.add(t.name)
        return sorted(tests)
    
    def _get_test_result(self, summary, test_name: str):
        """Get a specific test result from a summary."""
        for t in summary.tests:
            if t.name == test_name:
                return t
        return None
    
    def generate_md(self, output_path: Path):
        """Generate Markdown comparison table."""
        tests = self._collect_tests()
        
        lines = [
            "# NIST STS Batch Comparison",
            "",
            "| Generator | Overall | " + " | ".join(t.replace("_", " ").title() for t in tests) + " |",
            "|" + "-" * 10 + "|" + "-" * 8 + "|" + "|".join("-" * 12 for _ in tests) + "|",
        ]
        
        for summary in self.summaries:
            overall = "PASS" if summary.overall_status == "pass" else "FAIL" if summary.overall_status == "fail" else "N/A"
            row = f"| {summary.generator:8s} | {overall:6s} |"
            
            for test_name in tests:
                t = self._get_test_result(summary, test_name)
                if t and t.total > 0:
                    status = f"{t.passed}/{t.total}"
                elif t:
                    status = "SKIP"
                else:
                    status = "N/A"
                row += f" {status:10s} |"
            
            lines.append(row)
        
        with open(output_path, "w") as f:
            f.write("\n".join(lines) + "\n")
    
    def generate_json(self, output_path: Path):
        """Generate JSON comparison."""
        data = []
        for summary in self.summaries:
            data.append({
                "generator": summary.generator,
                "overall_status": summary.overall_status,
                "experiment_directory": str(summary.experiment_directory),
                "tests": [
                    {
                        "name": t.name,
                        "status": t.status,
                        "passed": t.passed,
                        "total": t.total,
                        "p_value": t.p_value,
                        "proportion": t.proportion
                    }
                    for t in summary.tests
                ]
            })
        
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def generate_html(self, output_path: Path):
        """Generate interactive HTML comparison dashboard."""
        tests = self._collect_tests()
        
        header_cols = "<th>Generator</th><th>Overall</th>"
        for test_name in tests:
            header_cols += f"<th>{test_name.replace('_', ' ').title()}</th>"
        
        rows = ""
        for summary in self.summaries:
            overall_class = "pass" if summary.overall_status == "pass" else "fail" if summary.overall_status == "fail" else "skip"
            overall_text = summary.overall_status.upper()
            
            row = f'<tr><td class="gen">{summary.generator}</td>'
            row += f'<td class="{overall_class}">{overall_text}</td>'
            
            for test_name in tests:
                t = self._get_test_result(summary, test_name)
                if t and t.total > 0:
                    cell_class = "pass" if t.status == "pass" else "fail"
                    cell_text = f"{t.passed}/{t.total}"
                elif t:
                    cell_class = "skip"
                    cell_text = "SKIP"
                else:
                    cell_class = "skip"
                    cell_text = "N/A"
                
                row += f'<td class="{cell_class}">{cell_text}</td>'
            
            row += "</tr>\n"
            rows += row
        
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>NIST STS Batch Comparison</title>
<style>
:root {{ --pass: #22c55e; --fail: #ef4444; --skip: #9ca3af; --bg: #f5f5f5; }}
body {{ font-family: system-ui, -apple-system, sans-serif; max-width: 1400px; margin: 40px auto; padding: 20px; background: var(--bg); }}
h1 {{ margin: 0 0 24px 0; font-size: 28px; }}
.card {{ background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
th {{ background: #1f2937; color: white; padding: 12px; text-align: left; font-weight: 600; position: sticky; top: 0; }}
td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; }}
tr:hover td {{ background: #f9fafb; }}
.gen {{ font-weight: 600; color: #1f2937; }}
.pass {{ background: #dcfce7; color: #166534; font-weight: 600; }}
.fail {{ background: #fee2e2; color: #991b1b; font-weight: 600; }}
.skip {{ background: #f3f4f6; color: #6b7280; }}
td.pass, td.fail, td.skip {{ text-align: center; border-radius: 4px; }}
</style>
</head>
<body>
<div class="card">
<h1>NIST STS Batch Comparison</h1>
<table>
<thead>
<tr>{header_cols}</tr>
</thead>
<tbody>
{rows}
</tbody>
</table>
</div>
</body>
</html>"""
        
        with open(output_path, "w") as f:
            f.write(html)