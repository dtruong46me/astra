# Thẻ từ vựng N2 (flashcard artifact)

Flashcard ôn từ vựng N2 (Riki「言葉ゲームの漂流記」) kiểu Anki, publish thành Claude artifact.

- `data/vocab-XXX-YYY.json` — dữ liệu từ vựng, mỗi file một dải số từ. `id` là số thứ tự trong sách (dùng làm khoá lưu tiến độ, không được đổi), `l` là số bài.
- `template.html` — giao diện + logic (SM-2, phát âm bằng Web Speech, đồng bộ tiến độ qua capability `db`).
- `build.py` — gộp mọi file `data/vocab-*.json` vào `template.html` thành `index.html` (file được publish).

Hiện có 1338 từ: bài 1–93 của sách (id 1–930) và 408 từ chỉ có trong danh sách 745 từ đã ra đề JLPT N2 2010–2024 (id 931–1338, `l` = 0, hiển thị là nhóm "Đề thi / Ngoài sách").
- `data/jlpt.json` — `{id: số lần ra đề}` cho mọi từ có trong danh sách đề thi (cả từ của sách). `build.py` gắn vào từng từ thành trường `jl`, dùng cho tag "Đề thi ×N" và bộ lọc "Đã ra đề / Ra đề ≥ 2 lần / Chưa ra đề".
- Sửa hoặc thêm từ: chỉnh file `data/vocab-*.json` tương ứng (file mới theo cùng cấu trúc), chạy `python3 build.py`, rồi publish lại `index.html` lên cùng URL artifact. Loại từ (`pos`): `n`, `v`, `vs`, `na`, `i`, `adv`, `pre` (tiền tố), `suf` (hậu tố), `exp` (cụm từ).
- `data/chains-*.txt` — tab "Nối chữ": các cây từ ghép nối theo kiểu 熟語しりとり (chữ Hán cuối của từ trên là chữ Hán đầu của từ dưới; một từ có thể rẽ nhiều nhánh). Từ có trong bộ thẻ chỉ ghi chữ, từ ngoài bộ ghi `語 よみ cấp HÁN VIỆT | nghĩa` (cấp N5–N1 là cấp tham khảo). `build.py` kiểm tra quy tắc nối, từ trùng và từ trong bộ thẻ trước khi gộp vào trang.
