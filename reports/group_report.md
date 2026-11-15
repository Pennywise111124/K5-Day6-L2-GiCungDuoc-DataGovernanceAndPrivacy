# Group Report — Day 06 Data Lab (Field-to-Release PoC)

> Chi tiết từng mục nằm trong `reports/sections/`. Số liệu lấy từ file do script sinh (`reports/selfcheck/*.json`, `reports/selfcheck/table1_selfcheck.md`, `out/poc/*`).

## 00 · Header

| Mục | Giá trị |
|---|---|
| Group ID | GiCungDuoc |
| Challenge | T08 · Retention & Delete Request Simulator |
| Thành viên (4) + vai trò | 1. Nguyễn Văn Đại (Lead/Integrator) · 2. Nguyễn Quốc Vương (Core algorithm) · 3. Phan Đình Giáp (Data & fixtures + QA/metric) · 4. Lê Duy Bảo (Human review + report) |
| Git URL | https://github.com/Pennywise111124/K5-Day6-L2-GiCungDuoc-DataGovernanceAndPrivacy |
| Tag `demo-180m` (commit) | chưa gắn tại thời điểm viết report |
| Tag `final-24h` (commit) | chưa gắn tại thời điểm viết report |
| Deadline (giờ VN) | +24h sau buổi lab 14/11/2026 |

## 01 · Problem statement

- Ai bị ảnh hưởng: người gửi yêu cầu xoá (xoá thiếu → vi phạm quyền xoá) và bên giữ dữ liệu / người khác (xoá nhầm → huỷ bằng chứng đang legal hold, mất dữ liệu người khác, không hoàn tác).
- Điểm nghẽn: dữ liệu một người nằm rải trong raw → backup → frame → crop/embedding/annotation → training export; xoá theo tên file bỏ sót phần dẫn xuất.
- Đầu vào → đầu ra: `requests.json` (10 yêu cầu) + `data_graph.json` (212 artefact) → `actions.csv` (158 dòng: delete / retain_legal_hold / escalate) + `audit_log.jsonl` + quyết định từng request.
- Tiêu chí GO / HOLD / REWORK: GO khi mọi ngoại lệ đã được ký và không còn legal hold; HOLD khi còn ngoại lệ chưa ký hoặc còn hold; REWORK khi catalog lineage mâu thuẫn (xem `sections/07_human_decision.md` §7.3).
- Giả định cần DPO/legal xác nhận: chính sách R1–R8 và hold thừa kế xuống cả cây con.

## 02 · Data & provenance

Xem `sections/02_data_provenance_C.md` và `sections/02_algorithm_part_B.md`.

| Split | N | Nguồn / link | License | Synthetic? |
|---|---|---|---|---|
| eval (không chia) | 10 request · 212 artefact · 158 cặp | `fixtures/t08_deletion/` | CC0-1.0 | Có |

- Seed 42; không chia split vì không có tham số để tune. `manifest.csv` verified: có (`python -m tools.verify_manifests`).
- Không dùng dữ liệu thật; GT tự kiểm `reports/selfcheck/t08_expected.csv` do C gán tay.

## 03 · Research & design

Xem `sections/03_research_design.md` (references, data flow, trade-off). Không dùng model/weights; chạy offline.

## 04 · Baseline vs PoC

Xem `sections/04_baseline_vs_poc.md`. Baseline = xoá raw theo filename (`src.t08.baseline`); PoC = lineage + R1–R8 + hàng chờ DPO (`src.pipeline`). Cùng data, seed 42, 158 cặp.

| Metric (unit) | Baseline | PoC | Ghi chú |
|---|---|---|---|
| Primary: Deletion Completeness | 0.0784 (8/102) | 1.0000 (102/102) | higher; chấm trên self-check, không phải GT giảng viên |
| False-delete count | 2 | 0 | lower; baseline xoá `a0043`, `a0099` đang legal hold |
| Exception handling accuracy | 0.0000 (0/56) | 1.0000 (56/56) | |
| Runtime / 100 items | 0.3070 s | 0.1186 s | `table1_selfcheck.md` |

## 05 · Evaluation protocol

Xem `reports/metric_contract.md` và `sections/05_eval_protocol.md`. Lệnh: `python -m src.evaluate --track t08 --gt reports/selfcheck/t08_expected.csv --pred out/poc/actions.csv --out reports/selfcheck/metrics_poc_selfcheck.json`.

## 06 · Result slices

Xem `sections/06_result_slices.md` (slice theo action và theo loại artefact, 2 failure case, latency).

## 07 · Human & decision

Xem `sections/07_human_decision.md` và `sections/07_generated_tables.md`. Bằng chứng: `reports/review_queue.csv` (56 ngoại lệ), `reports/review_queue_reviewed.csv` (2 dòng đã ký), `reports/decision_log.csv`. Kết quả: DR-006 GO, 9 request HOLD, `data-catalog` REWORK.

## 08 · Reproduce & tests

```powershell
python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.main --offline --seed 42 --output out/poc --run-name poc
.\.venv\Scripts\python.exe -m src.main --config configs/lab.yaml --track t08 --pipeline src.t08.baseline --output out/baseline --run-name baseline --offline --seed 42
.\.venv\Scripts\python.exe -m pytest -q
```

- Output `pytest -q`: 70 passed, 39 skipped (skip do repo học viên không có `gt/`).
- Máy: Windows 11, Intel64, Python 3.11.9 · git sha khi kiểm: 02e62ad. Chạy lại 2 lần cho `actions.csv` giống hệt.

## 09 · Limitations & ethics

Xem `sections/09_limitations_ethics.md`. Không tuyên bố đạt GDPR / luật Việt Nam; cần DPO/pháp chế xác nhận.

## 10 · Team contribution

Chi tiết: `reports/team_contributions.csv`. Nhóm 4 người; commit `loversky02`, `Tin Duong` là của repo starter.

| Học viên | Git author/email | Module / vai trò | Commit SHA | Trình bày? |
|---|---|---|---|---|
| Nguyễn Văn Đại | Danaai | Integration / pipeline / store | 216f04c, 3489952, cdbde7d, de8e31d, 11db8a8, 343c368, 02e62ad | |
| Nguyễn Quốc Vương | vuomg / vug10032004@gmail.com | Core algorithm + baseline | 9ac6fb4, b334a4e, 3810fdc, 8d83d7b, 9767932, 57e85f7 | |
| Phan Đình Giáp | giappd-ai / giappdhe140952@gmail.com | Data + self-check GT + tests + metric | 6ac9c66, 6cc97c3, dde1a51, 223f261, 2dcdc00, f72c08c | |
| Lê Duy Bảo | baodu1204 / duybaole2004@gmail.com | Review (DPO) + report | chưa có commit | |

## 11 · References

| URL | Ngày xem | Ý nghĩa |
|---|---|---|
| https://gdpr-info.eu/art-17-gdpr/ | 14/11/2026 | Quyền xoá và ngoại lệ (Art.17(3)(e)) → luật R2/R3 |
| Luật 91/2025, Nghị định 356/2025 (tài liệu lớp) | 14/11/2026 | Quyền xoá theo pháp luật VN; cần pháp chế xác nhận |
| https://openlineage.io/docs/spec/examples | 15/11/2026 | Chuẩn mô tả lineage tương ứng `parent_ids` |

---

**Bảng 3 · Checklist chốt khi nộp**

- [x] Link repo trong report; input không chứa PII thật. Tag cuối: chưa gắn.
- [x] Đúng 1 lệnh run, 1 lệnh evaluate, 1 lệnh tests; không cần download khi chạy.
- [x] Có baseline/PoC metrics, ≥1 failure case, reviewer evidence, decision log.
- [x] Có license/source provenance, seed, offline environment, N.
- [ ] Mỗi thành viên có ≥1 commit thực chất (Lê Duy Bảo chưa có).
