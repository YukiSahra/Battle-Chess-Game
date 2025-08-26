## ⚙️ Cách hoạt động

1. **Kết nối:** Mỗi người chơi chạy client và kết nối đến server
2. **Chọn đội hình:** Chọn 4 tướng từ danh sách có sẵn (có thể trùng tướng)
3. **Tìm đối thủ:** Server tự động ghép cặp 2 người chơi
4. **Trận đấu:** Server mô phỏng trận chiến tự động theo luật đã định
5. **Kết quả:** Server trả về kết quả thắng/thua và log chi tiết

## 🛠️ Cấu trúc

```
├── server.py              # Server chính xử lý game
├── client.py              # Client console (text-based)
├── requirements.txt       # Dependencies
└── README.md             # File này
```

## 📦 Yêu cầu hệ thống

- **Python:** 3.7 trở lên
- **Thư viện:** 
  - `socket` (built-in)
  - `threading` (built-in) 
  - `json` (built-in)

## 🚀 Cách chạy

### 1. Chạy Server

```bash
python server.py
```

Server sẽ khởi động tại `localhost:8888` và chờ client kết nối.

### 2. Chạy Client (2 Client nếu test)

```bash
python client.py
```

### 3. Chơi game

1. Kết nối đến server
2. Chọn 4 tướng cho đội hình
3. Sẵn sàng chiến đấu
4. Chờ server ghép đối thủ
5. Xem kết quả trận đấu

## 🎯 Luật chơi

### Cơ chế chiến đấu:
1. **Theo lượt:** Team 1 tấn công → Team 2 phản công
2. **Mục tiêu:** Mỗi tướng đánh vào tướng còn sống đầu tiên của đối phương
3. **Điều kiện thắng:** Tiêu diệt hết tướng đối phương
4. **Giới hạn:** Tối đa 50 round để tránh vòng lặp vô hạn

### Ví dụ trận đấu:

**Team 1:** Warrior (HP:12), Mage (HP:8)  
**Team 2:** Archer (HP:10), Tank (HP:20)

**Round 1:**
- Team 1: Warrior đánh Archer (10→7 HP), Mage đánh Archer (7→2 HP)  
- Team 2: Archer đánh Warrior (12→8 HP), Tank đánh Warrior (8→6 HP)

**Round 2:**
- Team 1: Warrior đánh Archer (2→0 HP, chết), Mage đánh Tank (20→14 HP)
- Team 2: Tank đánh Warrior (6→4 HP)

*...và cứ thế cho đến khi có team thắng*

*Chúc bạn chơi game vui vẻ! 🎮*