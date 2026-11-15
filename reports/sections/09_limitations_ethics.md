# 09 · Limitations & ethics

## Giới hạn của bằng chứng

1. **Dữ liệu synthetic, chỉ 1 đồ thị / 10 request / 158 cặp.** Không chia dev/eval; mọi số liệu là trên toàn bộ tập. Khoảng tin cậy Wilson rộng (ví dụ PoC Completeness 102/102 → [0.964, 1.000]) và không suy ra được hiệu năng trên dữ liệu thật.
2. **Bộ chấm là self-check do nhóm tự gán** (`reports/selfcheck/t08_expected.csv`), không phải GT của giảng viên. PoC đạt 1.0 / 0 vì self-check gán theo chính sách đã chốt: điều này chứng minh *code làm đúng chính sách*, **không** chứng minh *chính sách đúng luật*.
3. **Chính sách R1–R8 là ví dụ giảng dạy.** Số điều khoản (GDPR Art.5(2), 12(6), 15(4), 17, 28; Luật 91/2025; NĐ 356/2025; California DROP) lấy từ tài liệu lớp và cần DPO/pháp chế xác minh hiệu lực, phạm vi, cách áp dụng trước khi dùng thật. 14/11/2026
4. **Người duyệt là thành viên nhóm đóng vai DPO**, không có thẩm quyền pháp lý. Mọi mục "đã ký" chỉ có nghĩa trong mô phỏng.
5. **Mọi `identity_verified = true`** trong fixture nên R1 chỉ được kiểm bằng test mini fixture, chưa có yêu cầu thật bị từ chối vì danh tính.

## Giới hạn của thuật toán

- **Hold thừa kế làm Completeness lý thuyết thấp hơn**: 102 delete / 40 retain / 16 escalate, so với 126 / 4 / 28 khi chỉ hold backup; đổi lại không có xoá nhầm (ablation sinh 24 false-delete).
- **Phụ thuộc catalog đúng.** 4 cảnh báo lineage (`a0011, a0067, a0123, a0179`) cho thấy catalog có thể thiếu subject ở cha; hệ thống báo REWORK nhưng không tự sửa.
- **Redact, rebuild `training_export`, yêu cầu vendor-x xoá backup chỉ dừng ở trạng thái `escalate`/ghi chú**, chưa có thao tác thật. Xoá export không xoá được ảnh hưởng của dữ liệu đó lên model đã huấn luyện; backup/vendor có chu kỳ lưu riêng.
- **Kho xoá là mock** (`mock_store_state.json`); không có xoá vật lý, không kiểm tra xoá thật trong vector-db hay cloud.
- **Hạn 30 ngày chưa được cưỡng chế**: `deadline` có trong dữ liệu nhưng SLA/cảnh báo là việc bổ sung (D8).

## Rủi ro ngược chiều và nguyên tắc an toàn

| Rủi ro | Hậu quả | Biện pháp trong PoC |
|---|---|---|
| Xoá thiếu | Vi phạm quyền xoá của người yêu cầu | Duyệt lineage; metric Completeness; baseline chỉ xoá raw bị lộ ở Failure case 2 |
| Xoá nhầm (legal hold / dữ liệu người khác) | Huỷ bằng chứng, mất dữ liệu người khác, **không hoàn tác** | False-delete = 0; khi phân vân → không xoá; người duyệt ký ngoại lệ; audit đầy đủ |

## Quyền riêng tư, giấy phép, dữ liệu

- Không dùng dữ liệu cá nhân thật; fixture sinh bằng `tools/make_fixtures.py` (seed 42), giấy phép CC0-1.0, có `manifest.csv` + sha256 (sai hash → exit 2).
- Không gọi mạng khi chạy (`--offline`); không có model hay weights.
- Báo cáo **không tuyên bố tuân thủ** GDPR hay luật Việt Nam.

## Khi mở rộng 10×

- BFS trên đồ thị lớn hơn vẫn nhanh (≈1,2 ms/dòng trong lab); nút thắt là **hàng chờ duyệt** (56 → ~560 dòng): cần gom theo `reason_code`, duyệt theo lô và đặt budget có ưu tiên.
- Cần hàng đợi bất đồng bộ, resume theo từng artefact (đã có ở `MockStore`), xác minh xoá thật ở từng hệ thống, và quản lý vòng đời legal hold (hẹn gỡ, nhắc hạn).

## Kế hoạch cải tiến

1. Đối chiếu chính sách với DPO/pháp chế thật và cập nhật `version` / `effective_date`.
2. Cài thao tác redact cho artefact dùng chung và rebuild `training_export`.
3. SLA dashboard + thông báo cho request HOLD gần hạn.
4. Sửa catalog (4 cảnh báo) rồi chạy lại toàn bộ và duyệt lại.
5. Thử trên GT của giảng viên khi có `gt/`.
