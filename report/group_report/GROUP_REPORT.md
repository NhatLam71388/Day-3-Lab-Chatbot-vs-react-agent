# Báo cáo Nhóm: Lab 3 - Hệ thống Chatbot và ReAct Agent

- **Tên nhóm**: Nhóm A8
- **Thành viên**: 
  - Tạ Văn Huấn - 2A202600984
  - Nguyễn Nhật Lâm - 2A202600851
  - Hoàng Trung Quân - 2A202600720
- **Ngày triển khai**: 01/06/2026

---

## 1. Tóm tắt Thực thi (Executive Summary)

*Tổng quan về mục tiêu của Agent và tỷ lệ thành công so với Chatbot cơ bản.*

- **Tỷ lệ thành công**: Đạt 90% trên các kịch bản kiểm thử đa bước phức tạp.
- **Kết quả chính**: Hệ thống ReAct Agent của nhóm có khả năng tự động tra cứu tồn kho, tính giá, áp dụng mã giảm giá và tính phí vận chuyển thành công. Agent giải quyết được 100% các câu hỏi đa bước (multi-step queries) mà Chatbot cơ bản (Baseline) luôn thất bại do thiếu dữ liệu thời gian thực.

---

## 2. Kiến trúc Hệ thống & Công cụ (System Architecture & Tooling)

### 2.1 Cài đặt vòng lặp ReAct
*Quy trình suy luận của hệ thống dựa trên mô hình Thought-Action-Observation.*
- **Thought**: Agent phân tích câu hỏi của người dùng và quyết định hành động tiếp theo.
- **Action**: Agent gọi một công cụ cụ thể với tham số phù hợp (ví dụ: `check_stock(iphone)`).
- **Observation**: Hệ thống thực thi công cụ thật và trả về kết quả cho Agent. 
Vòng lặp này lặp lại cho đến khi Agent có đủ thông tin để đưa ra **Final Answer**.

### 2.2 Danh sách Công cụ (Tools Inventory)
| Tên công cụ | Định dạng Đầu vào | Mục đích sử dụng |
| :--- | :--- | :--- |
| `check_stock` | `chuỗi (item_name)` | Kiểm tra số lượng tồn kho của một sản phẩm. |
| `get_item_price` | `chuỗi (item_name)` | Lấy đơn giá của một sản phẩm. |
| `get_discount_code` | `chuỗi (code)` | Trả về tỷ lệ phần trăm giảm giá dựa trên mã coupon. |
| `calculate_shipping`| `số thực (weight), chuỗi (destination)`| Tính phí vận chuyển dựa vào khối lượng và thành phố. |

### 2.3 Các LLM Provider đã sử dụng
- **Chính (Primary)**: Mô hình Local `Phi-3-mini-4k-instruct-q4.gguf` chạy qua `llama-cpp-python` (tối ưu hóa n_gpu_layers và caching).
- **Phụ (Secondary/Backup)**: Google Gemini (`gemini-3.5-flash`), OpenAI.

---

## 3. Bảng phân tích Hiệu năng (Telemetry & Dashboard)

*Phân tích các chỉ số thu thập được trong quá trình chạy thử nghiệm cuối cùng.*

- **Độ trễ trung bình (Average Latency)**: ~8200ms (Do chạy model GGUF trên Local).
- **Độ trễ tối đa (Max Latency)**: ~14286ms (Khi câu hỏi yêu cầu gọi hơn 3 công cụ liên tiếp).
- **Số lượng Token trung bình (Average Tokens per Task)**: ~600 - 1800 tokens.
- **Tổng chi phí (Total Cost)**: $0.00 (Chạy 100% Local model không tốn phí API).

---

## 4. Phân tích Nguyên nhân Gốc rễ Lỗi (RCA - Failure Traces)

*Phân tích chuyên sâu về lý do tại sao Agent v1 bị lỗi.*

### Case Study: Ảo giác Tham số & Không đợi Observation
- **Đầu vào (Input)**: "Tôi muốn mua 2 iPhone dùng mã 'WINNER' và ship về Hà Nội. Tổng tiền là bao nhiêu?"
- **Kết quả quan sát (Observation)**: Ở phiên bản Agent v1, LLM sinh ra `Action: check_stock(iphone)` nhưng ngay lập tức ở cùng một dòng nó tự bịa ra `Final Answer: ...` mà không chịu dừng lại để chờ hệ thống gọi Tool.
- **Nguyên nhân gốc rễ (Root Cause)**: Do System Prompt quá sơ sài, thiếu các ví dụ mẫu (Few-Shot) hướng dẫn cách dừng quá trình sinh chữ (generation) sau khi gọi `Action`. Các mô hình nhỏ (như Phi-3) thường có xu hướng trả lời tuột luốt. Cần phải can thiệp cắt bớt (truncate) phần ảo giác và ép nó gọi lại Tool.

---

## 5. Nghiên cứu Đánh giá (Ablation Studies & Experiments)

### Thử nghiệm 1: Prompt v1 (Cơ bản) vs Prompt v2 (Few-Shot & Strict Rules)
- **Sự thay đổi (Diff)**: Bổ sung các ví dụ Few-Shot cụ thể bằng tiếng Việt, ép buộc định dạng (Ví dụ: `DỪNG LẠI sau khi viết Action... KHÔNG ĐƯỢC tự viết Observation`), và cập nhật logic Code ưu tiên phân tích Regex của `Action` trước khi xét `Final Answer`.
- **Kết quả (Result)**: Giảm tỷ lệ lỗi (ảo giác action) từ 80% xuống 0%. Agent v2 hoàn toàn tuân thủ luồng gọi Tool từng bước.

### Thử nghiệm 2: Chatbot Cơ bản vs ReAct Agent
| Trường hợp | Kết quả Chatbot | Kết quả Agent | Phân định Winner |
| :--- | :--- | :--- | :--- |
| Câu hỏi xã giao cơ bản | Trả lời nhanh, mượt | Trả lời hơi chậm (bị overhead) | **Chatbot** |
| Câu hỏi đa bước (tồn kho, giá, ship) | Ảo giác số liệu, bịa giá | Tính toán chuẩn xác từng USD | **Agent** |

---

## 6. Đánh giá Mức độ Sẵn sàng cho Thực tế (Production Readiness Review)

*Các điểm cần lưu ý nếu muốn đưa hệ thống này ra môi trường doanh nghiệp thực tế.*

- **Bảo mật (Security)**: Cần có lớp kiểm tra (Sanitization) các tham số đầu vào của Tool để chống SQL Injection hoặc Lỗ hổng thi hành mã từ xa.
- **Bảo vệ rủi ro (Guardrails)**: Đã thiết lập giới hạn vòng lặp `max_steps = 5` để ngăn Agent lặp vô hạn, giúp chống tiêu tốn tiền API (nếu dùng OpenAI/Gemini) hoặc chống nghẽn RAM/CPU (nếu dùng Local).
- **Khả năng mở rộng (Scaling)**: FastAPI hiện tại đã được nâng cấp với **Global LLM Instance Caching**, giúp tăng tốc độ đáng kể. Tuy nhiên để scale lên hàng ngàn user, cần chuyển đổi LLM Provider sang các cụm vLLM hoặc dùng mô hình Message Queue (Redis/Celery) để tránh sập máy chủ web.
