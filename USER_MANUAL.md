# Hướng Dẫn Sử Dụng Mindfun

> *Mindfun - Không cấm đoán, chỉ tạo khoảng dừng tỉnh thức.*

## 1. Giới thiệu
Mindfun là một ứng dụng trên Windows được thiết kế dựa trên nguyên lý **"Ma sát hành vi" (Behavioral Friction)**. Thay vì cấm hoàn toàn việc chơi game, phần mềm sẽ tạo ra một khoảng thời gian chờ bắt buộc trước khi bạn vào game. Khoảng dừng này nhằm mục đích để lý trí của bạn có cơ hội thức tỉnh và can thiệp trước những xung động nhất thời.

## 2. Cài đặt và Khởi chạy
- Bạn có thể chạy file cài đặt `MindfunSetup.exe` (nằm trong thư mục `installer/Output/`).
- Sau khi cài đặt, Mindfun sẽ tự động khởi động cùng Windows. Bạn có thể tìm thấy biểu tượng (icon) của Mindfun ở khay hệ thống (System Tray) góc dưới cùng bên phải màn hình.

## 3. Các Tính Năng Nổi Bật

- ⏱️ **Màn hình khóa đếm ngược (Lockscreen):** Yêu cầu chờ một khoảng thời gian trước khi có thể vào game. Có 5 mức độ từ 15 giây (Nhắc nhở) đến 5 phút (Thiết quân luật). Cửa sổ game sẽ bị thu nhỏ lại và màn hình chờ sẽ nằm đè lên trên (Always-on-Top).
- 🌙 **Khóa ban đêm (Sleep Lock):** Quản lý giờ giấc chơi game vào ban đêm để bảo vệ sức khỏe.
- 🔒 **Chặn thoát nhanh (Anti-Cheat / Friction Lock):** Khóa chức năng thoát dễ dàng từ khay hệ thống - điều này tạo thêm rào cản hành vi cần thiết.
- 📋 **Checklist & Câu hỏi:** Đưa ra những công việc chưa làm hoặc những câu hỏi để bạn tự hỏi bản thân trong lúc chờ đợi. 

## 4. Hướng dẫn Cấu hình (Settings)
Click chuột phải vào biểu tượng Mindfun ở khay hệ thống, chọn **"Mở Cài Đặt..."**. Giao diện cài đặt bao gồm 3 tab chính:

### 4.1. Tab: Cài Đặt Chung (General Settings)
Nơi chứa toàn bộ các tùy chỉnh cốt lõi của phần mềm:
- **Mức Độ Cam Kết:** 5 mức độ từ 15 giây (Nhắc nhở) đến 5 phút (Thiết quân luật). Mức 5 cho phép bạn tự do tùy chỉnh thời gian chờ.
- **Giờ đi ngủ (Sleep Lock):** Thiết lập khung giờ cấm chơi game ban đêm (mặc định 23:00 đến 05:00 sáng). Nếu mở game vào khung giờ này, màn hình sẽ có cảnh báo đỏ nghiêm khắc.
- **Chặn thoát nhanh (Anti-Cheat):** Nếu bật, nút **"Thoát Mindfun"** và **"Tạm dừng"** ở khay hệ thống sẽ bị ẩn đi, ép bạn phải dùng Task Manager nếu muốn gian lận.
- **Ngôn ngữ / Giao diện:** Cho phép đổi Tiếng Việt/English và bật/tắt Giao diện tối (Dark Mode).
- **Nút "Quản Lý Danh Sách Game":** Mở ra cửa sổ để bạn Thêm/Xóa các tựa game cần giám sát (Yêu cầu điền tên file `.exe` của game, VD: `LeagueClient.exe`). MindFun đã tích hợp sẵn danh sách 75 game phổ biến nhất để bạn dễ dàng lựa chọn.

### 4.2. Tab: Câu Hỏi Thức Tỉnh (Mindful Questions)
- Nơi bạn soạn các công việc chưa làm hoặc câu hỏi suy ngẫm để phần mềm tự động hiển thị ngẫu nhiên lúc đếm ngược.
- **Dùng làm Checklist:** Nếu bạn tích chọn mục này, bạn sẽ bắt buộc phải tick (✅) hoàn thành các công việc trên màn hình thì nút **PLAY** mới được mở khóa (áp dụng ở Mức 4 hoặc Mức 5 có bật "Bắt buộc làm Checkist").

### 4.3. Tab: Nhật Ký (Log)
- Theo dõi thống kê thời gian bạn đã chơi game mỗi ngày bằng biểu đồ trực quan.
- Hiển thị danh sách các lần bạn vi phạm (mở game vào giờ đi ngủ) để tiện tự kiểm điểm bản thân.

## 5. Trải Nghiệm Khi Mở Game
1. Bạn mở một tựa game đã được thêm vào Danh sách Game.
2. Mindfun sẽ phát hiện, tự động thu nhỏ cửa sổ game đó lại và hiện màn hình chờ đếm ngược.
3. Trong lúc đếm ngược, phần mềm chặn các phím tắt như `Alt + F4` để tránh việc bạn thoát màn hình chờ.
4. Hãy đọc các câu hỏi, hoặc tick vào checklist công việc. Chậm lại và hít thở.
5. Khi đếm ngược kết thúc:
   - Nhấn **PLAY**: Bạn quyết định chơi, cửa sổ game sẽ mở ra lại. (Quyền chơi game này sẽ được ghi nhớ và cho phép tới tận 05:00 sáng mai, không bị đếm ngược lại).
   - Nhấn **QUIT**: Cửa sổ game sẽ mở lại, nhưng kèm banner màu đỏ ở góc trên màn hình nhắc bạn hãy nhấn nút thoát game.

## 6. Nhật Ký & Gỡ Cài Đặt
- **Nhật ký:** Ở Tab "Nhật Ký", bạn có thể theo dõi thời gian mình đã chơi và các vi phạm (đặc biệt là chơi quá giờ đi ngủ ban đêm).
- **Gỡ cài đặt:** Chạy công cụ Uninstaller từ Control Panel của Windows. Hệ thống sẽ hỏi bạn có muốn giữ lại file cấu hình và nhật ký hay xóa toàn bộ không. Lựa chọn tùy thuộc vào ý muốn của bạn.
