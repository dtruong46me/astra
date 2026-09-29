# Luyện đề N2 (DORA Nihongo)

Một trang duy nhất chứa toàn bộ đề: https://claude.ai/artifact/McgkzL1p4ubcdAq5VbB8dk

- Chế độ làm bài: chỉ có câu hỏi, có đồng hồ; đáp án và giải thích chỉ hiện sau khi nộp.
- Chế độ xem lại: điểm, đánh dấu đúng/sai, lọc câu sai, giải thích từng câu (đáp án, dịch câu,
  từ vựng + Hán Việt + cách đọc, phương án nhiễu, ngữ pháp, ghi chú mở rộng), bảng đáp án.

Cấu trúc:
- `exams/*.json` – nội dung + giải thích từng đề (`no` = số đề theo thư mục Drive 1–20)
- `catalog.json` – 20 ô đề và link thư mục Drive tương ứng
- `app.html` – giao diện
- `python3 build.py` → `dist/index.html`
