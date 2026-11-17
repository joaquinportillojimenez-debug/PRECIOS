"""Lee un _chat.txt de WhatsApp (iOS) y lo convierte en mensajes {i, dt, author, text}."""
import re, sys, json, unicodedata
LINE = re.compile(r"^‎?\[(\d{1,2})/(\d{1,2})/(\d{2}), (\d{1,2}):(\d{2}):(\d{2})\] ([^:]+?): ?(.*)$")
def parse(path):
    msgs = []
    for raw in open(path, encoding="utf-8").read().replace("\r\n", "\n").split("\n"):
        m = LINE.match(raw)
        if m:
            d, mo, y, H, M, S, author, text = m.groups()
            msgs.append({"i": len(msgs), "date": f"20{y}-{int(mo):02d}-{int(d):02d}",
                         "time": f"{int(H):02d}:{M}:{S}", "author": author.strip(), "text": text})
        elif msgs:
            msgs[-1]["text"] += "\n" + raw
    for m in msgs:
        m["text"] = m["text"].replace("‎", "").strip()
    return msgs
def norm(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
if __name__ == "__main__":
    msgs = parse(sys.argv[1])
    json.dump(msgs, open(sys.argv[2], "w"), ensure_ascii=False)
    print(len(msgs), "mensajes,", msgs[0]["date"], "->", msgs[-1]["date"])
