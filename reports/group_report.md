# Group Report — Day 06 Data Lab (Field-to-Release PoC)

> Chi tiết từng mục nằm trong `reports/sections/`. Số liệu lấy từ file do script sinh (`reports/selfcheck/*.json`, `reports/selfcheck/table1_selfcheck.md`, `out/poc/*`). Tài liệu học tập trên dữ liệu synthetic, không phải tư vấn pháp lý.

## 00 · Header

| Mục | Giá trị |
|---|---|
| Group ID | GiCungDuoc |
| Challenge | T08 · Retention & Delete Request Simulator |
| Thành viên (4) + vai trò | 1. Nguyễn Văn Đại (Lead / Integrator, kiêm Human review + report) · 2. Nguyễn Quốc Vương (Core algorithm) · 3. Phan Đình Giáp (Data & fixtures + QA / metric) · 4. Lê Duy Bảo (Human review + report) |
| Git URL | https://github.com/Pennywise111124/K5-Day6-L2-GiCungDuoc-DataGovernanceAndPrivacy |
| Tag `demo-180m` (commit) | `81a5576` (đã push) |
| Tag `final-24h` (commit) | `__________` (điền sau khi gắn tag) |
| Deadline (giờ VN) | +24h sau buổi lab 14/11/2026 |

## 01 · Problem statement

- **Ai bị ảnh hưởng:** người gửi yêu cầu xoá (xoá thiếu → vi phạm quyền xoá) và bên giữ dữ liệu / người khác (xoá nhầm → huỷ bằng chứng đang legal hold, mất dữ liệu người khác, không hoàn tác).
- **Điểm nghẽn:** dữ liệu một người nằm rải trong raw → backup → frame → crop / embedding / annotation → training export; xoá theo tên file bỏ sót phần dẫn xuất.
- **Đầu vào → đầu ra:** `requests.json` (10 yêu cầu) + `data_graph.json` (212 artefact) → `actions.csv` (158 dòng: delete / retain_legal_hold / escalate) + `audit_log.jsonl` + quyết định từng request.
- **Tiêu chí GO / HOLD / REWORK:** GO khi mọi ngoại lệ đã được ký và không còn legal hold; HOLD khi còn ngoại lệ chưa ký hoặc còn hold; REWORK khi catalog lineage mâu thuẫn (xem `sections/07_human_decision.md` §7.3).
- **Giả định cần DPO / pháp chế xác nhận:** chính sách R1–R8 và hold thừa kế xuống cả cây con.

## 02 · Data & provenance

Xem `sections/02_data_provenance_C.md` và `sections/02_algorithm_part_B.md`.

| Split | N | Nguồn / link | License | Synthetic? |
|---|---|---|---|---|
| eval (không chia) | 10 request · 212 artefact · 158 cặp | `fixtures/t08_deletion/` | CC0-1.0 | Có |

- Seed 42; không chia dev/eval vì không có tham số để tune. `manifest.csv` verified (`python -m tools.verify_manifests`; sai hash → exit 2).
- Không dùng dữ liệu thật. Bộ chấm `reports/selfcheck/t08_expected.csv` do C gán tay và đóng băng trước khi chạy PoC.

## 03 · Research & design

Xem `sections/03_research_design.md` (references, data flow, trade-off). Không dùng model / weights; chạy offline.

## 04 · Baseline vs PoC

Xem `sections/04_baseline_vs_poc.md`. Baseline = xoá raw theo filename (`src.t08.baseline`); PoC = lineage + R1–R8 + hàng chờ DPO (`src.pipeline`). Cùng dữ liệu, seed 42, 158 cặp.

> **Lưu ý quan trọng:** các số dưới đây được chấm trên **self-check do nhóm tự gán**, không phải ground truth của giảng viên (repo học viên không có `gt/`). Chúng chứng minh code làm đúng chính sách của nhóm, không chứng minh chính sách đúng luật.

| Metric (unit) | Baseline | PoC | Ghi chú |
|---|---|---|---|
| **Primary:** Deletion Completeness | 0.0784 (8/102) | 1.0000 (102/102) | higher is better |
| False-delete count | 2 | 0 | lower is better; baseline xoá `a0043`, `a0099` đang legal hold |
| Exception handling accuracy | 0.0000 (0/56) | 1.0000 (56/56) | higher is better |
| **Hard-slice:** `retain_legal_hold` (N=40) | 0.000 | 1.000 | ablation bỏ hold thừa kế: 0.100 |
| **Hard-slice:** `training_export` (N=12) | 0.000 | 1.000 | ablation: 0.000 (export là hậu duệ crop bị hold) |
| Review@B | n/a | 56/56 ngoại lệ vào hàng chờ, miss = 0, B = 100 | B ≥ 56 nên miss = 0 theo cấu trúc, không dùng làm bằng chứng chất lượng |
| Runtime (PoC) | 0.0307 s / 10 dòng | 0.1874 s / 158 dòng (≈ 1.19 ms/dòng) | baseline chỉ xử lý 10 dòng nên không so sánh trực tiếp theo "100 items" |

Ablation (bỏ hold thừa kế) sinh 24 xoá nhầm: thừa kế hold là điều kiện cần để False-delete = 0.

## 05 · Evaluation protocol

Xem `reports/metric_contract.md` và `sections/05_eval_protocol.md`. Lệnh: `python -m src.evaluate --track t08 --gt reports/selfcheck/t08_expected.csv --pred out/poc/actions.csv --out reports/selfcheck/metrics_poc_selfcheck.json`. File metric đặt đúng đường dẫn nộp bài: `reports/metrics_baseline.json`, `reports/metrics_poc.json` (bản sao của hai file `*_selfcheck.json`).

## 06 · Result slices

Xem `sections/06_result_slices.md` (slice theo action và theo loại artefact, 2 failure case, latency): failure case 1 là baseline xoá nhầm raw đang legal hold (`DR-002:a0043`, `DR-005:a0099`); failure case 2 là baseline chỉ xoá raw nên còn sót 13 artefact phải xoá ở DR-001.

## 07 · Human & decision

Xem `sections/07_human_decision.md` và `sections/07_generated_tables.md`. Bằng chứng: `reports/review_queue.csv` (56 ngoại lệ), `reports/review_queue_reviewed.csv` (2 dòng đã ký), `reports/decision_log.csv`, `out/poc/audit_log.jsonl`.

- Kết quả: **DR-006 GO**, 9 request HOLD, `data-catalog` REWORK.
- Người duyệt (vai DPO): `Le Duy Bao`. Đây là thành viên nhóm đóng vai, không phải chữ ký pháp lý thật.
- DR-002 và DR-005 không có dòng `delete` nào vì toàn bộ phạm vi nằm dưới legal hold.
- DR-006 GO chỉ đúng theo catalog hiện tại, vì `a0123` (đã ký) nằm trong 4 cảnh báo lineage.

## 08 · Reproduce & tests

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m tools.preflight
.\.venv\Scripts\python.exe -m src.main --offline --seed 42
mkdir out\poc
copy reports\review_queue_reviewed.csv out\poc\review_queue_reviewed.csv
.\.venv\Scripts\python.exe -m src.main --config configs/lab.yaml --track t08 --output out/poc --run-name poc --offline --seed 42
.\.venv\Scripts\python.exe -m src.main --config configs/lab.yaml --track t08 --pipeline src.t08.baseline --output out/baseline --run-name baseline --offline --seed 42
.\.venv\Scripts\python.exe -m pytest -q
```

Demo idempotent (chế độ thực thi mock, `dry_run: false`) — chạy hai lần, lần 2 phải có `deleted_new: 0, skipped_already_deleted: 102` trong `out/exec/run_info.json`:

```powershell
.\.venv\Scripts\python.exe -m src.main --config configs/lab_execute.yaml --track t08 --output out/exec --run-name exec --offline --seed 42
```

- Mặc định `configs/lab.yaml` dùng `dry_run: true` (chỉ lập kế hoạch, không gọi kho mock); `configs/lab_execute.yaml` dùng `dry_run: false`.
- `pytest -q`: **70 passed, 39 skipped** (39 test bị skip vì repo học viên không có file `gt/` của giảng viên).
- Máy: Windows 11, Intel64, Python 3.13.17; git sha khi kiểm: `__________` (lấy bằng `git rev-parse --short HEAD`). Chạy lại 2 lần cho `actions.csv` giống hệt.
- Không cần mạng; `--offline` fail rõ nếu thiếu dữ liệu, không tải gì.

## 09 · Limitations & ethics

Xem `sections/09_limitations_ethics.md`. Tóm tắt: dữ liệu synthetic và chỉ 10 request; chấm bằng self-check của nhóm; chính sách R1–R8 là ví dụ giảng dạy cần pháp chế xác nhận; người duyệt là thành viên đóng vai; kho xoá là mock; redact và rebuild `training_export` mới dừng ở `escalate`. Không tuyên bố đạt GDPR hay luật Việt Nam.

## 10 · Team contribution

Chi tiết: `reports/team_contributions.csv`. Nhóm 4 người; commit của `loversky02`, `Tin Duong` thuộc repo starter, không tính.

| Học viên | Git author / email | Module / vai trò | Commit SHA | Trình bày |
|---|---|---|---|---|
| Nguyễn Văn Đại | Danaai / 115464649+Danaai@users.noreply.github.com | Integration, `src/pipeline.py`, `src/t08/store.py`, `src/t08/review.py`, `tools/t08_review_report.py`, báo cáo mục 07 và 09 | 216f04c, 51ee0d9, 3489952, cdbde7d, de8e31d, 11db8a8, 343c368, 02e62ad, 584b484 | __________ |
| Nguyễn Quốc Vương | vuomg / vug10032004@gmail.com | Core algorithm: `graph.py`, `policy.py`, `baseline.py`, `t08_policy.yaml` | 9ac6fb4, b334a4e, 3810fdc, 8d83d7b, 9767932, 57e85f7 | __________ |
| Phan Đình Giáp | giappd-ai / giappdhe140952@gmail.com | Data + self-check GT + tests + metric + slices | 6ac9c66, 6cc97c3, dde1a51, 223f261, 2dcdc00, f72c08c | __________ |
| Lê Duy Bảo | baodu1204 / duybaole2004@gmail.com | `Human review + report` | d06157a, ce04980 | __________ |

Commit `8bf4a6b` ("nothing") không có nội dung nên không được tính cho ai.

## 11 · References

| URL | Ngày xem | Ý nghĩa |
|---|---|---|
| https://gdpr-info.eu/art-17-gdpr/ | 14/11/2026 | Quyền xoá và các ngoại lệ (Art.17(3)(e)) → cơ sở luật R2/R3 trong ví dụ giảng dạy |
| https://openlineage.io/docs/spec/examples | 15/11/2026 | Chuẩn mô tả lineage tương ứng trường `parent_ids` trong `data_graph.json` |
| Luật 91/2025; Nghị định 356/2025 — `[URL văn bản chính thức bạn đã mở]` | `[ngày xem]` | Quyền xoá theo pháp luật Việt Nam; cần pháp chế xác nhận hiệu lực và phạm vi |

---

**Bảng 3 · Checklist chốt khi nộp**

- [ ] Link repo và tag cuối (`final-24h`) trong report; input không chứa PII thật.
- [ ] Đúng 1 lệnh run, 1 lệnh evaluate, 1 lệnh tests; không cần download khi chạy.
- [ ] Có baseline / PoC metrics (`reports/metrics_baseline.json`, `reports/metrics_poc.json`), ≥ 1 failure case, reviewer evidence, decision log.
- [ ] Có license / source provenance, seed, offline environment, N.
- [ ] Mỗi thành viên có ≥ 1 commit thực chất và được nêu ở mục 10.