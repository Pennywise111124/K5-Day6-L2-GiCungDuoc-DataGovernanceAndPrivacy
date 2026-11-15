# 06 · Result slices (phần C — QA / metric)

> Nguồn: `reports/selfcheck/t08_slices.md` (sinh bằng `python -m tools.t08_slices`), chấm trên self-check, seed 42.

**Slice theo `expected_action`** (accuracy = đúng action / N)

| Slice | N | Baseline | PoC | Ablation | Ghi chú |
|---|---|---|---|---|---|
| delete | 102 | 0.078 | 1.000 | 1.000 | baseline chỉ xoá raw |
| retain_legal_hold | 40 | 0.000 | 1.000 | 0.100 | ablation mất thừa kế hold |
| escalate | 16 | 0.000 | 1.000 | 1.000 | |

**Slice theo `artefact_type`**

| Slice | N | Baseline | PoC | Ablation | Ghi chú |
|---|---|---|---|---|---|
| raw_video | 10 | 0.800 | 1.000 | 1.000 | baseline sai 2 raw bị hold |
| backup | 10 | 0.000 | 1.000 | 1.000 | |
| frame | 33 | 0.000 | 1.000 | 0.818 | |
| face_crop | 30 | 0.000 | 1.000 | 0.800 | |
| embedding | 30 | 0.000 | 1.000 | 0.800 | |
| annotation | 33 | 0.000 | 1.000 | 0.818 | |
| training_export | 12 | 0.000 | 1.000 | 0.000 | export là hậu duệ crop bị hold |

- **Failure case 1 — xoá nhầm ngoại lệ (baseline).** `out/baseline/actions.csv` có `DR-002,a0043,delete`; trong `data_graph.json` `a0043` là raw_video của subj_03 với `legal_hold = LH-2026-03` (tương tự `DR-005,a0099,delete`, `LH-2026-07`). **Root cause:** baseline chỉ khớp tên file, không đọc `legal_hold` → xoá dữ liệu đang bị giữ pháp lý, không hoàn tác được. PoC: R2 → `retain_legal_hold`, có test `test_legal_hold_never_deleted`.
- **Failure case 2 — chỉ xoá raw, bỏ sót lineage (baseline, DR-001).** Baseline xoá 1/17 artefact trong phạm vi; còn sót 13 artefact phải xoá (3 frame · 3 face_crop · 3 embedding · 3 annotation · 1 backup), ví dụ backup `a0016` ở `mock://glacier/backup/a0016`, embedding `a0019/a0023/a0027` trong vector-db. **Root cause:** không duyệt `parent_ids` → Completeness 8/102. PoC: `graph.scope` duyệt cây.
- **Latency / compute** (Windows 11, Python 3.12.0, AMD64): PoC 0.1874 s / 158 dòng = **1.19 ms/dòng**; baseline 0.0307 s / 10 dòng; ablation 0.2347 s / 158 dòng.

### Nhận xét phản biện

- Phần slice này rất mạnh ở chỗ nó không chỉ báo "PoC tốt" theo tổng số, mà còn cho thấy từng nhóm lỗi và từng kiểu artefact có thể sai ở đâu. Cách tổ chức theo `expected_action` và `artefact_type` khiến người đọc dễ nhận ra nguyên nhân sâu hơn: không phải do lỗi randomness, mà là do thiếu lineage và thiếu kiểm tra hold.
- Tuy nhiên, để tăng độ tin cậy hơn nữa, nên bổ sung thêm một slice theo "trạng thái dữ liệu thật" như `legal_hold`, `shared_subject`, `origin_unknown`, hoặc `missing_catalog` để thấy mô hình có thể xử lý các trường hợp rủi ro thực tế tốt đến đâu. Hiện tại, các trường hợp thất bại được mô tả khá rõ nhưng chưa được trình bày như một ma trận kiểm thử đầy đủ.
- Một điểm đáng lưu ý là latency được báo rất tốt, nhưng cần đi kèm với bối cảnh thí nghiệm: file size, số lượng đồ thị vật lý, và mức độ phong phú của lineage. Nếu không thêm yếu tố đó, con số 1.19 ms/dòng có thể dễ bị hiểu nhầm là hiệu suất thực tế của hệ thống trong sản phẩm.
