# Báo cáo Cá nhân: Lab 3 - Chatbot vs ReAct Agent

- **Họ và tên**: Tạ Văn Huấn
- **Student ID**: 2A202600984
- **Ngày**: 01/06/2026

---

## I. Đóng góp Kỹ thuật (15 Điểm)

*Mô tả đóng góp cụ thể vào mã nguồn của dự án.*

- **Các module đã triển khai**: `main.py` (API Server), `static/index.html`, `static/style.css`, `static/app.js`
- **Điểm nổi bật trong Code**: 
  - Đã xây dựng máy chủ FastAPI (`main.py`) để kết nối Frontend với Backend (Agent).
  - Triển khai endpoint `/chat` nhận request thông số provider (bao gồm Google, OpenAI, và Local Provider) cùng model.
  - Thiết kế giao diện Dark Mode/Neon với bố cục chia cột (Cột trái cho giao diện Chat, Cột phải cho Telemetry/Mind Inspector).
  - Viết logic Javascript (`app.js`) để render dữ liệu chuỗi suy luận (ReAct steps) dạng accordion gấp/mở mượt mà và hiển thị thông số hiệu năng (Latency, Token, Cost) theo thời gian thực.
- **Tài liệu hóa**: Giao diện đóng vai trò trực quan hóa quá trình *Thought -> Action -> Observation* của ReAct Agent, giúp nhóm dễ dàng debug và so sánh trực quan sức mạnh suy luận của ReAct Agent so với Chatbot thông thường.

---

## II. Phân tích Tình huống Lỗi (10 Điểm)

*Phân tích sự cố cụ thể gặp phải trong quá trình làm lab.*

- **Mô tả vấn đề**: API không lấy được dấu vết suy luận (traces) chính xác vì hệ thống Logger mặc định chỉ ghi log xuống file (qua `logger.py`) thay vì trả về cho Frontend qua API endpoint.
- **Nguồn log**: Báo cáo lỗi khi UI không nhận được trường `traces` trong JSON trả về.
- **Chẩn đoán**: FastAPI server gọi hàm `agent.run()` nhưng luồng log được ghi hoàn toàn độc lập. Cần một cơ chế chặn (hook) log tạm thời để hứng dữ liệu trả về cùng HTTP response mà không phá vỡ kiến trúc gốc của team.
- **Giải pháp**: Tôi đã tạo một custom logger hook (dùng monkey-patch đè lên `logger.log_event`) trực tiếp bên trong endpoint `/chat` để bắt các sự kiện "AGENT_THOUGHT", "AGENT_OBSERVATION" và lưu vào một mảng `local_traces` trước khi trả về cho Frontend, rồi sau đó khôi phục lại logger gốc.

---

## III. Góc nhìn Cá nhân: Chatbot vs ReAct (10 Điểm)

*Suy ngẫm về sự khác biệt trong khả năng suy luận.*

1.  **Suy luận**: Khối `Thought` giúp Agent tự phân tách một yêu cầu phức tạp (như tính tổng giá, tồn kho, giảm giá và phí vận chuyển) thành các bước nhỏ thay vì phải đoán mò một câu trả lời duy nhất như Chatbot thông thường.
2.  **Độ tin cậy**: ReAct Agent đôi khi hoạt động kém hoặc phản hồi chậm hơn Chatbot ở những câu hỏi giao tiếp xã giao thông thường, do nó bị gò bó vào format suy luận hoặc cố tìm cách gọi tool khi không cần thiết, dẫn đến tiêu tốn thời gian (latency cao) và token.
3.  **Quan sát (Observation)**: Kết quả từ môi trường giúp Agent nhận ra lỗi (ví dụ tool báo lỗi sai tham số hoặc hết hàng) và cho phép nó linh hoạt suy nghĩ lại để đổi hướng (ví dụ: sửa tham số đầu vào hoặc từ chối đơn hàng) ở bước tiếp theo thay vì đưa ra thông tin bịa đặt.

---

## IV. Cải tiến trong Tương lai (5 Điểm)

*Đề xuất mở rộng hệ thống AI Agent.*

- **Khả năng mở rộng**: Tách biệt API server và LLM Worker. Sử dụng Message Queue (như RabbitMQ/Redis) để xử lý các request suy luận dài của Agent, tránh làm treo/block FastAPI server khi có nhiều request đồng thời.
- **Độ an toàn**: Bổ sung cơ chế Human-in-the-loop: Đối với các action nhạy cảm (thanh toán, thay đổi dữ liệu), Frontend sẽ pop-up yêu cầu người dùng xác nhận trước khi cho phép Agent thực thi Tool đó.
- **Hiệu năng & Trải nghiệm**: Quản lý state bằng WebSockets/SSE (Server-Sent Events) thay vì HTTP Polling truyền thống để Frontend nhận được luồng suy nghĩ của LLM theo thời gian thực (Streaming UI) ngay khi LLM đang sinh text, giúp ứng dụng có cảm giác phản hồi tức thì.
