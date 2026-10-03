# パワードリル N2 文字・語彙 · 文法 — app luyện đề

- `data/b01.js … b06.js`: sách 文字・語彙 — 30 回 + 10 集中トレーニング (câu hỏi, đáp án theo 別冊, dịch nghĩa, giải thích, ngữ pháp, từ vựng kèm Hán Việt và nhãn "Hay thi"/"Nhận diện").
- `data/g01.js … g06.js`: sách 文法 — 30 回 (問題1 chọn mẫu ngữ pháp, 問題2 sắp xếp câu ★ kèm thứ tự đúng, 問題3 đoạn văn kèm bản dịch) + 10 集中トレーニング; mỗi câu có dịch nghĩa, giải thích, phân tích 4 lựa chọn, mẫu ngữ pháp (cách nối, nghĩa, nhãn) và từ vựng.
- `app.html`: giao diện (tab 語彙 / 文法 / Từ vựng / Ngữ pháp / Thẻ; tự làm / xem đáp án, bảng tổng hợp cuối bài, flashcard từ vựng và ngữ pháp, lưu tiến độ).
- `node build.js` → `dist/index.html` (file publish làm Artifact).

Đáp án 文字・語彙: 集中トレーニング lấy từ dòng 【答え】 cuối mỗi trang, 30 回 lấy từ 別冊解答. Đáp án 文法 lấy từ 別冊解答 (gồm cả thứ tự sắp xếp của 問題2).
