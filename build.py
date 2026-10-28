"""Sinh tài liệu Markdown và web app từ data/ngay-*.json.

Chạy:  python3 build.py
Kết quả:
  ngay-N.md          bài học + bài tập (không có đáp án)
  dap-an-ngay-N.md   đáp án + giải thích
  app/index.html     web app luyện thi (gắn dữ liệu của mọi ngày)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
LETTERS = "ABCD"


def load_days():
    days = {}
    for f in sorted(ROOT.glob("data/ngay-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("examFile"):
            d["exam"] = json.loads((ROOT / "data" / d.pop("examFile")).read_text(encoding="utf-8"))
        days[d["day"]] = d
    return days


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def mcq_md(items, start=1):
    out = []
    for i, it in enumerate(items):
        kind = f" *({it['type']})*" if it.get("type") else ""
        out.append(f"**{start + i}.**{kind} {it['q']}")
        out.append("")
        out.append("   ".join(f"{LETTERS[j]}. {o}" for j, o in enumerate(it["options"])))
        out.append("")
    return "\n".join(out)


def key_md(items, start=1):
    out = []
    for i, it in enumerate(items):
        line = f"**{start + i}. {it['answer']}** ({it['tag']}): {it['explain']}"
        if it.get("evidence"):
            line += f"  \n   Câu chứa đáp án: *“{it['evidence']}”*"
        out.append(line)
    return "\n\n".join(out)


def transform_md(items, start):
    out = []
    for i, t in enumerate(items, start):
        out += [f"**{i}.** {t['source']}", f"   → {t['start']} ______________________________", ""]
    return out


def transform_key_md(items, start):
    return [f"**{i}.** {' / '.join(t['answers'])}  \n   ({t['tag']}) {t['explain']}\n" for i, t in enumerate(items, start)]


def sets_md(sets, start, key=False):
    """Các nhóm câu hỏi (có thể kèm bài đọc). Trả về (dòng, số câu tiếp theo)."""
    out, n = [], start
    for st in sets:
        out += [f"#### {st['title']}", ""]
        if st.get("directions"):
            out += [f"*{st['directions']}*", ""]
        if st.get("passage") and not key:
            out += [f"**{st.get('passageTitle', '')}**", ""] + [f"({i}) {p}\n" for i, p in enumerate(st["passage"], 1)]
        out += [key_md(st["items"], n) if key else mcq_md(st["items"], n), ""]
        n += len(st["items"])
    return out, n


def lesson_md(d):
    g, r, sp = d.get("grammar"), d.get("reading"), d.get("speaking")
    parts = [f"# Ngày {d['day']}: {d['grammarTopic']} · {d['vocabTopic']}",
             "", "> Làm bài xong mới mở `dap-an-ngay-%d.md`, hoặc làm trực tiếp trên web app để được chấm tự động." % d["day"],
             "", "## Kế hoạch hôm nay", "",
             table(["Khung giờ", "Bước", "Nội dung"], [[p["time"], p["step"], p["content"]] for p in d["plan"]])]
    if g:
        parts += ["", f"## Bài học: {d['grammarTopic']}"]
        for s in g["sections"]:
            parts += ["", f"### {s['title']}", "", table(s["headers"], s["rows"])]
        if g.get("notes"):
            parts += ["", "### Ghi nhớ", ""] + [f"- {n}" for n in g["notes"]]
        if g.get("traps"):
            parts += ["", "### Bẫy hay gặp", ""]
            for i, t in enumerate(g["traps"], 1):
                parts += [f"**{i}. {t['title']}**", f"- ❌ {t['wrong']}", f"- ✅ {t['right']}", f"- {t['why']}", ""]
    if d.get("grammarMcq"):
        parts += ["", "## Bài tập ngữ pháp", "", "### Sentence completion", "", mcq_md(d["grammarMcq"])]
    if d.get("transform"):
        parts += ["### Sentence transformation", ""] + transform_md(d["transform"], 11)
    if d.get("extra"):
        x = d["extra"]
        parts += [f"## {x['title']}", "", x["note"], ""]
        lines, n = sets_md(x["sets"], 1)
        parts += lines
        if x.get("transform"):
            parts += ["#### Viết lại câu", ""] + transform_md(x["transform"], n)
    if d.get("vocab"):
        parts += [f"## Từ vựng: {d['vocabTopic']}", "",
                  table(["Từ / cụm từ", "Từ loại", "Phiên âm", "Nghĩa", "Collocation", "Ví dụ"],
                        [[f"**{v['phrase']}**", v["pos"], v["ipa"], v["meaning"], v["colloc"], f"*{v['example']}*"] for v in d["vocab"]])]
    if d.get("vocabMcq"):
        parts += ["", "## Bài tập từ vựng", "", mcq_md(d["vocabMcq"])]
    if r:
        parts += [f"## Luyện đọc · giới hạn {r['minutes']} phút", "", f"### {r['title']}", ""]
        parts += [f"({i}) {p}\n" for i, p in enumerate(r["paragraphs"], 1)]
        parts += [mcq_md(r["questions"])]
    if d.get("exam"):
        where = ("Đề nằm ở phần ĐỀ MẪU cuối `study.md` (đừng kéo xuống ANSWER KEY), hoặc làm"
                 if d["exam"]["title"].startswith("Đề mẫu") else "Làm") + \
                " trên web app tab **Đề thi** để được chấm tự động và nghe phần Listening."
        parts += [f"## {d['exam']['title']}", "", d["exam"]["note"], "", where, ""]
    if sp:
        parts += [f"## Luyện nói: {d['speakingTopic']}", "", f"### {sp['introTitle']}", ""]
        parts += [f"> {l}" for l in sp["intro"]]
        parts += ["", f"**Khung trả lời:** {sp['frame']}", "", "**Câu cứu nguy:**", ""] + [f"- *{x}*" for x in sp["rescue"]]
        parts += ["", "### Câu hỏi của giám khảo", ""]
        for i, q in enumerate(sp["questions"], 1):
            parts += [f"{i}. **{q['q']}**  \n   Gợi ý: {q['hint']}"]
        parts += ["", "**Tiêu chí chấm:** " + "; ".join(sp["rubric"]) + ".", ""]
    if d.get("reviewQuiz"):
        parts += ["## Tổng kết: Quiz ôn tập", "", mcq_md(d["reviewQuiz"])]
    return "\n".join(parts).rstrip() + "\n"


def answers_md(d):
    r = d.get("reading")
    parts = [f"# Đáp án ngày {d['day']}", ""]
    if d.get("grammarMcq"):
        parts += ["## Bài tập ngữ pháp", "", key_md(d["grammarMcq"]), ""]
    if d.get("transform"):
        parts += ["## Viết lại câu", ""] + transform_key_md(d["transform"], 11)
    if d.get("extra"):
        x = d["extra"]
        parts += [f"## {x['title']}", ""]
        lines, n = sets_md(x["sets"], 1, key=True)
        parts += lines
        if x.get("transform"):
            parts += ["#### Viết lại câu", ""] + transform_key_md(x["transform"], n)
    if d.get("vocabMcq"):
        parts += ["## Bài tập từ vựng", "", key_md(d["vocabMcq"]), ""]
    if r:
        parts += ["## Luyện đọc", "", key_md(r["questions"]), "", "### Từ mới nên học", "",
                  table(["Từ", "Từ loại", "Phiên âm", "Nghĩa"], [[f"**{w['word']}**", w["pos"], w["ipa"], w["meaning"]] for w in r["newWords"]]), ""]
    if d.get("exam"):
        parts += [f"## {d['exam']['title']}", ""]
        for pa in d["exam"]["papers"]:
            parts += [f"### {pa['title']}", ""]
            for pt in pa["parts"]:
                if pt.get("items"):
                    parts += [key_md(pt["items"], pt["start"]), ""]
                parts += transform_key_md(pt.get("transform", []), pt["start"])
                if pt.get("script"):
                    parts += ["Lời thoại:", ""] + [f"> {l}  " for l in pt["script"]] + [""]
    if d.get("reviewQuiz"):
        parts += ["## Quiz tổng kết", "", key_md(d["reviewQuiz"])]
    return "\n".join(parts).rstrip() + "\n"


def check(d):
    """Đảm bảo mỗi câu trắc nghiệm có 4 lựa chọn và đáp án hợp lệ."""
    groups = [(k, d.get(k, [])) for k in ("grammarMcq", "vocabMcq", "reviewQuiz")]
    groups += [("reading", d.get("reading", {}).get("questions", []))]
    groups += [(st["key"], st["items"]) for st in d.get("extra", {}).get("sets", [])]
    groups += [(pt["key"], pt.get("items", [])) for pa in d.get("exam", {}).get("papers", []) for pt in pa["parts"]]
    for name, items in groups:
        for i, it in enumerate(items, 1):
            assert len(it["options"]) == 4 and it["answer"] in LETTERS, f"Ngày {d['day']} {name} câu {i}"
            assert it["answer"] in LETTERS and it.get("explain"), f"Ngày {d['day']} {name} câu {i} thiếu giải thích"


def main():
    days = load_days()
    for n, d in days.items():
        check(d)
        (ROOT / f"ngay-{n}.md").write_text(lesson_md(d), encoding="utf-8")
        (ROOT / f"dap-an-ngay-{n}.md").write_text(answers_md(d), encoding="utf-8")
    template = (ROOT / "app/template.html").read_text(encoding="utf-8")
    payload = json.dumps({"days": {str(k): v for k, v in days.items()}}, ensure_ascii=False).replace("</", "<\\/")
    html, count = re.subn(r'/\*__DATA__\*/\{"days":\{\}\}', lambda _: payload, template)
    assert count == 1, "Không tìm thấy chỗ gắn dữ liệu trong app/template.html"
    (ROOT / "app/index.html").write_text(html, encoding="utf-8")
    print(f"Đã build {len(days)} ngày: " + ", ".join(f"ngay-{n}.md" for n in days) + ", app/index.html")


if __name__ == "__main__":
    main()
