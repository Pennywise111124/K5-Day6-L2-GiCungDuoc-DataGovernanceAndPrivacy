# 07 · Human & decision

> Tài liệu học tập trên dữ liệu synthetic; không phải tư vấn pháp lý. "DPO" trong báo cáo là **thành viên nhóm đóng vai**, không phải chữ ký pháp lý thật.

## 7.1 Hàng chờ duyệt (review queue)

- Mọi dòng có action khác `delete` (56 dòng = 40 `retain_legal_hold` + 16 `escalate`) vào `out/poc/review_queue.csv` / `review_queue.html`. Review budget B = 100 ≥ 56 nên **không bỏ sót dòng nào do ngân sách**; vì vậy Recall@B của hàng chờ bằng 1 theo cấu trúc và không dùng làm bằng chứng chất lượng.
- Thứ tự ưu tiên (`src/t08/review.py`, `PRIORITY`): identity / legal hold trực tiếp (5) > hold thừa kế, thiếu quyền ACL (4) > nguồn gốc không rõ (3) > export, dữ liệu dùng chung nhiều người (2).
- Thành phần hàng chờ (Bảng 7.3 bên dưới): LEGAL_HOLD_INHERITED 38 · MULTI_SUBJECT_SHARED 12 · ORIGIN_UNKNOWN 3 · LEGAL_HOLD_ACTIVE 2 · NO_PERMISSION_ACL 1.

## 7.2 Cách người duyệt tác động (override) và log

| `reviewer_decision` | Tác dụng | Ghi log |
|---|---|---|
| `approve` | Người duyệt **ký** action máy đề xuất; điền `reviewed_by` | `review:approve` (before = after) |
| `edit` + `override_value` | Đổi action (chỉ nhận `delete` / `retain_legal_hold` / `escalate`); `rule_id = HUMAN_OVERRIDE` | `review:edit` (before ≠ after) |
| `reject` / `escalate` / `skip` | Chưa ký → request vẫn HOLD | `review:<quyết định>` |

Mỗi thao tác ghi 1 dòng `audit_log.jsonl`: `actor`, `action`, `item_id`, `before`, `after`, `reason` (= `review_note`), `request_id`, `ts`. Thiếu `reviewer` → pipeline báo lỗi. File gốc `review_queue.csv` không bị sửa; quyết định nằm ở `review_queue_reviewed.csv` (bản lưu: `reports/review_queue_reviewed.csv`).

## 7.3 Chính sách quyết định theo request

| Điều kiện (theo thứ tự kiểm) | Quyết định | reason_code | Owner |
|---|---|---|---|
| Còn ngoại lệ chưa có `reviewed_by` | **HOLD** | PENDING_DPO_REVIEW | DPO (`owner` trong `configs/lab.yaml`) |
| Đã ký hết nhưng còn `retain_legal_hold` | **HOLD** | LEGAL_HOLD_ACTIVE | DPO / pháp chế |
| Đã ký hết, không còn hold | **GO** | ERASURE_COMPLETE / ERASURE_DONE_EXCEPTIONS_SIGNED | DPO |
| Catalog có cảnh báo lineage (4: `a0011, a0067, a0123, a0179`) | **REWORK** (scope `data-catalog`) | LINEAGE_INCONSISTENT | Chủ catalog |
| Tổng thể | GO chỉ khi mọi request GO | ALL_CLOSED / OPEN_REQUESTS | DPO |

Khi chưa chắc, hệ thống chọn **không xoá** (xoá không hoàn tác, giữ/escalate thì sửa được sau).

## 7.4 Vòng duyệt 1 (do Lê Duy Bảo, vai DPO, ngày 14/11/2026)

Đã duyệt **2 dòng** (Bảng 7.2): `DR-006:a0123`, `DR-006:a0126` (frame/annotation dùng chung 2 người: giữ `escalate`, chuyển sang redact thay vì xoá) [+ các dòng khác nếu có]. Không dùng `edit` trong lần chạy được chấm, để tránh biến ngoại lệ thành `delete`; minh hoạ override (nếu làm) chạy riêng ở `out/override_demo/`.

## 7.5 Kết quả và điều đáng chú ý

**Quyết định theo request**

| request | artefact trong phạm vi | delete | retain_legal_hold | escalate | ngoại lệ đã ký | ngoại lệ chưa ký | quyết định | reason_code |
|---|---|---|---|---|---|---|---|---|
| DR-001 | 17 | 14 | 1 | 2 | 0 | 3 | HOLD | PENDING_DPO_REVIEW |
| DR-002 | 15 | 0 | 15 | 0 | 0 | 15 | HOLD | PENDING_DPO_REVIEW |
| DR-003 | 16 | 12 | 2 | 2 | 0 | 4 | HOLD | PENDING_DPO_REVIEW |
| DR-004 | 18 | 11 | 2 | 5 | 0 | 7 | HOLD | PENDING_DPO_REVIEW |
| DR-005 | 16 | 0 | 16 | 0 | 0 | 16 | HOLD | PENDING_DPO_REVIEW |
| DR-006 | 14 | 12 | 0 | 2 | 2 | 0 | GO | ERASURE_DONE_EXCEPTIONS_SIGNED |
| DR-007 | 17 | 14 | 1 | 2 | 0 | 3 | HOLD | PENDING_DPO_REVIEW |
| DR-008 | 15 | 13 | 1 | 1 | 0 | 2 | HOLD | PENDING_DPO_REVIEW |
| DR-009 | 15 | 12 | 1 | 2 | 0 | 3 | HOLD | PENDING_DPO_REVIEW |
| DR-010 | 15 | 14 | 1 | 0 | 0 | 1 | HOLD | PENDING_DPO_REVIEW |

**Dòng đã được người duyệt xử lý** — 2 dòng

| item_id | reason | suggested_action | reviewer | reviewer_decision | review_note | reviewed_at |
|---|---|---|---|---|---|---|
| DR-006:a0123 | MULTI_SUBJECT_SHARED | escalate | Le Duy Bao | approve | frame chung subj_08+09: giu escalate, chuyen redact | 2026-11-15T17:00:00 |
| DR-006:a0126 | MULTI_SUBJECT_SHARED | escalate | Le Duy Bao | approve | annotation chung subj_08+09: giu escalate, chuyen redact | 2026-11-15T17:00:00 |

**Hàng chờ theo lý do** (tổng 56 dòng)

| reason | số dòng |
|---|---|
| LEGAL_HOLD_INHERITED | 38 |
| MULTI_SUBJECT_SHARED | 12 |
| ORIGIN_UNKNOWN | 3 |
| LEGAL_HOLD_ACTIVE | 2 |
| NO_PERMISSION_ACL | 1 |

**Quyết định cấp hệ thống / catalog:**

| scope | status | reason_code | reason |
|---|---|---|---|
| data-catalog | REWORK | LINEAGE_INCONSISTENT | 4 lineage warnings |
| t08-all | HOLD | OPEN_REQUESTS | 1/10 requests GO |

- **DR-006 = GO** vì cả 2 ngoại lệ đã ký; **9 request còn lại HOLD** do còn ngoại lệ chưa ký.
- **DR-002 và DR-005: 0 dòng `delete`** (15/15 và 16/16 artefact trong phạm vi bị hold, vì raw `a0043` / `a0099` có legal hold và hold thừa kế xuống cả cây con). Nghĩa là yêu cầu xoá của hai người này không thực hiện được cho tới khi hold được gỡ; cần ghi hạn gỡ hold và người sở hữu.
- **DR-006 GO nhưng `data-catalog` vẫn REWORK**, và `a0123` (đã ký) nằm trong 4 cảnh báo lineage. Vì thế GO của DR-006 chỉ có nghĩa "workflow xoá hoàn tất theo catalog hiện tại"; nếu catalog sửa lại, cần chạy lại và duyệt lại.
- `decision_log.csv` và `audit_log.jsonl` nối thêm dòng sau mỗi lần chạy; số liệu ở trên lấy bản ghi cuối của mỗi `scope`.

## 7.6 Câu hỏi debate đã chuẩn bị

- *Khi nào được từ chối xoá?* Khi có legal hold (R2/R3): ghi `reason_code` + nguồn luật + ngày gỡ hold dự kiến.
- *DPO duyệt sai thì sao?* Audit ghi ai / khi nào / trước–sau; sửa bằng lần duyệt mới (không sửa log cũ).
- *Vì sao không tuyên bố "đạt GDPR / luật Việt Nam"?* Chính sách là ví dụ giảng dạy, nguồn luật cần DPO/pháp chế xác nhận, dữ liệu là mock.
