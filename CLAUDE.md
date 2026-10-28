# Ôn thi tiếng Anh đầu vào thạc sĩ ĐH KHTN (ĐHQG-HCM) – 7 ngày

Claude đóng vai gia sư theo `study.md` (prompt gốc + đề mẫu). Mọi bài học nằm trong `data/*.json`, được build thành Markdown và một web app (Claude Artifact) có chấm tự động và lưu lỗi sai.

## Người học

- TOEIC: Listening 290, Reading 235, Speaking 80, Writing 120. Mục tiêu ≥ 55%.
- Mạnh nhất: Nghe. Yếu: Đọc hiểu, Nói, ngữ pháp nền.
- Lỗi lặp lại nhiều nhất (xem `loi-sai.md`):
  1. Dùng have/has + V3 dù câu có mốc quá khứ (last year, when I was young, before + V2).
  2. Thêm "been" vào câu chủ động (have been learned).
  3. where / which: chọn theo danh từ đứng trước thay vì nhìn phía sau chỗ trống.
  4. Viết lại câu điều kiện thiếu had / would; spend + to V.
- Hay chỉ nộp phần ngữ pháp, bỏ qua từ vựng/đọc/nói → nhắc làm đủ, nhất là Đọc và Nói (có điểm liệt).
- Chưa gửi thông tin cá nhân cho bài giới thiệu (tên, quê, ngành, trường, công việc, ngành thạc sĩ + lý do).

## Đề thi thật

Theo tài liệu ôn của trường (*Tài liệu ôn thi đầu vào sau đại học khóa tháng 3–4/2021 – 6 Practice Tests*, bán tại phòng Sau đại học KHTN Q5). **File PDF không nằm trong thư mục này**; nếu có, hãy lưu vào `tai-lieu/` để phiên sau đọc được.

- **Đậu: trung bình ≥ 50% và không phần nào bị điểm liệt** (ngưỡng liệt chưa rõ).
- Paper 1 Reading (60 phút): Vocabulary 1–10; **4 bài đọc**, câu 11–35.
- Paper 2 Grammar (30 phút): Sentence completion 36–45; **Error identification 46–55**; Cloze 56–65; Sentence transformation 66–70 (tự viết).
- Paper 3 Listening: 10 hội thoại ngắn 71–80; hội thoại dài 81–85; bài nói 86–90. Nghe 2 lần, dễ hơn TOEIC.
- Paper 4 Speaking: giới thiệu 4–5 câu (đừng đọc thuộc lòng); bốc thăm 1 chủ đề (đổi được 1 lần), nói qua lại với giám khảo, được hỏi lại.
- Cuối tài liệu có 20 mẫu viết lại câu (Practice 1–20), đã tóm tắt trong tab Tổng ôn của ngày 7.
- Đã dùng: Test 1 (ngày 5), Test 6 Paper 1+2 (đề thi thử 2, ngày 6), Test 2 bài đọc 4 (ngày 7). Test 2–5 còn lại có thể dùng luyện thêm (tài liệu không có đáp án và file nghe → Claude tự giải, tự viết lời thoại).
- `ĐỀ MẪU` ở cuối `study.md` (70 câu) là bản rút gọn cũ, không đúng format 90 câu.

## Quy trình

```
data/ngay-N.json (+ data/de-*.json)  →  python3 build.py  →  ngay-N.md, dap-an-ngay-N.md, app/index.html
app/index.html  →  Artifact publish lên https://claude.ai/artifact/5oLuJLbV2VLKPhyhFqXfYe
```

- Sửa giao diện trong `app/template.html` (không sửa `app/index.html`, file này được sinh ra).
- Republish bằng Artifact tool với `url` ở trên (artifact khai báo capability `db` + `sample`). Phiên mới phải `action: "read"` artifact trước khi publish.
- Dữ liệu người học nằm trong database của artifact (đọc bằng ArtifactData với url trên):
  - `mistakes`: mỗi câu sai `{day, section, tag, q, chosen, answer, at}`.
  - `scores`: id `d{N}-{key}` → `{day, section, score, total}`.
  - `progress/d{N}`: các bước kế hoạch đã tick. `known/d{N}`: cụm từ đã thuộc (bỏ qua khi soạn từ vựng mới).
- Sau mỗi lần chấm: cập nhật `loi-sai.md` (theo chủ điểm) và `tien-do.md`, đưa lỗi cũ vào bài các ngày sau.
- Kiểm tra trước khi publish: `python3 build.py` (tự kiểm tra 4 lựa chọn + đáp án + giải thích). Máy không có Node; không được tải Node về. Ít nhất kiểm tra cân bằng ngoặc của `<script>` cuối trong `app/index.html`.

## Định dạng `data/ngay-N.json`

Chỉ `day`, `grammarTopic`, `vocabTopic`, `speakingTopic`, `plan` là bắt buộc; tab nào không có dữ liệu thì app tự ẩn.

| Khóa | Tab | Nội dung |
|---|---|---|
| `plan` | Kế hoạch | `[{time, step, content}]`, `step: "Nghỉ"` không có ô tick |
| `grammar` | Ngữ pháp | `{sections: [{title, headers, rows}], notes: [], traps: [{title, wrong, right, why}]}` |
| `grammarMcq` + `transform` | Bài tập NP | MCQ `{q, options[4], answer "A–D", tag, explain}`; transform `{source, start, answers[], tag, explain}` (so khớp không phân biệt hoa thường/dấu câu, liệt kê đủ biến thể đúng) |
| `extra` | Luyện thêm | `{title, note, sets: [{key, title, directions?, passageTitle?, passage?: [đoạn], items}], transform?}` |
| `vocab` + `vocabMcq` | Từ vựng, Bài tập TV | vocab `{phrase, pos, ipa, meaning, colloc, example}` |
| `reading` | Đọc | `{title, minutes, paragraphs, questions (MCQ + type + evidence: chuỗi con đúng nguyên văn trong bài), newWords}` |
| `examFile` | Đề thi | tên file trong `data/` (vd `de-thi-2.json`) |
| `speaking` | Nói | `{introTitle, intro: [], frame, rescue: [], questions: [{q, hint}], rubric: []}` |
| `reviewQuiz` | Tổng kết | 10 MCQ |

Đề thi (`data/de-*.json`): `{title, meta?, note, papers: [{title, points? | minutes?, parts: [{key, title, directions?, start, items | transform, passageTitle?, passage?, script?}]}], speaking: {intro, topic, questions}}`.
- Không có `points` → app chấm theo % từng Paper (dùng cho format đề thật).
- Paper thứ 3 là Listening: item có `script` (mảng "Man: …"/"Woman: …") thì mỗi câu có nút nghe riêng; part có `script` thì nghe cả đoạn. App đọc bằng speechSynthesis, phát 2 lần.
- Câu Tìm lỗi sai: viết `"[When](A) she heard … [despite](D) …"`, options là 4 cụm gạch chân.
- `key` của part phải khác nhau trong cùng đề (điểm lưu theo `d{N}-{key}`).

## Lệnh người học

- **"Bắt đầu ngày N"**: đọc lỗi mới trong db + `loi-sai.md`, soạn/điều chỉnh `data/ngay-N.json`, build, republish.
- **"thi nói" / "thi nói thử"**: Claude làm giám khảo ngay trong chat, hỏi từng câu, sửa lỗi + gợi ý câu hay hơn, cuối cùng chấm ước tính.
- **"chấm bài"**, **"điểm"**, **"quiz"**, **"flashcard"**: xem `study.md`.

Quy tắc soạn bài: trình độ B1, đúng dạng đề trường, 4 lựa chọn A–D, đáp án phân bố đều, giải thích bằng tiếng Việt ngắn gọn, không đưa đáp án trước khi người học làm.

## Trạng thái (2026-10-28)

- Đã soạn đủ ngày 1–7. Ngày 4: đề thi thử 1 (70 câu, format cũ). Ngày 6: đề thi thử 2 (90 câu, đúng format, Test 6). Ngày 7: làm lại toàn bộ câu đã sai (lấy từ db lúc soạn) + 20 mẫu viết lại + 1 bài đọc.
- Bỏ: đề mẫu 70 câu của ngày 2, idiom.
- Điểm các ngày: xem `tien-do.md` và tab Sổ lỗi sai trong app.
