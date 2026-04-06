"""
Assignment Feedback Application and Skill Development Tracking Survey
======================================================================
Module  : Fundamentals of Programming, 4BUIS008C  (Level 4)
Project : Coursework 1  —  GUI Version (Tkinter)

Run with:   python gui_app.py

Variable types used: int, str, float, list, tuple, range, bool, dict, set, frozenset
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import re
import csv
from datetime import datetime, date

# ─────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────
QUESTIONS_FILE:       str       = "questions.json"          # str
RESULTS_DIR:          str       = "data"                    # str
ALLOWED_FILE_FORMATS: tuple     = ("json", "csv", "txt")    # tuple
ALLOWED_NAME_CHARS:   frozenset = frozenset(                 # frozenset
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'"
)

# Colour palette
C: dict = {                                                  # dict
    "bg":       "#F7F5F0",
    "surface":  "#FFFFFF",
    "ink":      "#1A1814",
    "ink2":     "#5A5650",
    "ink3":     "#9A9690",
    "accent":   "#1D4ED8",
    "acc_lt":   "#EFF4FF",
    "success":  "#166534",
    "danger":   "#991B1B",
    "border":   "#E5E2DC",
}


# ═════════════════════════════════════════════════════════════════════
#  FILE / DATA FUNCTIONS
# ═════════════════════════════════════════════════════════════════════

def load_questions(fp: str) -> dict:
    """Load survey questions from external JSON file at runtime."""
    with open(fp, "r", encoding="utf-8") as f:
        data: dict = json.load(f)
    return data


def get_saved_files() -> list:
    """Return sorted list of saved result filenames."""
    files: list = []
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    for fn in os.listdir(RESULTS_DIR):
        if fn.endswith((".json", ".csv", ".txt")):
            files.append(fn)
    files.sort(reverse=True)
    return files


def save_result(rd: dict, fmt: str) -> str:
    """Save result dict to chosen format. Returns the filename."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    safe: str = re.sub(r"[^a-zA-Z0-9_]", "_", rd["surname"])
    ts: str   = datetime.now().strftime("%Y%m%d_%H%M%S")
    base: str = f"{safe}_{ts}"

    if fmt == "json":
        fname: str = base + ".json"
        with open(os.path.join(RESULTS_DIR, fname), "w", encoding="utf-8") as f:
            json.dump(rd, f, indent=4, ensure_ascii=False)

    elif fmt == "csv":
        fname = base + ".csv"
        fields: list = ["surname","given_name","dob","student_id",
                         "total_score","state_label","state_desc","timestamp","answers"]
        row: dict = {k: rd.get(k,"") for k in fields}
        row["answers"] = json.dumps(rd.get("answers", []))
        with open(os.path.join(RESULTS_DIR, fname), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader(); w.writerow(row)

    else:
        fname = base + ".txt"
        with open(os.path.join(RESULTS_DIR, fname), "w", encoding="utf-8") as f:
            f.write("=" * 52 + "\n  FEEDBACK APPLICATION & SKILL TRACKING SURVEY\n  RESULT RECORD\n" + "=" * 52 + "\n\n")
            for k, v in [("Surname", rd.get("surname","")), ("Given Name", rd.get("given_name","")),
                          ("DOB", rd.get("dob","")), ("Student ID", rd.get("student_id","")),
                          ("Timestamp", rd.get("timestamp","")), ("Total Score", rd.get("total_score",0)),
                          ("State", rd.get("state_label","")), ("Description", rd.get("state_desc",""))]:
                f.write(f"{k}: {v}\n")
            f.write("\nAnswers:\n")
            for a in rd.get("answers", []):
                f.write(f"  Q{a['question_id']}: {a['selected_option']} (score: {a['score']})\n")
    return fname


def load_result_file(fn: str) -> dict | None:
    """Load a previously saved result from disk."""
    path: str = os.path.join(RESULTS_DIR, fn)
    if not os.path.exists(path):
        return None
    result: dict = {}
    if fn.endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            result = json.load(f)
    elif fn.endswith(".csv"):
        with open(path, "r", encoding="utf-8", newline="") as f:
            rows: list = list(csv.DictReader(f))
            if rows:
                result = dict(rows[0])
                result["total_score"] = int(result.get("total_score", 0))
                result["answers"] = json.loads(result.get("answers", "[]"))
    elif fn.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            lines: list = f.readlines()
        for line in lines:
            line = line.strip()
            if ": " in line:
                k, _, v = line.partition(": ")
                result[k.lower().replace(" ", "_")] = v
        if "total_score" in result:
            result["total_score"] = int(result["total_score"])
    return result


# ═════════════════════════════════════════════════════════════════════
#  VALIDATION FUNCTIONS
# ═════════════════════════════════════════════════════════════════════

def validate_name(name: str) -> tuple:
    """Letters, hyphens, apostrophes, spaces only. Uses for loop."""
    if not name or not name.strip():
        return False, "Name cannot be empty."
    stripped: str = name.strip()
    for char in stripped:                          # for loop
        if char not in ALLOWED_NAME_CHARS:
            return False, f"Invalid character '{char}'."
    has_letter: bool = any(c.isalpha() for c in stripped)
    if not has_letter:
        return False, "Must contain at least one letter."
    return True, ""


def validate_dob(dob_str: str) -> tuple:
    """DD/MM/YYYY or similar. Uses while loop."""
    if not dob_str or not dob_str.strip():
        return False, "Date of birth cannot be empty."
    attempt: int  = 0
    parsed        = None
    formats: list = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
    while attempt < len(formats):                  # while loop
        try:
            parsed = datetime.strptime(dob_str.strip(), formats[attempt]).date()
            break
        except ValueError:
            attempt += 1
    if parsed is None:
        return False, "Use DD/MM/YYYY — e.g. 15/03/2001."
    today: date = date.today()
    if parsed > today:
        return False, "Date cannot be in the future."
    age: int = today.year - parsed.year - ((today.month, today.day) < (parsed.month, parsed.day))
    if age < 10:  return False, "Age below 10 — check date."
    if age > 120: return False, "Unrealistic age — check date."
    return True, ""


def validate_student_id(sid: str) -> tuple:
    """Digits only, min 4. Uses for loop."""
    if not sid or not sid.strip():
        return False, "Student ID cannot be empty."
    sid_s: str = sid.strip()
    for ch in sid_s:                               # for loop
        if not ch.isdigit():
            return False, f"Digits only. Found: '{ch}'"
    if len(sid_s) < 4:
        return False, "At least 4 digits required."
    return True, ""


def calculate_state(score: int, bands: list) -> dict:
    """Match total score to the appropriate state band."""
    result: dict = {}
    for band in bands:
        if band["min"] <= score <= band["max"]:
            result = {"label": band["label"], "description": band["description"]}
            break
    if not result:
        result = {"label": "Out of range", "description": "Unexpected score."}
    return result


# ═════════════════════════════════════════════════════════════════════
#  WIDGET HELPERS
# ═════════════════════════════════════════════════════════════════════

def lbl(parent, text, size=11, weight="normal", color=None, **kw):
    return tk.Label(parent, text=text, font=("Segoe UI", size, weight),
                    bg=parent["bg"], fg=color or C["ink"], **kw)


def btn(parent, text, cmd, style="primary", **kw):
    colours: dict = {
        "primary": (C["accent"], "#fff"),
        "success": (C["success"], "#fff"),
        "ghost":   (C["surface"], C["ink"]),
        "danger":  (C["danger"], "#fff"),
    }
    bg, fg = colours.get(style, colours["primary"])
    return tk.Button(parent, text=text, command=cmd,
                     font=("Segoe UI", 11, "bold"),
                     bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                     relief="flat", bd=0, cursor="hand2",
                     padx=14, pady=7, **kw)


def inp(parent, var=None, width=34, **kw):
    return tk.Entry(parent, textvariable=var, width=width,
                    font=("Segoe UI", 11), relief="solid", bd=1,
                    bg=C["surface"], fg=C["ink"], insertbackground=C["ink"],
                    highlightthickness=1, highlightbackground=C["border"],
                    highlightcolor=C["accent"], **kw)


def card(parent, **kw):
    return tk.Frame(parent, bg=C["surface"], relief="flat", bd=0,
                    highlightthickness=1, highlightbackground=C["border"], **kw)


def blank(parent):
    return tk.Label(parent, text="", bg=parent["bg"], font=("Segoe UI", 3))


# ═════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION CLASS
# ═════════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Feedback Application & Skill Tracking Survey — WIUT")
        self.configure(bg=C["bg"])
        self.geometry("840x660")
        self.minsize(720, 540)

        self.survey_data: dict  = load_questions(QUESTIONS_FILE)
        self.questions: list    = self.survey_data["questions"]
        self.scoring: list      = self.survey_data["scoring"]
        self.result_data: dict  = {}
        self.version: float     = 1.0               # float

        # Per-question IntVar (one per question, -1 = unanswered)
        self.answer_vars: list  = [tk.IntVar(value=-1) for _ in self.questions]

        # User detail StringVars
        self.var_surname:     tk.StringVar = tk.StringVar()
        self.var_given_name:  tk.StringVar = tk.StringVar()
        self.var_dob:         tk.StringVar = tk.StringVar()
        self.var_student_id:  tk.StringVar = tk.StringVar()
        self.var_fmt:         tk.StringVar = tk.StringVar(value="json")

        # range used to iterate over page classes
        container = tk.Frame(self, bg=C["bg"])
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames: dict = {}
        page_classes: tuple = (PageHome, PageDetails, PageSurvey, PageResult, PageLoad)
        for i in range(len(page_classes)):              # range used here
            F = page_classes[i]
            f = F(container, self)
            self.frames[F] = f
            f.grid(row=0, column=0, sticky="nsew")

        self.show(PageHome)

    def show(self, cls):
        f = self.frames[cls]
        if hasattr(f, "on_show"):
            f.on_show()
        f.tkraise()


# ─────────────────────────────────────────────────────────────────────
# PAGE: Home
# ─────────────────────────────────────────────────────────────────────

class PageHome(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=C["bg"])
        a = app
        bar = tk.Frame(self, bg=C["surface"], height=56)
        bar.pack(fill="x"); bar.pack_propagate(False)
        lbl(bar, "FeedbackSurvey", 14, "bold", C["accent"]).pack(side="left", padx=18, pady=14)
        lbl(bar, "· WIUT 4BUIS008C", 11, color=C["ink2"]).pack(side="left", pady=18)

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=44, pady=28)
        lbl(body, a.survey_data["survey_title"], 13, "bold", wraplength=640).pack(anchor="w")
        lbl(body, a.survey_data["survey_description"], 10, color=C["ink2"],
            wraplength=640, justify="left").pack(anchor="w", pady=(5, 18))

        row = tk.Frame(body, bg=C["bg"])
        row.pack(fill="x")
        row.columnconfigure(0, weight=1); row.columnconfigure(1, weight=1)

        c1 = card(row); c1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(c1, text="📋", font=("Segoe UI", 26), bg=C["surface"]).pack(anchor="w", padx=16, pady=(14,2))
        lbl(c1, "Start new survey", 13, "bold").pack(anchor="w", padx=16)
        lbl(c1, "Answer 20 questions about\nyour feedback habits.", 10, color=C["ink2"]).pack(anchor="w", padx=16, pady=(4,10))
        btn(c1, "Begin survey →", lambda: a.show(PageDetails)).pack(anchor="w", padx=16, pady=(0,16))

        c2 = card(row); c2.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(c2, text="📂", font=("Segoe UI", 26), bg=C["surface"]).pack(anchor="w", padx=16, pady=(14,2))
        lbl(c2, "Load saved result", 13, "bold").pack(anchor="w", padx=16)
        lbl(c2, "View a previously saved\nquestionnaire result.", 10, color=C["ink2"]).pack(anchor="w", padx=16, pady=(4,10))
        btn(c2, "Load result →", lambda: a.show(PageLoad), "ghost").pack(anchor="w", padx=16, pady=(0,16))

        strip = card(body); strip.pack(fill="x", pady=(16, 0))
        stats: list = [("Questions","20"), ("Options/Q","5"), ("Score bands","7"), ("Save formats","JSON · CSV · TXT")]
        for i, (k, v) in enumerate(stats):
            col = tk.Frame(strip, bg=C["surface"])
            col.grid(row=0, column=i, padx=20, pady=12, sticky="w")
            lbl(col, k, 9, color=C["ink3"]).pack(anchor="w")
            lbl(col, v, 13, "bold").pack(anchor="w")


# ─────────────────────────────────────────────────────────────────────
# PAGE: Details
# ─────────────────────────────────────────────────────────────────────

class PageDetails(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=C["bg"])
        self.app = app; self._build()

    def _build(self):
        a = self.app
        bar = tk.Frame(self, bg=C["surface"], height=56)
        bar.pack(fill="x"); bar.pack_propagate(False)
        btn(bar, "← Back", lambda: a.show(PageHome), "ghost").pack(side="left", padx=10, pady=10)
        lbl(bar, "Your details", 13, "bold").pack(side="left", padx=8, pady=18)

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=44, pady=20)
        lbl(body, "Enter your details", 15, "bold").pack(anchor="w")
        lbl(body, "All fields required and validated.", 10, color=C["ink2"]).pack(anchor="w", pady=(3, 14))

        c = card(body); c.pack(fill="x")
        inner = tk.Frame(c, bg=C["surface"]); inner.pack(fill="x", padx=20, pady=18)

        self.errs: dict = {}
        fields: list = [
            ("Surname *",                     a.var_surname,    "surname"),
            ("Given name *",                  a.var_given_name, "given_name"),
            ("Date of birth * (DD/MM/YYYY)",  a.var_dob,        "dob"),
            ("Student ID *",                  a.var_student_id, "student_id"),
        ]
        for label_text, var, key in fields:
            r = tk.Frame(inner, bg=C["surface"]); r.pack(fill="x", pady=5)
            lbl(r, label_text, 10, "bold").pack(anchor="w")
            inp(r, var).pack(anchor="w", pady=(2, 0))
            e = lbl(r, "", 9, color=C["danger"]); e.pack(anchor="w")
            self.errs[key] = e

        br = tk.Frame(inner, bg=C["surface"]); br.pack(anchor="w", pady=(10, 0))
        btn(br, "Verify & continue →", self._validate).pack(side="left")
        btn(br, "Clear", self._clear, "ghost").pack(side="left", padx=(10, 0))

    def _clear(self):
        a = self.app
        for v in (a.var_surname, a.var_given_name, a.var_dob, a.var_student_id):
            v.set("")
        for e in self.errs.values():
            e.config(text="")

    def _validate(self):
        a = self.app
        checks: list = [
            ("surname",    a.var_surname.get(),    validate_name),
            ("given_name", a.var_given_name.get(), validate_name),
            ("dob",        a.var_dob.get(),        validate_dob),
            ("student_id", a.var_student_id.get(), validate_student_id),
        ]
        all_ok: bool = True
        for key, val, fn in checks:
            ok, msg = fn(val)
            self.errs[key].config(text=msg if not ok else "")
            if not ok: all_ok = False
        if all_ok:
            for v in a.answer_vars: v.set(-1)
            a.show(PageSurvey)


# ─────────────────────────────────────────────────────────────────────
# PAGE: Survey
# ─────────────────────────────────────────────────────────────────────

class PageSurvey(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=C["bg"])
        self.app = app; self._build()

    def _build(self):
        a = self.app
        bar = tk.Frame(self, bg=C["surface"], height=56)
        bar.pack(fill="x"); bar.pack_propagate(False)
        btn(bar, "← Back", lambda: a.show(PageDetails), "ghost").pack(side="left", padx=10, pady=10)
        self.prog_lbl = lbl(bar, "0 / 20", 11, color=C["ink2"])
        self.prog_lbl.pack(side="right", padx=18, pady=18)

        pb_bg = tk.Frame(self, bg=C["border"], height=4); pb_bg.pack(fill="x")
        self.pbar = tk.Frame(pb_bg, bg=C["accent"], height=4)
        self.pbar.place(x=0, y=0, relheight=1, relwidth=0)

        canvas = tk.Canvas(self, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=C["bg"])
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        pad = tk.Frame(sf, bg=C["bg"]); pad.pack(fill="both", expand=True, padx=36, pady=16)
        lbl(pad, a.survey_data["survey_title"], 12, "bold", wraplength=700).pack(anchor="w")
        lbl(pad, "Answer all 20 questions, then click Submit.", 10, color=C["ink2"]).pack(anchor="w", pady=(3, 12))

        total: int = len(a.questions)
        for idx in range(total):
            q = a.questions[idx]; var = a.answer_vars[idx]
            qc = card(pad); qc.pack(fill="x", pady=4)
            inner = tk.Frame(qc, bg=C["surface"]); inner.pack(fill="x", padx=14, pady=10)
            lbl(inner, f"QUESTION {q['id']} OF {total}", 8, color=C["ink3"]).pack(anchor="w")
            lbl(inner, q["text"], 11, "bold", wraplength=680, justify="left").pack(anchor="w", pady=(3,7))
            for opt in q["options"]:
                tk.Radiobutton(inner, text=opt["label"], variable=var, value=opt["score"],
                               font=("Segoe UI", 10), bg=C["surface"], fg=C["ink"],
                               activebackground=C["acc_lt"], selectcolor=C["acc_lt"],
                               relief="flat", cursor="hand2",
                               command=self._upd).pack(anchor="w", padx=6, pady=2)

        bf = tk.Frame(pad, bg=C["bg"]); bf.pack(fill="x", pady=14)
        btn(bf, "Submit survey →", self._submit, "success").pack(anchor="w")

    def _upd(self):
        a = self.app
        n: int = sum(1 for v in a.answer_vars if v.get() != -1)
        self.prog_lbl.config(text=f"{n} / {len(a.questions)}")
        self.pbar.place(relwidth=n / len(a.questions))

    def _submit(self):
        a = self.app
        unanswered: list = [i+1 for i, v in enumerate(a.answer_vars) if v.get() == -1]
        if unanswered:
            qs = ", ".join(str(n) for n in unanswered[:5])
            extra = f" +{len(unanswered)-5} more" if len(unanswered) > 5 else ""
            messagebox.showwarning("Unanswered", f"Answer all questions first.\n\nMissing: Q{qs}{extra}")
            return

        total_score: int   = 0
        answers: list      = []
        answered_ids: set  = set()          # set

        for idx, q in enumerate(a.questions):
            sc: int = a.answer_vars[idx].get()
            total_score += sc
            answered_ids.add(q["id"])
            lbl_str: str = next((o["label"] for o in q["options"] if o["score"] == sc), "")
            answers.append({"question_id": q["id"], "question_text": q["text"],
                             "selected_option": lbl_str, "score": sc})

        pct: float  = round(len(answered_ids) / len(a.questions) * 100, 1)
        mx: int     = sum(max(o["score"] for o in q["options"]) for q in a.questions)
        state: dict = calculate_state(total_score, a.scoring)

        a.result_data = {
            "surname":      a.var_surname.get().strip(),
            "given_name":   a.var_given_name.get().strip(),
            "dob":          a.var_dob.get().strip(),
            "student_id":   a.var_student_id.get().strip(),
            "total_score":  total_score,
            "max_score":    mx,
            "pct_answered": pct,
            "state_label":  state["label"],
            "state_desc":   state["description"],
            "timestamp":    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "answers":      answers,
            "survey_title": a.survey_data["survey_title"],
            "version":      a.version,
        }
        a.show(PageResult)

    def on_show(self): self._upd()


# ─────────────────────────────────────────────────────────────────────
# PAGE: Result
# ─────────────────────────────────────────────────────────────────────

class PageResult(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=C["bg"])
        self.app = app

    def on_show(self):
        for w in self.winfo_children(): w.destroy()
        self._build()

    def _build(self):
        a = self.app; rd = a.result_data
        bar = tk.Frame(self, bg=C["surface"], height=56)
        bar.pack(fill="x"); bar.pack_propagate(False)
        btn(bar, "← Home", lambda: a.show(PageHome), "ghost").pack(side="left", padx=10, pady=10)
        lbl(bar, "Your result", 13, "bold").pack(side="left", padx=8, pady=18)

        canvas = tk.Canvas(self, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=C["bg"])
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.pack(side="left", fill="both", expand=True); sb.pack(side="right", fill="y")

        body = tk.Frame(sf, bg=C["bg"]); body.pack(fill="both", expand=True, padx=36, pady=16)

        hero = tk.Frame(body, bg=C["accent"]); hero.pack(fill="x", pady=(0,12))
        hi = tk.Frame(hero, bg=C["accent"]); hi.pack(fill="x", padx=20, pady=18)
        tk.Label(hi, text=f"{rd['total_score']}  /  {rd['max_score']}", font=("Segoe UI", 32, "bold"),
                 bg=C["accent"], fg="white").pack(anchor="w")
        tk.Label(hi, text=rd["state_label"], font=("Segoe UI", 14, "bold"),
                 bg=C["accent"], fg="white").pack(anchor="w", pady=(4,0))
        tk.Label(hi, text=rd["state_desc"], font=("Segoe UI", 10),
                 bg=C["accent"], fg="#BFDBFE", wraplength=640, justify="left").pack(anchor="w", pady=(5,0))

        # Details card
        dc = card(body); dc.pack(fill="x", pady=5)
        di = tk.Frame(dc, bg=C["surface"]); di.pack(fill="x", padx=18, pady=14)
        lbl(di, "Respondent details", 12, "bold").pack(anchor="w", pady=(0,8))
        for k, v in [("Full name", f"{rd['given_name']} {rd['surname']}"),
                     ("Student ID", rd["student_id"]), ("DOB", rd["dob"]),
                     ("Completed", rd["timestamp"]), ("% Answered", f"{rd['pct_answered']}%")]:
            r = tk.Frame(di, bg=C["surface"]); r.pack(fill="x", pady=1)
            lbl(r, k, 9, color=C["ink3"]).pack(side="left", padx=(0,10))
            lbl(r, v, 10, "bold").pack(side="left")

        # Save card
        sc_card = card(body); sc_card.pack(fill="x", pady=5)
        si = tk.Frame(sc_card, bg=C["surface"]); si.pack(fill="x", padx=18, pady=14)
        lbl(si, "Save your result", 12, "bold").pack(anchor="w")
        lbl(si, "Choose a format and save to the data/ folder.", 10, color=C["ink2"]).pack(anchor="w", pady=(2,8))
        fr = tk.Frame(si, bg=C["surface"]); fr.pack(anchor="w")
        lbl(fr, "Format:", 10).pack(side="left")
        ttk.Combobox(fr, textvariable=a.var_fmt, values=list(ALLOWED_FILE_FORMATS), width=7, state="readonly").pack(side="left", padx=8)
        btn(fr, "Save", self._save).pack(side="left", padx=4)

        # Answers card
        ac = card(body); ac.pack(fill="x", pady=5)
        ai = tk.Frame(ac, bg=C["surface"]); ai.pack(fill="x", padx=18, pady=14)
        lbl(ai, "Answer breakdown", 12, "bold").pack(anchor="w", pady=(0,8))
        for ans in rd.get("answers", []):
            r = tk.Frame(ai, bg=C["bg"]); r.pack(fill="x", pady=1)
            tk.Label(r, text=f"Q{ans['question_id']}", width=3, font=("Segoe UI",9),
                     bg=C["bg"], fg=C["ink3"], anchor="w").grid(row=0, column=0, sticky="w", padx=(2,6))
            tk.Label(r, text=ans["selected_option"], font=("Segoe UI",9),
                     bg=C["bg"], fg=C["ink"], anchor="w").grid(row=0, column=1, sticky="w")
            tk.Label(r, text=str(ans["score"]), font=("Segoe UI",9,"bold"),
                     bg=C["acc_lt"], fg=C["accent"], width=2, anchor="center").grid(row=0, column=2, padx=4)

        btn(body, "Take survey again",
            lambda: [self._reset(), a.show(PageDetails)], "ghost").pack(anchor="w", pady=(10,4))

    def _save(self):
        a = self.app
        try:
            fname = save_result(a.result_data, a.var_fmt.get())
            messagebox.showinfo("Saved", f"Result saved:\n  data/{fname}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _reset(self):
        a = self.app
        for v in a.answer_vars: v.set(-1)
        for v in (a.var_surname, a.var_given_name, a.var_dob, a.var_student_id): v.set("")


# ─────────────────────────────────────────────────────────────────────
# PAGE: Load
# ─────────────────────────────────────────────────────────────────────

class PageLoad(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=C["bg"])
        self.app = app; self._build()

    def _build(self):
        a = self.app
        bar = tk.Frame(self, bg=C["surface"], height=56)
        bar.pack(fill="x"); bar.pack_propagate(False)
        btn(bar, "← Back", lambda: a.show(PageHome), "ghost").pack(side="left", padx=10, pady=10)
        lbl(bar, "Load saved result", 13, "bold").pack(side="left", padx=8, pady=18)

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=44, pady=20)
        lbl(body, "Load a previously saved result", 15, "bold").pack(anchor="w")
        lbl(body, "Select a file from the list or browse for one.", 10, color=C["ink2"]).pack(anchor="w", pady=(3,14))

        c = card(body); c.pack(fill="x")
        inner = tk.Frame(c, bg=C["surface"]); inner.pack(fill="x", padx=18, pady=16)
        lbl(inner, "Saved files:", 10, "bold").pack(anchor="w")
        self.lb = tk.Listbox(inner, font=("Segoe UI",10), height=7,
                             bg=C["bg"], fg=C["ink"],
                             selectbackground=C["accent"], selectforeground="white",
                             relief="solid", bd=1, highlightthickness=0)
        self.lb.pack(fill="x", pady=(4,10))
        self._refresh()

        br = tk.Frame(inner, bg=C["surface"]); br.pack(anchor="w")
        btn(br, "Load selected", self._load_sel).pack(side="left")
        btn(br, "Browse…", self._browse, "ghost").pack(side="left", padx=(8,0))
        btn(br, "Refresh", self._refresh, "ghost").pack(side="left", padx=(8,0))

        self.ra = tk.Frame(body, bg=C["bg"]); self.ra.pack(fill="both", expand=True, pady=(14,0))

    def on_show(self): self._refresh()

    def _refresh(self):
        self.lb.delete(0, tk.END)
        files: list = get_saved_files()
        for f in files: self.lb.insert(tk.END, f)
        if not files: self.lb.insert(tk.END, "(no saved results)")

    def _load_sel(self):
        sel = self.lb.curselection()
        if not sel: messagebox.showwarning("No selection", "Please select a file."); return
        fn: str = self.lb.get(sel[0])
        if fn.startswith("("): return
        self._display(fn)

    def _browse(self):
        path: str = filedialog.askopenfilename(
            title="Open result file",
            filetypes=[("All","*.json *.csv *.txt"),("JSON","*.json"),("CSV","*.csv"),("Text","*.txt")],
            initialdir=RESULTS_DIR if os.path.exists(RESULTS_DIR) else "."
        )
        if path:
            fn = os.path.basename(path)
            if not os.path.exists(os.path.join(RESULTS_DIR, fn)):
                import shutil; os.makedirs(RESULTS_DIR, exist_ok=True)
                shutil.copy(path, os.path.join(RESULTS_DIR, fn))
            self._display(fn)

    def _display(self, fn: str):
        result: dict | None = load_result_file(fn)
        if not result: messagebox.showerror("Error", f"Could not load: {fn}"); return
        for w in self.ra.winfo_children(): w.destroy()
        c = card(self.ra)
        tk.Frame(c, bg=C["accent"], height=4).pack(fill="x")
        c.pack(fill="x")
        inner = tk.Frame(c, bg=C["surface"]); inner.pack(fill="x", padx=16, pady=14)
        lbl(inner, f"File: {fn}", 9, color=C["ink3"]).pack(anchor="w")
        lbl(inner, f"Score: {result.get('total_score','—')}", 18, "bold", C["accent"]).pack(anchor="w", pady=(4,2))
        lbl(inner, result.get("state_label",""), 12, "bold").pack(anchor="w")
        lbl(inner, result.get("state_desc",""), 9, color=C["ink2"], wraplength=560, justify="left").pack(anchor="w", pady=(4,8))
        for k, v in [("Name", f"{result.get('given_name','')} {result.get('surname','')}".strip()),
                     ("Student ID", result.get("student_id","—")),
                     ("DOB", result.get("dob","—")),
                     ("Recorded", result.get("timestamp","—"))]:
            r = tk.Frame(inner, bg=C["surface"]); r.pack(fill="x", pady=1)
            lbl(r, f"{k}:", 9, color=C["ink3"]).pack(side="left", padx=(0,8))
            lbl(r, v, 9, "bold").pack(side="left")


# ═════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    os.makedirs(RESULTS_DIR, exist_ok=True)
    App().mainloop()
