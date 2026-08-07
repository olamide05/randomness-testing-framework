"""CSV exporter."""
import csv
from pathlib import Path


def export_csv(summary, output_path: Path = None) -> Path:
    if output_path is None:
        output_path = summary.experiment_directory / "report.csv"

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["test", "status", "passed", "total", "p_value", "proportion"])
        for t in summary.tests:
            writer.writerow([
                t.name,
                t.status,
                t.passed,
                t.total,
                "" if t.p_value is None else t.p_value,
                "" if t.proportion is None else t.proportion,
            ])

    return output_path