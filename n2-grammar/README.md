# Sổ tay ngữ pháp N2

Tổng hợp ngữ pháp JLPT N2 từ *Mimikara 110 mẫu* và *Shinkanzen N2*, gộp theo nhóm nghĩa.

- `index.html`: trang hoàn chỉnh (thẻ ngữ pháp, sơ đồ tư duy, bảng cụm dễ nhầm, quy tắc & cách đọc, ngăn ghi chú).
- `src/data*.js`: dữ liệu từng nhóm ngữ pháp. Cú pháp `{漢字|かんじ}` là furigana, `[[...]]` là phần tô sáng.
- `src/compare.js`: bảng cụm dễ nhầm, bảng cách đọc, quy tắc loại đáp án.
- `src/mindmap.js`: quan hệ giữa các mẫu trong sơ đồ tư duy.
- `src/template.html`: giao diện và mã JS.

Sửa dữ liệu trong `src/` rồi chạy `python3 build.py` để tạo lại `index.html`.

Ghi chú và tiến độ được lưu vào tài khoản khi mở trang dưới dạng Artifact trên claude.ai; mở file trực tiếp thì lưu trên trình duyệt.
