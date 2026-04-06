"""
Assignment Feedback Application and Skill Development Tracking Survey
======================================================================
Module  : Fundamentals of Programming, 4BUIS008C  (Level 4)
Project : Coursework 1  —  Web Version (Streamlit)

Run with:   streamlit run streamlit_app.py
Deploy to:  share.streamlit.io  (push to GitHub first)

Variable types used: int, str, float, list, tuple, range, bool, dict, set, frozenset
"""

import streamlit as st
import json
import os
import re
import csv
import io
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

# ─────────────────────────────────────────────────────────────────────
# Page config  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Feedback Survey — WIUT",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────
# Custom CSS — matching the clean academic style of the literature review
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.hero    { background:#1D4ED8; color:white; border-radius:12px; padding:1.75rem 2rem 1.5rem; margin-bottom:1.2rem; }
.hero-sc { font-size:3rem; font-weight:700; line-height:1; letter-spacing:-2px; }
.hero-lb { font-size:1.15rem; font-weight:600; margin-top:.4rem; }
.hero-ds { font-size:.88rem; opacity:.82; margin-top:.5rem; line-height:1.6; }
.icard   { background:white; border:1px solid #E5E2DC; border-radius:10px; padding:1.1rem 1.4rem; margin-bottom:.9rem; }
.qcard   { background:white; border:1px solid #E5E2DC; border-radius:10px; padding:1rem 1.3rem .7rem; margin-bottom:.55rem; }
.qnum    { font-size:.7rem; color:#9A9690; font-weight:600; letter-spacing:.5px; text-transform:uppercase; }
.qtxt    { font-size:.95rem; font-weight:600; color:#1A1814; margin-top:3px; line-height:1.5; }
.ferr    { color:#991B1B; font-size:.82rem; margin-top:2px; }
.ar      { display:flex; align-items:center; gap:10px; padding:5px 8px; border-radius:6px; margin-bottom:3px; font-size:.85rem; }
.ar:nth-child(odd) { background:#F7F5F0; }
.aqn     { width:26px; color:#9A9690; font-weight:600; flex-shrink:0; }
.atx     { flex:1; color:#1A1814; }
.asc     { background:#EFF4FF; color:#1D4ED8; border-radius:5px; padding:1px 7px; font-weight:700; font-size:.82rem; }
.br      { display:flex; gap:12px; padding:7px 0; border-bottom:1px solid #E5E2DC; font-size:.88rem; }
.br:last-child { border:none; }
.brn     { min-width:60px; color:#5A5650; font-weight:500; }
.brl     { flex:1; color:#1A1814; }
.br.cur  { font-weight:700; color:#1D4ED8; }
div[data-testid="metric-container"] { background:white; border:1px solid #E5E2DC; border-radius:10px; padding:10px 14px; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
#  FILE / DATA FUNCTIONS
# ═════════════════════════════════════════════════════════════════════

@st.cache_data
def load_questions(fp: str) -> dict:
    """Load survey questions from external JSON file (cached between reruns)."""
    with open(fp, "r", encoding="utf-8") as f:
        data: dict = json.load(f)
    return data


def get_saved_files() -> list:
    """Return a sorted list of saved result filenames."""
    files: list = []
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    for fn in os.listdir(RESULTS_DIR):
        if fn.endswith((".json", ".csv", ".txt")):
            files.append(fn)
    files.sort(reverse=True)
    return files


def save_result(rd: dict, fmt: str) -> tuple:
    """
    Save survey result to disk in the chosen format.
    Returns (filename: str, bytes_content: bytes) so the browser
    download button can also offer the file directly.
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    safe: str = re.sub(r"[^a-zA-Z0-9_]", "_", rd["surname"])
    ts: str   = datetime.now().strftime("%Y%m%d_%H%M%S")
    base: str = f"{safe}_{ts}"

    if fmt == "json":
        fname: str    = base + ".json"
        content: bytes = json.dumps(rd, indent=4, ensure_ascii=False).encode("utf-8")

    elif fmt == "csv":
        fname = base + ".csv"
        fields: list = ["surname","given_name","dob","student_id",
                         "total_score","state_label","state_desc","timestamp","answers"]
        row: dict = {k: rd.get(k, "") for k in fields}
        row["answers"] = json.dumps(rd.get("answers", []))
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=fields)
        w.writeheader(); w.writerow(row)
        content = buf.getvalue().encode("utf-8")

    else:  # txt
        fname = base + ".txt"
        lines: list = [
            "=" * 52,
            "  FEEDBACK APPLICATION & SKILL TRACKING SURVEY",
            "  RESULT RECORD",
            "=" * 52, "",
            f"Surname:     {rd.get('surname','')}",
            f"Given Name:  {rd.get('given_name','')}",
            f"DOB:         {rd.get('dob','')}",
            f"Student ID:  {rd.get('student_id','')}",
            f"Timestamp:   {rd.get('timestamp','')}",
            "",
            f"Total Score: {rd.get('total_score',0)}",
            f"State:       {rd.get('state_label','')}",
            f"Description: {rd.get('state_desc','')}", "",
            "Answers:",
        ]
        for a in rd.get("answers", []):
            lines.append(f"  Q{a['question_id']}: {a['selected_option']} (score: {a['score']})")
        content = "\n".join(lines).encode("utf-8")

    with open(os.path.join(RESULTS_DIR, fname), "wb") as f:
        f.write(content)
    return fname, content


def load_result_file(fn: str) -> dict | None:
    """Load a previously saved result back from disk."""
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
    """
    Name must contain only letters, hyphens, apostrophes, and spaces.
    Uses a for loop to check each character individually.
    Returns (is_valid: bool, error_message: str).
    """
    if not name or not name.strip():
        return False, "Name cannot be empty."
    stripped: str = name.strip()
    for char in stripped:                          # for loop — checks every character
        if char not in ALLOWED_NAME_CHARS:
            return False, f"Invalid character '{char}'. Use letters, hyphens, apostrophes, spaces only."
    has_letter: bool = any(c.isalpha() for c in stripped)
    if not has_letter:
        return False, "Name must contain at least one letter."
    return True, ""


def validate_dob(dob_str: str) -> tuple:
    """
    Date of birth must be in DD/MM/YYYY (or similar) format and be realistic.
    Uses a while loop to try multiple format strings before failing.
    Returns (is_valid: bool, error_message: str).
    """
    if not dob_str or not dob_str.strip():
        return False, "Date of birth cannot be empty."
    attempt: int  = 0
    parsed        = None
    formats: list = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
    while attempt < len(formats):                  # while loop — tries each format
        try:
            parsed = datetime.strptime(dob_str.strip(), formats[attempt]).date()
            break
        except ValueError:
            attempt += 1
    if parsed is None:
        return False, "Invalid date. Use DD/MM/YYYY — e.g. 15/03/2001."
    today: date = date.today()
    if parsed > today:
        return False, "Date of birth cannot be in the future."
    age: int = today.year - parsed.year - (
        (today.month, today.day) < (parsed.month, parsed.day)
    )
    if age < 10: return False, "Age below 10 — please check the date."
    if age > 120: return False, "Unrealistic age — please check the date."
    return True, ""


def validate_student_id(sid: str) -> tuple:
    """
    Student ID must contain digits only, minimum 4 characters.
    Uses a for loop to check each character individually.
    Returns (is_valid: bool, error_message: str).
    """
    if not sid or not sid.strip():
        return False, "Student ID cannot be empty."
    sid_s: str = sid.strip()
    for ch in sid_s:                               # for loop — checks every digit
        if not ch.isdigit():
            return False, f"Student ID must be digits only. Found: '{ch}'"
    if len(sid_s) < 4:
        return False, "Student ID must be at least 4 digits."
    return True, ""


def calculate_state(score: int, bands: list) -> dict:
    """Match total score to the appropriate psychological state band."""
    result: dict = {}
    for band in bands:
        if band["min"] <= score <= band["max"]:
            result = {"label": band["label"], "description": band["description"]}
            break
    if not result:
        result = {"label": "Score out of range", "description": "Unexpected score — please retake."}
    return result


# ═════════════════════════════════════════════════════════════════════
#  SESSION STATE INITIALISATION
# ═════════════════════════════════════════════════════════════════════

def _init_state():
    defaults: dict = {
        "page":          "home",   # home | details | survey | result | load
        "surname":       "",
        "given_name":    "",
        "dob":           "",
        "student_id":    "",
        "answers":       {},       # {question_id: score}
        "result_data":   {},
        "errors":        {},
        "loaded_result": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


def go(page: str):
    """Navigate to a named page and force a rerun."""
    st.session_state["page"] = page
    st.rerun()


# ═════════════════════════════════════════════════════════════════════
#  LOAD SURVEY DATA  (done once, cached)
# ═════════════════════════════════════════════════════════════════════

survey:    dict = load_questions(QUESTIONS_FILE)
questions: list = survey["questions"]
scoring:   list = survey["scoring"]
total_q:   int  = len(questions)
max_score: int  = sum(max(o["score"] for o in q["options"]) for q in questions)


# ═════════════════════════════════════════════════════════════════════
#  PAGE: Home
# ═════════════════════════════════════════════════════════════════════

def page_home():
    st.markdown('<span style="background:#EFF4FF;color:#1D4ED8;border-radius:999px;padding:3px 12px;font-size:.75rem;font-weight:600;">WIUT · 4BUIS008C · Coursework 1</span>', unsafe_allow_html=True)
    st.markdown(f"# {survey['survey_title']}")
    st.markdown(f"<p style='color:#5A5650;font-size:.97rem;margin-bottom:1.5rem;'>{survey['survey_description']}</p>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="icard"><div style="font-size:1.8rem;margin-bottom:.4rem;">📋</div><div style="font-weight:700;font-size:1.05rem;margin-bottom:.3rem;">Start new survey</div><div style="font-size:.88rem;color:#5A5650;margin-bottom:.8rem;">Answer 20 questions about your feedback habits. Takes about 5 minutes.</div></div>', unsafe_allow_html=True)
        if st.button("Begin survey →", type="primary", use_container_width=True):
            go("details")
    with c2:
        st.markdown('<div class="icard"><div style="font-size:1.8rem;margin-bottom:.4rem;">📂</div><div style="font-weight:700;font-size:1.05rem;margin-bottom:.3rem;">Load saved result</div><div style="font-size:.88rem;color:#5A5650;margin-bottom:.8rem;">View a previously saved questionnaire result stored on this system.</div></div>', unsafe_allow_html=True)
        if st.button("Load result →", use_container_width=True):
            go("load")

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Questions",   "20")
    m2.metric("Options / Q", "5")
    m3.metric("Score bands", "7")
    m4.metric("Formats",     "JSON · CSV · TXT")


# ═════════════════════════════════════════════════════════════════════
#  PAGE: User Details
# ═════════════════════════════════════════════════════════════════════

def page_details():
    if st.button("← Back"):
        go("home")
    st.markdown("## Enter your details")
    st.caption("All fields are required and validated before the survey begins.")

    errs: dict = st.session_state.get("errors", {})
    c1, c2 = st.columns(2)
    with c1:
        surname = st.text_input("Surname *", value=st.session_state["surname"],
                                placeholder="e.g. Smith-Jones",
                                help="Letters, hyphens, apostrophes, spaces only")
        if errs.get("surname"):
            st.markdown(f'<div class="ferr">⚠ {errs["surname"]}</div>', unsafe_allow_html=True)
        dob = st.text_input("Date of birth * (DD/MM/YYYY)", value=st.session_state["dob"],
                             placeholder="15/03/2001")
        if errs.get("dob"):
            st.markdown(f'<div class="ferr">⚠ {errs["dob"]}</div>', unsafe_allow_html=True)
    with c2:
        given_name = st.text_input("Given name *", value=st.session_state["given_name"],
                                   placeholder="e.g. Mary Ann")
        if errs.get("given_name"):
            st.markdown(f'<div class="ferr">⚠ {errs["given_name"]}</div>', unsafe_allow_html=True)
        student_id = st.text_input("Student ID *", value=st.session_state["student_id"],
                                   placeholder="00012345", help="Digits only")
        if errs.get("student_id"):
            st.markdown(f'<div class="ferr">⚠ {errs["student_id"]}</div>', unsafe_allow_html=True)

    st.markdown("")
    if st.button("Verify & continue →", type="primary"):
        new_errs: dict = {}
        checks: list = [
            ("surname",    surname,    validate_name),
            ("given_name", given_name, validate_name),
            ("dob",        dob,        validate_dob),
            ("student_id", student_id, validate_student_id),
        ]
        all_ok: bool = True
        for key, val, fn in checks:
            ok, msg = fn(val)
            if not ok:
                new_errs[key] = msg
                all_ok = False
        st.session_state["errors"] = new_errs
        if all_ok:
            st.session_state.update({
                "surname": surname.strip(), "given_name": given_name.strip(),
                "dob": dob.strip(), "student_id": student_id.strip(),
                "answers": {}, "errors": {},
            })
            go("survey")
        else:
            st.rerun()


# ═════════════════════════════════════════════════════════════════════
#  PAGE: Survey Questions
# ═════════════════════════════════════════════════════════════════════

def page_survey():
    ans: dict   = st.session_state.get("answers", {})
    done: int   = len(ans)
    pct: float  = round(done / total_q * 100, 1)

    cb, cp = st.columns([1, 3])
    with cb:
        if st.button("← Back"):
            go("details")
    with cp:
        st.progress(done / total_q, text=f"{done} / {total_q} answered  ({pct}%)")

    st.markdown(f"## {survey['survey_title']}")
    st.caption("Answer all 20 questions honestly, then click Submit at the bottom.")
    st.divider()

    for q in questions:
        qid: int   = q["id"]
        opts: list = q["options"]
        labels: list = [o["label"] for o in opts]

        prev_sc = ans.get(qid)
        prev_idx = None
        if prev_sc is not None:
            for i, o in enumerate(opts):
                if o["score"] == prev_sc:
                    prev_idx = i
                    break

        st.markdown(f'<div class="qcard"><div class="qnum">Question {qid} of {total_q}</div><div class="qtxt">{q["text"]}</div></div>', unsafe_allow_html=True)
        choice = st.radio(
            label=f"q{qid}",
            options=range(len(labels)),
            format_func=lambda i, lb=labels: lb[i],
            index=prev_idx,
            key=f"radio_{qid}",
            label_visibility="collapsed",
        )
        if choice is not None:
            st.session_state["answers"][qid] = opts[choice]["score"]
        st.markdown("")

    st.divider()
    unanswered: list = [q["id"] for q in questions if q["id"] not in st.session_state["answers"]]
    if unanswered:
        st.warning(f"Please answer all questions before submitting. Remaining: {len(unanswered)}")

    if st.button("Submit survey →", type="primary", disabled=bool(unanswered)):
        total_score: int   = 0
        final_ans: list    = []
        answered_ids: set  = set()      # set — tracks which questions were answered

        for q in questions:
            qid        = q["id"]
            sc: int    = st.session_state["answers"].get(qid, 0)
            total_score += sc
            answered_ids.add(qid)
            lbl_str: str = next((o["label"] for o in q["options"] if o["score"] == sc), "")
            final_ans.append({"question_id": qid, "question_text": q["text"],
                               "selected_option": lbl_str, "score": sc})

        pct_ans: float = round(len(answered_ids) / total_q * 100, 1)
        state: dict    = calculate_state(total_score, scoring)
        version: float = 1.0                                # float variable

        st.session_state["result_data"] = {
            "surname":      st.session_state["surname"],
            "given_name":   st.session_state["given_name"],
            "dob":          st.session_state["dob"],
            "student_id":   st.session_state["student_id"],
            "total_score":  total_score,
            "max_score":    max_score,
            "pct_answered": pct_ans,
            "state_label":  state["label"],
            "state_desc":   state["description"],
            "timestamp":    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "answers":      final_ans,
            "survey_title": survey["survey_title"],
            "version":      version,
        }
        go("result")


# ═════════════════════════════════════════════════════════════════════
#  PAGE: Result
# ═════════════════════════════════════════════════════════════════════

def page_result():
    rd: dict = st.session_state.get("result_data", {})
    if not rd:
        st.error("No result found. Please complete the survey first.")
        if st.button("← Home"):
            go("home")
        return

    if st.button("← Home"):
        go("home")

    sc: int        = rd["total_score"]
    mx: int        = rd["max_score"]
    pct_bar: float = round(sc / mx * 100, 1)

    st.markdown(f"""
    <div class="hero">
      <div style="font-size:.72rem;opacity:.7;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.2rem;">Total score</div>
      <div class="hero-sc">{sc} <span style="font-size:1.4rem;opacity:.55;">/ {mx}</span></div>
      <div class="hero-lb">{rd['state_label']}</div>
      <div class="hero-ds">{rd['state_desc']}</div>
      <div style="background:rgba(255,255,255,.22);border-radius:999px;height:7px;margin-top:1.1rem;overflow:hidden;">
        <div style="height:100%;background:white;border-radius:999px;width:{pct_bar}%;"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Score",       f"{sc} / {mx}")
    m2.metric("% Answered",  f"{rd['pct_answered']}%")
    m3.metric("Name",        f"{rd['given_name']} {rd['surname']}")
    m4.metric("Student ID",  rd["student_id"])

    st.divider()
    st.markdown("### Save your result")
    cf, cb2, cdl = st.columns([2, 1, 2])
    with cf:
        fmt: str = st.selectbox("Format", list(ALLOWED_FILE_FORMATS),
                                 format_func=str.upper, label_visibility="collapsed")
    with cb2:
        do_save: bool = st.button("Save", type="primary")
    if do_save:
        fname, content = save_result(rd, fmt)
        mime_map: dict = {"json": "application/json", "csv": "text/csv", "txt": "text/plain"}
        with cdl:
            st.download_button(f"⬇ Download {fname}", data=content, file_name=fname,
                               mime=mime_map.get(fmt, "text/plain"))
        st.success(f"Saved to data/{fname}")

    st.divider()
    with st.expander("📋 Your answers", expanded=True):
        rows: str = ""
        for a in rd.get("answers", []):
            rows += f'<div class="ar"><span class="aqn">Q{a["question_id"]}</span><span class="atx">{a["selected_option"]}</span><span class="asc">{a["score"]}</span></div>'
        st.markdown(rows, unsafe_allow_html=True)

    with st.expander("📊 Scoring bands reference"):
        bh: str = ""
        for band in scoring:
            cur: bool = band["min"] <= sc <= band["max"]
            cls: str  = "br cur" if cur else "br"
            arr: str  = "  ← your result" if cur else ""
            bh += f'<div class="{cls}"><span class="brn">{band["min"]}–{band["max"]}</span><span class="brl">{band["label"]}{arr}</span></div>'
        st.markdown(bh, unsafe_allow_html=True)

    st.markdown("")
    if st.button("Take survey again"):
        st.session_state.update({"answers": {}, "result_data": {}})
        go("details")


# ═════════════════════════════════════════════════════════════════════
#  PAGE: Load Saved Result
# ═════════════════════════════════════════════════════════════════════

def page_load():
    if st.button("← Back"):
        go("home")
    st.markdown("## Load a saved result")
    st.caption("Select a previously saved file or upload one from your device.")

    saved: list = get_saved_files()
    tab1, tab2 = st.tabs(["Select from saved files", "Upload a file"])

    with tab1:
        if not saved:
            st.info("No saved results found. Complete a survey to create one.")
        else:
            chosen: str = st.selectbox("Choose file", saved)
            if st.button("Load selected", type="primary"):
                r = load_result_file(chosen)
                if r:
                    st.session_state["loaded_result"] = r
                    st.rerun()
                else:
                    st.error(f"Could not load: {chosen}")

    with tab2:
        uploaded = st.file_uploader("Upload result file", type=["json", "csv", "txt"])
        if uploaded:
            raw: bytes = uploaded.read()
            os.makedirs(RESULTS_DIR, exist_ok=True)
            dest: str = os.path.join(RESULTS_DIR, uploaded.name)
            with open(dest, "wb") as f:
                f.write(raw)
            r = load_result_file(uploaded.name)
            if r:
                st.session_state["loaded_result"] = r
                st.rerun()
            else:
                st.error("Could not parse the uploaded file.")

    lr: dict = st.session_state.get("loaded_result", {})
    if lr:
        st.divider()
        sv: int = lr.get("total_score", 0)
        st.markdown(f"""
        <div class="hero">
          <div style="font-size:.72rem;opacity:.7;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.2rem;">Loaded result</div>
          <div class="hero-sc">{sv}</div>
          <div class="hero-lb">{lr.get('state_label','')}</div>
          <div class="hero-ds">{lr.get('state_desc', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(f"**Name:** {lr.get('given_name','')} {lr.get('surname','')}".strip())
        c1.markdown(f"**DOB:** {lr.get('dob','—')}")
        c2.markdown(f"**Student ID:** {lr.get('student_id','—')}")
        c2.markdown(f"**Recorded:** {lr.get('timestamp','—')}")
        if lr.get("answers"):
            with st.expander("📋 Recorded answers"):
                rows: str = ""
                for a in lr["answers"]:
                    rows += f'<div class="ar"><span class="aqn">Q{a.get("question_id","")}</span><span class="atx">{a.get("selected_option","")}</span><span class="asc">{a.get("score","")}</span></div>'
                st.markdown(rows, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
#  ROUTER
# ═════════════════════════════════════════════════════════════════════
_p: str = st.session_state["page"]
if   _p == "home":    page_home()
elif _p == "details": page_details()
elif _p == "survey":  page_survey()
elif _p == "result":  page_result()
elif _p == "load":    page_load()
else:
    st.error(f"Unknown page: {_p}")
    go("home")
