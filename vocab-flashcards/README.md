# Thẻ từ vựng N2 (flashcard artifact)

Flashcard ôn từ vựng N2 (Riki「言葉ゲームの漂流記」) kiểu Anki, publish thành Claude artifact.

- `data/vocab-XXX-YYY.json` — dữ liệu từ vựng, mỗi file một dải số từ. `id` là số thứ tự trong sách (dùng làm khoá lưu tiến độ, không được đổi), `l` là số bài.
- `template.html` — giao diện + logic (SM-2, phát âm bằng Web Speech, đồng bộ tiến độ qua capability `db`).
- `build.py` — gộp mọi file `data/vocab-*.json` vào `template.html` thành `index.html` (file được publish).

Hiện có đủ bài 1–93 (từ 1–930). Sửa hoặc thêm từ: chỉnh file `data/vocab-*.json` tương ứng (file mới theo cùng cấu trúc), chạy `python3 build.py`, rồi publish lại `index.html` lên cùng URL artifact. Loại từ (`pos`): `n`, `v`, `vs`, `na`, `i`, `adv`.
