/* Cross links inside each comparison map: [rowA, rowB, type, label]
   type: similar = gần nghĩa, contrast = đối lập / so sánh, trap = bẫy dễ nhầm, related = liên quan */
const LINKS=[
[[0,3,"contrast","Bất ngờ, quá khứ ↔ có ý chí, tương lai"],[0,1,"similar","Đều bất ngờ; かと思うと không dùng cho bản thân"],[1,2,"similar","か〜ないかのうちに gần như đồng thời hơn"],[0,4,"related","矢先 thường đi với 'định làm'"],[3,5,"similar","次第 là bản trang trọng"]],
[[1,2,"similar","Gần như thay thế được; にあたって thiên về tích cực"],[0,1,"related","際に → に際して trang trọng hơn"],[2,3,"contrast","Quyết tâm ↔ thứ tự trước sau"],[0,5,"similar","際 = とき nói lịch sự"]],
[[0,1,"trap","Vた = sau khi; Vる = trong khi, để làm"],[3,4,"contrast","Hơn nữa ↔ một khi đã"],[2,5,"trap","Đều là 'về mặt'; đọc うえ ↔ じょう"]],
[[0,1,"similar","Gần như thay thế được"],[2,3,"similar","Văn viết, 'kéo theo'"],[4,5,"contrast","Tốt hoặc xấu ↔ chỉ xấu"],[0,7,"similar","Bản N3 dạng điều kiện"],[6,4,"related","Đang dần ↔ ngày càng"]],
[[0,6,"trap","Cộng thêm ↔ ngược hẳn"],[1,7,"similar","Văn viết ↔ văn nói"],[3,7,"similar","はもとより ≈ はもちろん"],[2,5,"similar","Mở rộng phạm vi"],[0,4,"similar","Đều cấm vế sau có ý chí"]],
[[0,1,"contrast","Chất liệu để sáng tạo ↔ căn cứ không lệch"],[1,2,"similar","Làm theo quy định, kế hoạch"],[5,6,"contrast","Chủ động điều chỉnh ↔ kết quả phụ thuộc"],[0,4,"trap","をもとに (元: gốc) ↔ のもとで (下: dưới)"]],
[[1,6,"trap","Thêm も: bất kể → mặc dù"],[0,1,"similar","Gần như thay thế được"],[3,4,"similar","Tạm gác; さておき dứt khoát hơn"],[4,5,"related","冗談はさておき／冗談抜きで"]],
[[6,7,"contrast","Sự thật cụ thể ↔ từ chỉ mức độ"],[2,3,"similar","つつも văn viết, đi với 思う, 知る"],[0,8,"similar","Văn viết ↔ văn nói"],[1,4,"related","Kết quả không như mong đợi"]],
[[0,1,"contrast","Khen hoặc chê ↔ chỉ khen"],[2,9,"similar","ばかりに ≈ せいで, thêm ý hối hận"],[2,3,"related","Đều dẫn tới kết quả xấu"],[5,0,"related","Suy từ tính cách ↔ từ lý do"]],
[[0,1,"contrast","Kết quả xấu ↔ có kết quả, quyết định"],[3,6,"similar","Trạng thái cứ để nguyên"],[4,7,"contrast","Lỡ mất ↔ may mà tránh được"],[2,5,"related","Cùng họ ところ"]],
[[1,2,"trap","Thêm ない: không thể → có thể (xấu)"],[3,4,"similar","Không có cách nào"],[5,6,"similar","Không thể xảy ra; っこない là văn nói"],[0,9,"contrast","Khó về tâm lý ↔ khó về vật lý"],[6,9,"similar","っこない ≈ はずがない"]],
[[0,1,"similar","に相違ない là bản văn viết"],[0,2,"contrast","Có căn cứ ↔ chủ quan"],[5,6,"similar","Khả năng xảy ra điều xấu"],[4,7,"contrast","Có vẻ thật ↔ như thể (không thật)"]],
[[0,1,"similar","Văn viết ↔ văn nói"],[2,3,"contrast","Vì đạo lý ↔ cảm xúc tự bật ra"],[4,5,"similar","Cảm xúc mạnh"],[0,6,"similar","Cùng chữ 得: bất đắc dĩ"]],
[[4,5,"trap","Thêm ない: không đời nào → mong sao"],[6,7,"trap","Thể khả năng ↔ thể ý chí"],[0,1,"contrast","Nên ↔ không nên"],[11,12,"contrast","Đúng là ↔ không phải cứ"],[2,3,"related","Cảm xúc nhìn lại"],[8,9,"trap","Tuy... nhưng ↔ vì"]],
[[0,1,"trap","Vる → lời khuyên; Aい → cảm thán"],[5,6,"contrast","Căn cứ ↔ tính cách người"],[6,7,"related","Đều nêu lý do"],[0,10,"contrast","Nên ↔ không cần"],[2,3,"related","Cảm thán"]],
[[1,2,"contrast","Chừng nào còn ↔ chừng nào chưa"],[4,7,"contrast","Chỉ riêng ↔ không chỉ"],[5,6,"trap","Là nhất ↔ đúng lúc thì lại"],[3,0,"related","Phạm vi, giới hạn"]],
[[0,2,"trap","Vた＋ばかり ↔ Vる＋ばかりだ"],[3,4,"trap","Không những ↔ chỉ vì"],[1,2,"related","Giọng phàn nàn"]],
[[0,1,"contrast","Đánh giá ↔ đoán cảm xúc người khác"],[0,4,"trap","Đánh giá ↔ hành động hướng tới"],[5,6,"trap","Có は: về khoản; không có: từ… đến"],[1,3,"similar","Nhìn từ một góc"]],
[[1,2,"trap","Không làm ↔ dù phải cũng làm"],[5,6,"contrast","Chỉ là ↔ chính là"],[0,3,"similar","Đến cả ↔ ngay cả"]]
];

/* Row → card pattern (exact p) where the automatic match is wrong or missing; null = no card */
const REFS={
"0:5":null,"1:4":"〜最中(に)／〜最中だ","1:5":"〜うちに","2:1":"〜る上で／Nの上で","2:2":"〜る上で／Nの上で","2:3":"〜上(に)","2:5":"〜上 (じょう)",
"4:4":"〜上(に)","6:5":"〜抜き(で)／〜抜きにして／〜を抜きにしては","7:3":"〜つつ(も)","7:6":"〜にしては","9:1":"〜末(に)","9:2":"〜たところ",
"10:9":"〜はずがない","12:1":"〜しかない／〜よりほかない","13:0":"〜ものだ／〜ものではない (lẽ thường)","13:1":"〜ものだ／〜ものではない (lẽ thường)",
"13:2":"〜たものだ (hồi tưởng)","13:3":"〜ものだ (cảm thán)","13:5":"〜ないものか／〜ないものだろうか","13:7":"〜(よ)うものなら",
"14:0":"〜ことだ (lời khuyên)","14:1":"〜ことだ (cảm thán)","14:2":"〜ことに","14:3":"〜ことか／〜ことだろう","15:1":"〜限り(は)／〜ない限り",
"17:2":"〜を〜として／〜として","17:6":null,"18:3":"〜さえ (ngay cả)"
};
