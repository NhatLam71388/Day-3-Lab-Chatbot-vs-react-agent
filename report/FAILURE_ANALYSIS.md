# Phân tích Lỗi: Giai đoạn 4

## Ngữ cảnh
Trong Giai đoạn 3, chúng ta đã xây dựng Agent v1 sử dụng một system prompt (câu lệnh hệ thống) đơn giản. Prompt này cung cấp mô tả của các công cụ (tools) và các hướng dẫn cơ bản về vòng lặp suy luận Thought-Action-Observation.

## Dấu vết Lỗi (Agent v1)
Khi thử nghiệm với câu hỏi: 
**"Tôi muốn mua 2 iPhone dùng mã 'WINNER' và ship về Hà Nội. Tổng tiền là bao nhiêu?"**

Agent v1 thường xuyên gặp thất bại theo một trong những cách sau:
1. **Ảo giác đối số (Hallucination of Arguments)**: Agent có thể tự đoán số lượng tồn kho hoặc định dạng tham số của tool không đúng chuẩn (ví dụ: viết `Action: check_stock("iPhone", 2)` thay vì phải viết chuẩn `Action: check_stock(iphone)`).
2. **Vòng lặp vô tận (Infinite Loops)**: Agent liên tục xuất ra `Thought: I need to check the stock` nhưng không xuất ra định dạng `Action` hợp lệ, hoặc không chịu chờ nhận `Observation` (kết quả trả về của tool) mà tự giả lập luôn kết quả đó.
3. **Lỗi toán học (Math Errors)**: Agent lấy được toàn bộ dữ liệu đầu vào thành công nhưng lại tính toán sai công thức `(giá * 2) * (1 - phần trăm giảm giá) + phí ship`.

### Log Lỗi Mẫu (từ thư mục `logs/`):
```json
{
  "event": "AGENT_ERROR",
  "data": {
    "message": "No action found."
  }
}
```
*Nguyên nhân lỗi:* LLM sinh ra `Thought: I will call check_stock` nhưng lại viết action thành một câu tự do như `Call check_stock for iphone` thay vì tuân thủ định dạng nghiêm ngặt là `Action: check_stock(iphone)`.

## Giải pháp Khắc phục: Agent v2
Để giải quyết triệt để vấn đề này, chúng tôi đã cập nhật system prompt ở phiên bản `Agent v2`. Bằng cách áp dụng kỹ thuật **Few-Shot Prompting**, chúng tôi cung cấp cho LLM các ví dụ mẫu chính xác về cách một chuỗi suy luận (trace) chuẩn diễn ra.

### Những thay đổi đã thực hiện (v1 -> v2):
1. **Bổ sung Few-Shot Examples (Ví dụ mẫu)**: Thêm các ví dụ minh họa chính xác định dạng `Action: tool_name(args)` và cách thức Agent phải chờ đợi để nhận kết quả (Observation) thay vì tự sinh ra kết quả ảo.
2. **Các nhắc nhở nghiêm ngặt**: Thêm quy tắc cứng như `DỪNG LẠI sau khi viết "Action: tool_name(args)". KHÔNG ĐƯỢC tự viết "Observation:"`.

Nhờ những thay đổi này, `Agent v2` đã truy vấn chính xác các hàm `check_stock`, `get_item_price`, `get_discount_code`, và `calculate_shipping` theo đúng trình tự Logic và đưa ra `Final Answer` (Câu trả lời cuối cùng) hoàn hảo.
