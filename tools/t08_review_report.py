"""Sinh bảng số liệu cho report mục 07 (Human & decision) từ output thật của pipeline.

Chạy:  python -m tools.t08_review_report            (mặc định đọc out/poc, ghi reports/sections/07_generated_tables.md)
Số liệu CHỈ lấy từ file output, không gõ tay.
"""
import argparse
import json
from pathlib import Path

import pandas as pd


def md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join("" if pd.isna(v) else str(v).replace("|", "/") for v in row) + " |")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="out/poc")
    ap.add_argument("--out", default="reports/sections/07_generated_tables.md")
    a = ap.parse_args()
    run = Path(a.run)

    actions = pd.read_csv(run / "actions.csv")
    reviewed_path = run / "review_queue_reviewed.csv"
    reviewed = pd.read_csv(reviewed_path) if reviewed_path.exists() else pd.DataFrame()
    dlog = pd.read_csv(run / "decision_log.csv")
    dlog = dlog.drop_duplicates(subset="scope", keep="last")      # decision_log nối thêm mỗi lần chạy -> lấy lần cuối
    audit = [json.loads(x) for x in (run / "audit_log.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]

    # Bảng 1: theo request
    rows = []
    for rid, g in actions.groupby("request_id", sort=True):
        exc = g[g.action != "delete"]
        d = dlog[dlog.scope == rid].iloc[0]
        rows.append({"request": rid, "artefact trong phạm vi": len(g), "delete": int((g.action == "delete").sum()),
                     "retain_legal_hold": int((g.action == "retain_legal_hold").sum()),
                     "escalate": int((g.action == "escalate").sum()),
                     "ngoại lệ đã ký": int((exc.reviewed_by.fillna("") != "").sum()),
                     "ngoại lệ chưa ký": int((exc.reviewed_by.fillna("") == "").sum()),
                     "quyết định": d.status, "reason_code": d.reason_code})
    t1 = pd.DataFrame(rows)

    # Bảng 2: các dòng đã duyệt
    if len(reviewed) and "reviewer_decision" in reviewed:
        r = reviewed[reviewed.reviewer_decision.notna() & (reviewed.reviewer_decision.astype(str).str.strip() != "")]
        t2 = r[["item_id", "reason", "suggested_action", "reviewer", "reviewer_decision", "review_note", "reviewed_at"]]
    else:
        t2 = pd.DataFrame(columns=["item_id", "reason", "suggested_action", "reviewer", "reviewer_decision", "review_note", "reviewed_at"])

    # Bảng 3: hàng chờ theo lý do
    q = pd.read_csv(run / "review_queue.csv")
    t3 = q.reason.value_counts().rename_axis("reason").reset_index(name="số dòng")

    n_rev = sum(1 for e in audit if str(e.get("action", "")).startswith("review:"))
    other = dlog[~dlog.scope.isin(t1.request)][["scope", "status", "reason_code", "reason"]]
    parts = [
        "<!-- Sinh tự động bởi tools/t08_review_report.py; không sửa tay -->",
        f"**Bảng 7.1 · Quyết định theo request** (nguồn: `{run}/actions.csv`, `decision_log.csv`)\n\n{md(t1)}",
        f"**Bảng 7.2 · Dòng đã được người duyệt xử lý** (nguồn: `{reviewed_path}`) — {len(t2)} dòng\n\n{md(t2)}",
        f"**Bảng 7.3 · Hàng chờ theo lý do** (nguồn: `{run}/review_queue.csv`, tổng {len(q)} dòng)\n\n{md(t3)}",
        f"**Quyết định cấp hệ thống / catalog:**\n\n{md(other)}",
        f"**Audit:** `audit_log.jsonl` có {len(audit)} dòng, trong đó {n_rev} dòng `review:*`.",
    ]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print(f"wrote {out}  (requests={len(t1)}, reviewed_rows={len(t2)}, review_audit_lines={n_rev})")


if __name__ == "__main__":
    main()
