# Hướng Dẫn Cài Đặt và Chạy Dự Án

Tài liệu này hướng dẫn chi tiết cách thiết lập môi trường, cài đặt các thư viện cần thiết và chạy ứng dụng **E-commerce Chatbot vs ReAct Agent** trên máy tính cá nhân.

---

## 📋 Yêu Cầu Hệ Thống
* **Python**: Phiên bản `3.9` trở lên.
* **Hệ điều hành**: Windows, macOS, hoặc Linux.

---

## 🚀 Hướng Dẫn Từng Bước

### Bước 1: Khởi Tạo Môi Trường Ảo (Khuyên Dùng)
Môi trường ảo (virtual environment) giúp cô lập các thư viện của dự án này với hệ thống để tránh xung đột phiên bản.

1. Mở terminal tại thư mục gốc của dự án.
2. Chạy lệnh sau để tạo thư mục môi trường ảo tên là `venv`:
   ```bash
   python -m venv venv
   ```
3. Kích hoạt môi trường ảo:
   * **Trên Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * **Trên Windows (Command Prompt)**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   * **Trên macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```

Sau khi kích hoạt thành công, bạn sẽ thấy ký hiệu `(venv)` hiển thị ở đầu dòng lệnh của terminal.

---

### Bước 2: Cài Đặt Các Thư Viện Phụ Thuộc
Chạy lệnh sau để cài đặt toàn bộ thư viện cần thiết được định nghĩa trong file `requirements.txt`:
```bash
pip install -r requirements.txt
```

> [!NOTE]
> Thư viện `llama-cpp-python` (dùng để chạy mô hình Local offline trên CPU) yêu cầu máy tính của bạn phải cài đặt sẵn **C++ Build Tools**. 
> * Nếu bạn chỉ có nhu cầu sử dụng mô hình qua API của OpenAI hoặc Gemini và gặp lỗi khi cài đặt thư viện này, bạn có thể mở file `requirements.txt`, xóa dòng `llama-cpp-python` đi, sau đó thực hiện lại lệnh cài đặt trên.

---

### Bước 3: Cấu Hình Biến Môi Trường (API Keys)
1. Tạo một file mới tên là `.env` bằng cách sao chép file `.env.example`:
   ```bash
   cp .env.example .env
   ```
2. Mở file `.env` lên bằng trình soạn thảo và điền API Key của dịch vụ bạn muốn sử dụng:
   * `OPENAI_API_KEY`: API Key của OpenAI (nếu dùng GPT).
   * `GEMINI_API_KEY`: API Key của Google Gemini (nếu dùng Gemini).
   * `DEFAULT_PROVIDER`: Chọn nhà cung cấp mặc định (`google`, `openai`, hoặc `local`).

---

### Bước 4: Tải và Cấu Hình Mô Hình Local (Chạy Offline trên CPU)
Nếu bạn không muốn sử dụng API Key trực tuyến (của OpenAI hoặc Gemini), bạn có thể chạy mô hình mã nguồn mở (như **Phi-3**) trực tiếp trên CPU của máy tính thông qua `llama-cpp-python`.

1. **Tải Mô Hình**: Tải file mô hình **Phi-3-mini-4k-instruct-q4.gguf** (khoảng 2.2GB) từ Hugging Face:
   * [Trang tải Hugging Face](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf)
   * Link tải trực tiếp: [Phi-3-mini-4k-instruct-q4.gguf](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf)

2. **Thêm vào dự án**:
   * Tạo một thư mục tên là `models` ở thư mục gốc của dự án.
   * Di chuyển file `.gguf` vừa tải về vào trong thư mục `models/` này.

3. **Cấu hình file `.env`**:
   Mở file `.env` và cập nhật thông tin nhà cung cấp mặc định cũng như đường dẫn mô hình:
   ```env
   DEFAULT_PROVIDER=local
   LOCAL_MODEL_PATH=./models/Phi-3-mini-4k-instruct-q4.gguf
   ```

---

### Bước 5: Kiểm Tra Tích Hợp Hệ Thống
Để chắc chắn các công cụ (Tools) và logic của ReAct Agent được kết nối chính xác trước khi khởi động Web UI, chạy kiểm tra giả lập bằng lệnh:
```bash
python verify_integration.py
```
Nếu terminal hiển thị dòng chữ `✅ Internal logic and tool integration check PASSED!`, nghĩa là hệ thống đã sẵn sàng.

Bạn cũng có thể chạy bộ test tự động của dự án:
```bash
pytest
```

---

### Bước 6: Chạy Giao Diện Web (FastAPI)
Ứng dụng cung cấp một Dashboard điều khiển trực quan nằm ở file `src/server.py`. 

Khởi chạy máy chủ phát triển nội bộ bằng một trong hai cách:

* **Cách 1 (Chạy qua script)**:
  ```bash
  python src/server.py
  ```

* **Cách 2 (Chạy trực tiếp bằng uvicorn)**:
  ```bash
  python -m uvicorn src.server:app --reload
  ```

Khi máy chủ hoạt động, terminal sẽ hiển thị dòng chữ:
`INFO: Uvicorn running on http://127.0.0.1:8000`

Mở trình duyệt web của bạn và truy cập vào đường dẫn:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🛠️ Trải Nghiệm Ứng Dụng Trên Web

Sau khi truy cập giao diện Web, bạn có thể:
1. **Nhập API Key**: Có thể cấu hình trực tiếp từ giao diện nếu chưa điền ở file `.env`.
2. **Chọn Provider & Model**:
   * **OpenAI**: `gpt-4o`, `gpt-4o-mini`, v.v.
   * **Google Gemini**: `gemini-1.5-flash`, `gemini-1.5-pro`, v.v.
   * **Local**: Sử dụng mô hình định dạng `.gguf` chạy offline (đặt file mô hình trong thư mục `./models/` và cấu hình đường dẫn `LOCAL_MODEL_PATH` trong `.env`).
3. **Lựa chọn Chế độ chạy (Execution Mode)**:
   * **Chatbot (Baseline)**: Trả lời câu hỏi dựa trên kiến thức tĩnh sẵn có của mô hình LLM.
   * **ReAct Agent**: Thực hiện chu trình suy nghĩ - hành động - quan sát (`Thought-Action-Observation`), tự động kích hoạt các công cụ tra cứu thông tin thời gian thực (như xem hàng tồn kho, tính phí ship, áp dụng giảm giá) để đưa ra câu trả lời tối ưu nhất cho đơn hàng.
