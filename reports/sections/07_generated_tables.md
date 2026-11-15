<!-- Sinh tự động bởi tools/t08_review_report.py; không sửa tay -->

**Bảng 7.1 · Quyết định theo request** (nguồn: `out\poc/actions.csv`, `decision_log.csv`)

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

**Bảng 7.2 · Dòng đã được người duyệt xử lý** (nguồn: `out\poc\review_queue_reviewed.csv`) — 2 dòng

| item_id | reason | suggested_action | reviewer | reviewer_decision | review_note | reviewed_at |
|---|---|---|---|---|---|---|
| DR-006:a0123 | MULTI_SUBJECT_SHARED | escalate | Le Duy Bao | approve | frame chung subj_08+09: giu escalate, chuyen redact | 2026-11-15T17:00:00 |
| DR-006:a0126 | MULTI_SUBJECT_SHARED | escalate | Le Duy Bao | approve | annotation chung subj_08+09: giu escalate, chuyen redact | 2026-11-15T17:00:00 |

**Bảng 7.3 · Hàng chờ theo lý do** (nguồn: `out\poc/review_queue.csv`, tổng 56 dòng)

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

**Audit:** `audit_log.jsonl` có 262 dòng, trong đó 2 dòng `review:*`.
