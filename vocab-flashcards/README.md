# Thẻ từ vựng N2 (flashcard artifact)

Flashcard ôn từ vựng N2 (Riki「言葉ゲームの漂流記」) kiểu Anki, publish thành Claude artifact.

- `data/vocab-XXX-YYY.json` — dữ liệu từ vựng, mỗi file một dải số từ. `id` là số thứ tự trong sách (dùng làm khoá lưu tiến độ, không được đổi), `l` là số bài.
- `template.html` — giao diện + logic (SM-2, phát âm bằng Web Speech, đồng bộ tiến độ qua capability `db`).
- `build.py` — gộp mọi file `data/vocab-*.json` vào `template.html` thành `index.html` (file được publish).

Hiện có bài 1–76 (từ 1–760). Thêm bài mới: tạo `data/vocab-761-860.json` (v.v.) theo cùng cấu trúc, chạy `python3 build.py`, rồi publish lại `index.html` lên cùng URL artifact. Loại từ (`pos`): `n`, `v`, `vs`, `na`, `i`, `adv`.
