#!/usr/bin/env python3
"""直した文のうち、意味が変わったかもしれない文だけを原文の文に戻す。

使い方:
    python3 revert_broken.py 原文.md 直した文.md 出力.md [--request 依頼.md]

--request には、ユーザーの依頼文を保存したファイルを渡す。依頼の中に出てくる値
（伏せるよう頼まれた番号、変えるよう頼まれた日時など）は、頼まれた直しとして戻さない。

check_meaning.py と同じ基準で原文と直した文を比べ、候補が出た所について、
原文の該当する文と、直した文の中でいちばん近い文を探し、その文を原文の文に置き換える。
原文の文が直した文から丸ごと消えている時は、近い位置に原文の文を差し込む。
候補が無くなるか、それ以上減らなくなるまで繰り返す（最大6回）。

標準ライブラリだけで動く。戻した文は一覧で出す。
"""
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_meaning import check, norm, MODALITY, NEG, NUM, CONTENT  # noqa: E402

SENT = re.compile(r"[^。！？!?\n]+[。！？!?]?")


def spans(text):
    return [(m.start(), m.end(), m.group()) for m in SENT.finditer(text) if m.group().strip()]


def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def is_heading(t):
    return bool(re.match(r"\s*#+\s", t)) or (len(t.strip()) < 25 and not re.search(r"[。！？!?]$", t.strip()) and t.strip().startswith("**"))


def best(sent, cands):
    """cands の中で sent にいちばん近いものの番号と近さ。見出しの行は相手にしない。"""
    scores = [0.0 if is_heading(c[2]) else sim(sent, c[2]) for c in cands]
    if not scores:
        return None, 0.0
    i = max(range(len(scores)), key=scores.__getitem__)
    return i, scores[i]


def owner_of(S, D):
    """原文の各文が、直した文のどの文に当たるか。近さが同じなら、同じ位置の文を選ぶ
    （担当や時刻を入れ替えた2文を、片方の文にまとめて戻さないため）。"""
    out = []
    for k, s in enumerate(S):
        best_i, best_sc = None, -1.0
        for i, d in enumerate(D):
            if is_heading(d[2]):
                continue
            pos = 1 - abs(k / max(len(S) - 1, 1) - i / max(len(D) - 1, 1))
            sc = sim(s[2], d[2]) + 0.05 * pos
            if sc > best_sc:
                best_i, best_sc = i, sc
        out.append(best_i)
    return out


def words_of(item):
    """候補の行から、原文の文を探すための手がかりの語を取り出す。"""
    m = re.match(r"\[(数値・日時|曜日|コード|URL)\] 原文にあって直した文で減ったもの: (.*)", item)
    if m:
        return [x.strip() for x in m.group(2).split(", ") if x.strip()], "lost"
    m = re.match(r"\[確かさ・強さ\] 「(.+?)」の言い方が(減った|増えた)", item)
    if m:
        return MODALITY[m.group(1)], ("lost" if m.group(2) == "減った" else "added")
    m = re.match(r"\[程度・約束\] 「(.+?)」が減った", item)
    if m:
        return [m.group(1)], "lost"
    m = re.match(r"\[(数値・日時|曜日|コード|URL)\] 直した文で増えたもの: (.*)", item)
    if m:
        return [x.strip() for x in m.group(2).split(", ") if x.strip()], "added"
    if item.startswith("[否定]"):
        return None, "neg"
    m = re.match(r"\[組み合わせ\] 「(.+?)」", item)
    if m:
        return [m.group(1)], "pair"
    m = re.match(r"\[消えた中身\] 中身の言葉が半分以上見当たらない文: (.*)", item)
    if m:
        return m.group(1), "gone"
    return None, None


PREFIX = re.compile(r"^\s*(?:\*\*[^*\n]+\*\*[:：]?\s*|[-*・]\s+|#+\s+|\d+[.)]\s+)")


def fit(orig, place):
    """原文の文を戻す時、行頭の見出し・箇条書きの記号は、置き換える先に合わせる。"""
    body = PREFIX.sub("", orig, count=1).strip()
    m = PREFIX.match(place)
    return (m.group(0) if m else "") + body


def has(s, ws):
    s = norm(s)
    return any(w in s for w in ws)


# 依頼文の読み方。値が依頼に出てくるだけでは「変えてよい」にしない。
# その値が出てくる依頼の文に、変える指示があり、残す・変えない指示が無い時だけ、頼まれた直しとみなす。
KEEP = re.compile(r"維持|そのまま|元のまま|変更しない|変えない|変えず|変更せず|残して|残す|保持|しないで|せずに")
CHANGE = re.compile(r"変更|変え|置き換|置換|書き換|直して|伏せ|非公開|マスク|隠|にして|にする|に修正|削除|消して|消す|外して|除いて|取り除")
MASK = re.compile(r"[［\[【〔(（][^］\]】〕)）]{1,12}[］\]】〕)）]|[●○＊*×Xx]{2,}")
MASK_WORDS = re.compile(r"伏せ|伏字|非公開|マスク|隠|黒塗り|置き換")
MASK_PLAIN = r"非公開|伏せ字|伏字|非表示|秘匿"   # 括弧なしで書かれた伏字
EMAIL = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"
PHONE = r"\+?[0-9０-９]{2,4}[-－‐][0-9０-９]{2,4}[-－‐][0-9０-９]{3,4}|[0-9０-９]{10,11}"
VALUE = re.compile(EMAIL + "|" + PHONE)
TOKEN = re.compile("|".join([MASK.pattern, MASK_PLAIN, EMAIL, PHONE, NUM.pattern, r"[\s\S]"]))
AFTER_VALUE = re.compile(r"^(?:まで|宛て|宛|へ|に)")


def req_sentences(request):
    return [s for s in re.split(r"[。！？!?\n]", norm(request)) if s.strip()]


def req_clauses(request):
    return [s for s in re.split(r"[。！？!?\n、，,]", norm(request)) if s.strip()]


def allowed(w, request):
    """依頼の中で、値 w を変えるよう頼まれているか。分からない時は頼まれていない扱い。"""
    w = norm(w).strip()
    if not w or not request:
        return False
    hit = [s for s in req_sentences(request) if w in s]
    if not hit:
        return False
    return all(not KEEP.search(s) for s in hit) and any(CHANGE.search(s) for s in hit)


def is_mask(seg):
    seg = seg.strip()
    return bool(seg) and bool(MASK.fullmatch(seg) or re.fullmatch(MASK_PLAIN, seg))


def label_of(before):
    """値の直前にある項目名（電話番号は〜 の「電話番号」）。無ければ空。"""
    words = CONTENT.findall(norm(before)[-12:])
    return words[-1] if words else ""


def value_ok(value, before, request):
    """原文の値 value を、依頼どおりに変える・伏せる・消してよいか。
    値そのものか、その項目名が、変える指示のある依頼の節に出てくる時だけ認める。
    同じ値か項目名が、残す指示のある節に出てくる時は認めない（定員は20名を維持、など）。"""
    if not request:
        return False
    v, label = norm(value).strip(), label_of(before)
    if not v:
        return False
    clauses = req_clauses(request)
    for c in clauses:
        if KEEP.search(c) and (v in c or (label and label in c)):
            return False
    for c in clauses:
        if not CHANGE.search(c) or KEEP.search(c):
            continue
        if v in c or (label and label in c):
            return True
        if re.fullmatch(PHONE, v) and re.search(r"電話|番号|TEL|tel", c):
            return True
        if re.fullmatch(EMAIL, v) and re.search(r"メール|アドレス|連絡先", c):
            return True
    return False


def allowed_new(seg, request, old="", before=""):
    """直した文に入った語 seg が、依頼で頼まれた置き換え（伏字など）か。
    伏字は、伏せる元の値（old）が依頼で伏せてよい物の時だけ認める。"""
    seg = seg.strip()
    if not seg or not request:
        return False
    if is_mask(seg):
        if not (MASK_WORDS.search(norm(request)) or seg in norm(request)):
            return False
        return value_ok(old, before, request) if old.strip() else True
    if old.strip() and not value_ok(old, before, request) and not allowed(old, request):
        return False
    return allowed(seg, request) if len(seg) >= 2 else False


def allowed_lost(w, src, request):
    """原文から減った値 w が、依頼で変える・伏せる・消すよう頼まれた物か。"""
    if allowed(w, request):
        return True
    n = norm(src)
    for m in TOKEN.finditer(n):
        if w in m.group() and (VALUE.fullmatch(m.group()) or NUM.fullmatch(m.group())):
            if value_ok(m.group(), n[max(0, m.start() - 12):m.start()], request):
                return True
    return False


def tokens(text):
    return TOKEN.findall(text)


def keep_requested(orig, draft, request):
    """原文の文に戻す時も、依頼で頼まれた置き換え（伏字など）は、直した文のまま残す。
    比べるのは文字ではなく値の単位（15時、03-0000-0000）なので、15時→16時 も1つの変更として扱う。"""
    if not request:
        return orig
    A, B = tokens(orig), tokens(draft)
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    out = []
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        old, new = "".join(A[a1:a2]), "".join(B[b1:b2])
        before = "".join(A[max(0, a1 - 8):a1])
        if op in ("replace", "insert") and allowed_new(new, request, old, before):
            out.append(new)
        elif op == "insert":
            continue
        elif op == "delete" and value_ok(old, before, request):
            continue
        else:
            out.append(old)
    return "".join(out)


def strip_requested(s, request, new_side=False):
    """依頼で変える・伏せる・消すよう頼まれた値（伏字や新しい値）を文から抜く。
    抜いた後の2文を比べて、ほかに違いが無ければ、その文は頼まれた直しだけの文とみなす。"""
    out, pos = [], 0
    for m in TOKEN.finditer(s):
        tok = m.group()
        if new_side:
            drop = is_mask(tok) and MASK_WORDS.search(norm(request)) or (
                (NUM.fullmatch(tok) or VALUE.fullmatch(tok)) and allowed(tok, request))
        else:
            drop = (NUM.fullmatch(tok) or VALUE.fullmatch(tok)) and value_ok(tok, s[max(0, m.start() - 12):m.start()], request)
        if drop:
            out.append(s[pos:m.start()])
            pos = m.end()
            a = AFTER_VALUE.match(s[pos:])
            if a:
                pos += a.end()
    out.append(s[pos:])
    return "".join(out)


def requested_only(orig, draft, request):
    """直した文 draft と原文の文 orig の違いが、依頼で頼まれた直しだけか。"""
    if not request or orig.strip() == draft.strip():
        return False
    a, b = strip_requested(orig, request), strip_requested(draft, request, new_side=True)
    if a == orig and b == draft:
        return False
    return not check(a, b) and sim(a, b) >= 0.6


def requested_mask_exists(orig, drafts, request):
    """伏字以外が原文と一致する文（依頼で頼まれた直しだけの文）が、下書きに残っているか。"""
    if not request:
        return False
    return any(requested_only(orig.strip(), d.strip(), request) for _, _, d in drafts)


def one_pass(src, dst, request=""):
    """候補を1つずつ見て、戻す文を決めて置き換える。戻した記録も返す。"""
    items = check(src, dst)
    if not items:
        return dst, []
    S, D = spans(src), spans(dst)
    req = norm(request)
    owner = owner_of(S, D)  # 原文の各文が、直した文のどの文に当たるか
    # 依頼で頼まれた直しだけの文は、戻さない（電話番号を消した文、伏せた文など）
    protected = set()
    for i, d in enumerate(D):
        ks = [k for k, o in enumerate(owner) if o == i]
        if len(ks) == 1 and requested_only(S[ks[0]][2], d[2], request):
            protected.add(i)
    replace = {}   # 直した文の番号 → 置き換える原文の文
    insert = []    # (直した文の番号の後ろ, 原文の文)
    used = set()   # 戻すのに使った原文の文

    def put(i, sent):
        if i in replace or i in protected or sent in used:
            return
        # 原文の2文以上を1文にまとめた文なら、まとめた元の文を全部戻す（片方だけ戻して中身を落とさない）
        group = [s[2] for k, s in enumerate(S) if owner[k] == i and s[2] not in used]
        if sent not in group:
            group = [sent]
        replace[i] = "".join(group)
        used.update(group)

    def add(p, sent):
        if sent not in used:
            insert.append((p, sent))
            used.add(sent)
    for item in items:
        ws, kind = words_of(item)
        if req and kind in ("lost", "added") and ws:
            ws = [w for w in ws if not allowed_lost(w, src, request)]  # 変えるよう頼まれた値は戻さない
            if not ws:
                continue
        if kind == "pair":
            # 話題の語を含む文どうしで、いちばん近い組を戻す（似た形の別の文と取り違えない）
            idx = [k for k, d in enumerate(D) if ws[0] in d[2]]
            for s in S:
                if ws[0] in s[2] and idx:
                    j, sc = best(s[2], [D[k] for k in idx])
                    if j is not None and sc >= 0.45:
                        put(idx[j], s[2])
            continue
        if kind in ("lost", "neg"):
            for s in S:
                if kind == "lost" and not has(s[2], ws):
                    continue
                i, sc = best(s[2], D)
                if i is None or sc < 0.45:
                    continue
                if kind == "lost" and has(D[i][2], ws):
                    continue
                if kind == "neg" and len(NEG.findall(norm(s[2]))) == len(NEG.findall(norm(D[i][2]))):
                    continue
                put(i, s[2])
        elif kind == "added":
            for i, d in enumerate(D):
                if not has(d[2], ws):
                    continue
                j, sc = best(d[2], S)
                if j is not None and not has(S[j][2], ws):
                    put(i, S[j][2])
        elif kind == "gone":
            s = next((x for x in S if x[2].strip().startswith(ws[:20])), None)
            if s is None:
                continue
            # 伏字化して残っている文を、消えた文として原文のまま差し込まない。
            if requested_mask_exists(s[2], D, request):
                continue
            k = S.index(s)
            if owner[k] in protected:
                continue
            prev = best(S[k - 1][2], D)[0] if k > 0 else None
            add(prev, s[2])
    if not replace and not insert:
        return dst, []
    log = []
    out, last = [], 0
    ins_after = {}
    for p, s in insert:
        ins_after.setdefault(p, []).append(s)
    if None in ins_after:
        for s in ins_after[None]:
            if s.strip() not in dst:
                out.append(PREFIX.sub("", s, count=1).strip() + "\n\n")
                log.append(f"差し込んだ：{s.strip()[:50]}")
    for i, (a, b, t) in enumerate(D):
        out.append(dst[last:a])
        new = fit(keep_requested(replace[i], t, request), t) if i in replace else t
        if i in replace and new.strip() != t.strip():
            out.append(new)
            log.append(f"戻した：{t.strip()[:30]} → {new.strip()[:30]}")
        else:
            out.append(t)
        for s in ins_after.get(i, []):
            if s.strip() not in dst:
                out.append(PREFIX.sub("", s, count=1).strip())
                log.append(f"差し込んだ：{s.strip()[:50]}")
        last = b
    out.append(dst[last:])
    return "".join(out), log


def remaining(src, dst, request=""):
    """戻した後に残る候補。依頼で変える・伏せる・消すよう頼まれた値だけの候補は数えない。"""
    out = []
    for item in check(src, dst):
        ws, kind = words_of(item)
        if request and kind == "lost" and ws and all(allowed_lost(w, src, request) for w in ws):
            continue
        if request and kind == "added" and ws and all(allowed(w, request) for w in ws):
            continue
        out.append(item)
    return out


def main():
    args = sys.argv[1:]
    request = ""
    if "--request" in args:
        k = args.index("--request")
        request = open(args[k + 1], encoding="utf-8").read()
        del args[k:k + 2]
    if len(args) != 3:
        print(__doc__)
        sys.exit(2)
    src = open(args[0], encoding="utf-8").read()
    dst = open(args[1], encoding="utf-8").read()
    logs = []
    n = len(remaining(src, dst, request))
    for _ in range(6):
        new, log = one_pass(src, dst, request)
        m = len(remaining(src, new, request))
        if not log or m >= n:
            break
        dst, n = new, m
        logs += log
    with open(args[2], "w", encoding="utf-8") as f:
        f.write(dst)
    if logs:
        print(f"{len(logs)}か所を原文に戻しました。")
        for x in logs:
            print("- " + x)
    else:
        print("戻した所はありません。")
    rest = remaining(src, dst, request)
    if rest:
        print(f"残っている候補が{len(rest)}件あります（読み比べて、同じ意味ならそのままでよい）：")
        for x in rest:
            print("- " + x)


if __name__ == "__main__":
    main()
