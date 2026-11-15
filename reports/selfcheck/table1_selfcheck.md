Baseline: `baseline` (git None, seed 42) · PoC: `poc` (git None, seed 42)

| Metric (unit) | Slice | Baseline | PoC | Δ abs | Δ rel | Better | N |
|---|---|---|---|---|---|---|---|
| **Deletion Completeness** (must-delete artefacts deleted / must-delete artefacts) | all | 0.0784 | 1.0000 | 0.9216 | +1175.0% | higher | 158 |
| False-delete count (count (target 0): exceptions deleted + deletes outside request scope) | all | 2.0000 | 0.0000 | -2.0000 | -100.0% | lower | None |
| Exception handling accuracy (legal-hold/escalate rows handled as expected / such rows) | all | 0.0000 | 1.0000 | 1.0000 | baseline=0 | higher | None |
| Audit trace completeness (actions with an audit entry / actions) | all | 1.0000 | 1.0000 | 0.0000 | +0.0% | higher | None |
| Runtime / 100 items (s) | all | 0.3070 | 0.1186 | | | lower | |

### Nhận xét phản biện

- Bảng này rất hiệu quả vì nó nén được hiệu suất chủ chốt của PoC thành một bộ số dễ đọc: completeness tăng mạnh, false-delete giảm về 0, và exception handling đạt 1.0. Điều này phù hợp để làm điểm khởi đầu cho phần tổng kết vì người đọc nắm ngay được "sự cải thiện chính" mà không cần đọc toàn bộ pipeline.
- Tuy nhiên, điểm yếu là các số liệu đang được tính trên toàn bộ tập synthetic và không tách train/dev/eval. Điều này làm cho các con số rất mạnh về mặt hướng dẫn, nhưng cũng có thể tạo ấn tượng rằng PoC đã đánh giá tốt trên dữ liệu đời thực. Cần nhấn mạnh rõ hơn ở đây rằng mục tiêu hiện tại là kiểm chứng logic, không phải khẳng định hiệu suất sản phẩm trên dữ liệu ngoài lab.
- Một cải tiến đáng làm là thêm một cột "confidence / uncertainty" hoặc ghi chú ngắn cho mỗi metric, ví dụ loại bỏ hoặc làm rõ khoảng tin cậy, để tránh người đọc suy diễn quá mức từ một bảng 10 dòng.
