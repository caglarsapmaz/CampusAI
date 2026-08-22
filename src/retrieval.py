import re
from collections import defaultdict

import requests

from src.database import get_chunks


FOUNDRY_URL = "http://127.0.0.1:64853"
MODEL_NAME = "phi-4-mini"


# =========================================================
# NORMALİZASYON
# =========================================================

def normalize_text(text):
    text = str(text or "").replace("İ", "i").lower()

    replacements = {
        "ı": "i",
        "ğ": "g",
        "ü": "u",
        "ş": "s",
        "ö": "o",
        "ç": "c",
        "â": "a",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9\s./:-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def norm_phrase(text):
    return clean(normalize_text(text))


# =========================================================
# BELGELER
# =========================================================

FIELD_RE = re.compile(r"([^:|]+):\s*([^|]*)")


def get_full_documents():
    documents = defaultdict(list)

    for row in get_chunks():
        if len(row) < 3 or not row[2]:
            continue

        pdf_name, chunk_no, content = row[:3]
        documents[pdf_name].append((chunk_no, str(content)))

    result = {}

    for pdf_name, chunks in documents.items():
        chunks.sort(
            key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0
        )

        result[pdf_name] = "\n".join(
            content for _, content in chunks
        )

    return result


# =========================================================
# TABLO KAYITLARI
# =========================================================

def _table_records():
    records = []

    for pdf_name, text in get_full_documents().items():

        for raw_line in text.splitlines():
            line = clean(raw_line)

            if "Program:" not in line or "Ders Adı:" not in line:
                continue

            fields = {
                clean(k): clean(v)
                for k, v in FIELD_RE.findall(line)
            }

            course = fields.get("Ders Adı", "")

            if not course:
                continue

            fields["pdf_name"] = pdf_name
            records.append(fields)

    return records


# =========================================================
# KELİME EŞLEŞMESİ
# =========================================================

STOP_WORDS = {
    "hangi",
    "hangisi",
    "ders",
    "dersi",
    "dersin",
    "dersinin",
    "sinav",
    "sinavi",
    "sinavlari",
    "ne",
    "zaman",
    "tarih",
    "tarihi",
    "saat",
    "saati",
    "kim",
    "kimdir",
    "hocasi",
    "ogretim",
    "uyesi",
    "nedir",
    "nerede",
    "derslik",
    "derslikte",
    "sinif",
    "sinifta",
    "salon",
    "salonda",
    "program",
    "programi",
    "programinda",
    "programindaki",
    "programdaki",
    "icin",
    "ve",
    "ile",
    "goster",
    "gosterir",
    "gosterebilir",
    "bana",
    "bunu",
    "bu",
    "bir",
    "var",
}


def words(text):
    return [
        w
        for w in re.findall(r"[a-z0-9]+", normalize_text(text))
        if len(w) >= 3 and w not in STOP_WORDS
    ]


def exact_or_fuzzy_match(value, query):
    a = norm_phrase(value)
    b = norm_phrase(query)

    if not a or not b:
        return False

    if a == b or a in b or b in a:
        return True

    aw = set(words(a))
    bw = set(words(b))

    return bool(bw) and bw.issubset(aw)


# =========================================================
# SORU TÜRÜ
# =========================================================

def question_kind(question):
    q = normalize_text(question)

    # Ders listesi
    if any(
        phrase in q
        for phrase in (
            "dersleri ve ogretim uyelerini",
            "dersler ve ogretim uyeleri",
            "dersleri ogretim uyeleri",
            "derslerini ve ogretim",
            "dersleri ve hocalari",
            "dersler ve hocalar",
            "hangi dersler",
            "dersleri goster",
            "derslerini goster",
        )
    ):
        return "courses"

    # Öğretim üyesi
    if any(
        phrase in q
        for phrase in (
            "ogretim uyesi",
            "ogretim uyesinin",
            "ogretim uyeleri",
            "hoca",
            "hocasi",
            "kimdir",
        )
    ):
        return "teacher"

    # Derslik
    if any(
        phrase in q
        for phrase in (
            "derslik",
            "sinif",
            "sinifta",
            "salon",
            "nerede",
        )
    ):
        return "room"

    # Sınav tarihi
    if any(
        phrase in q
        for phrase in (
            "ne zaman",
            "hangi tarih",
            "tarihi",
            "saat",
            "saati",
        )
    ):
        return "date"

    return None


# =========================================================
# PROGRAM TESPİTİ
# =========================================================

def detect_program(question, records):
    q = norm_phrase(question)

    programs = []
    seen = set()

    for record in records:
        program = clean(record.get("Program", ""))

        if not program:
            continue

        key = norm_phrase(program)

        if key in seen:
            continue

        seen.add(key)
        programs.append(program)

    candidates = []

    for program in programs:
        p = norm_phrase(program)

        if not p:
            continue

        # Direkt eşleşme
        if p in q:
            candidates.append(program)
            continue

        # Ek almış program isimleri
        p_words = p.split()

        if p_words and all(
            re.search(
                rf"\b{re.escape(word)}"
                rf"(?:da|de|ta|te|inda|inde|daki|deki|taki|teki)?\b",
                q,
            )
            for word in p_words
        ):
            candidates.append(program)

    if not candidates:
        return None

    return max(
        candidates,
        key=lambda x: len(norm_phrase(x))
    )


# =========================================================
# DERS TESPİTİ
# =========================================================

def detect_course(question, records):
    q = norm_phrase(question)

    courses = []
    seen = set()

    for record in records:
        course = clean(record.get("Ders Adı", ""))

        if not course:
            continue

        key = norm_phrase(course)

        if key in seen:
            continue

        seen.add(key)
        courses.append(course)

    # Tam ders adı
    exact = [
        course
        for course in courses
        if norm_phrase(course) in q
    ]

    if exact:
        return max(
            exact,
            key=lambda x: len(norm_phrase(x))
        )

    # Kelime bazlı eşleşme
    q_words = set(words(q))
    scored = []

    for course in courses:
        c_words = set(words(course))

        if not c_words:
            continue

        overlap = len(q_words & c_words)
        ratio = overlap / len(c_words)

        if overlap >= 1 and ratio >= 0.60:
            scored.append(
                (
                    ratio,
                    overlap,
                    len(c_words),
                    course,
                )
            )

    if scored:
        scored.sort(reverse=True)
        return scored[0][3]

    return None


# =========================================================
# SINAV TÜRÜ
# =========================================================

def detect_exam_type(question):
    q = normalize_text(question)

    if any(
        x in q
        for x in (
            "tek ders",
            "tekders",
        )
    ):
        return "tek_ders"

    if any(
        x in q
        for x in (
            "bütünleme",
            "butunleme",
            "büt",
            "but",
        )
    ):
        return "but"

    if any(
        x in q
        for x in (
            "final",
            "finaller",
        )
    ):
        return "final"

    if any(
        x in q
        for x in (
            "vize",
            "vizeler",
            "ara sinav",
        )
    ):
        return "vize"

    return None


def normalize_exam_type(value):
    q = normalize_text(value)

    if "tek ders" in q or "tekders" in q:
        return "tek_ders"

    if "butunleme" in q or q == "but":
        return "but"

    if "final" in q:
        return "final"

    if "vize" in q or "ara sinav" in q:
        return "vize"

    return q


def record_exam_type(record):
    return normalize_exam_type(
        record.get("Sınav Şekli", "")
    )


def exam_label(exam_type):
    return {
        "vize": "Vize",
        "final": "Final",
        "but": "Bütünleme",
        "tek_ders": "Tek Ders",
    }.get(
        exam_type,
        "Sınav",
    )


# =========================================================
# KAYIT EŞLEŞTİRME
# =========================================================

def matching_records(question):
    records = _table_records()

    if not records:
        return [], None, None

    course = detect_course(
        question,
        records,
    )

    program = detect_program(
        question,
        records,
    )

    matches = records

    if course:
        matches = [
            record
            for record in matches
            if exact_or_fuzzy_match(
                record.get("Ders Adı", ""),
                course,
            )
        ]

    if program:
        matches = [
            record
            for record in matches
            if exact_or_fuzzy_match(
                record.get("Program", ""),
                program,
            )
        ]

    exam_type = detect_exam_type(question)

    if exam_type:
        matches = [
            record
            for record in matches
            if record_exam_type(record) == exam_type
        ]

    return matches, course, program


# =========================================================
# YARDIMCI
# =========================================================

def _unique_values(records, field):
    values = []
    seen = set()

    for record in records:
        value = clean(
            record.get(field, "")
        )

        if not value:
            continue

        key = norm_phrase(value)

        if key in seen:
            continue

        seen.add(key)
        values.append(value)

    return values


def _unique_pairs(records, field):
    result = []
    seen = set()

    for record in records:
        value = clean(
            record.get(field, "")
        )

        program = clean(
            record.get("Program", "")
        )

        if not value:
            continue

        key = (
            norm_phrase(program),
            norm_phrase(value),
        )

        if key in seen:
            continue

        seen.add(key)

        result.append(
            (
                program,
                value,
            )
        )

    return result


# =========================================================
# DOĞRUDAN TABLO CEVABI
# =========================================================

def direct_table_answer(question):
    records = _table_records()

    if not records:
        return None

    kind = question_kind(question)
    exam_type = detect_exam_type(question)

    # -----------------------------------------------------
    # PROGRAM DERSLERİ
    # -----------------------------------------------------

    if kind == "courses":

        program = detect_program(
            question,
            records,
        )

        if not program:
            return None

        program_records = [
            record
            for record in records
            if exact_or_fuzzy_match(
                record.get("Program", ""),
                program,
            )
        ]

        if not program_records:
            return None

        seen = set()

        lines = [
            f"📚 {program} programındaki dersler:"
        ]

        for record in program_records:

            course = clean(
                record.get("Ders Adı", "")
            )

            teacher = clean(
                record.get("Öğretim Üyesi", "")
            )

            if not course:
                continue

            key = (
                norm_phrase(course),
                norm_phrase(teacher),
            )

            if key in seen:
                continue

            seen.add(key)

            if teacher:
                lines.append(
                    f"• {course} — {teacher}"
                )
            else:
                lines.append(
                    f"• {course}"
                )

        if len(lines) == 1:
            return None

        return "\n".join(lines)

    # -----------------------------------------------------
    # DERS TESPİTİ
    # -----------------------------------------------------

    course = detect_course(
        question,
        records,
    )

    if not course:
        return None

    matches = [
        record
        for record in records
        if exact_or_fuzzy_match(
            record.get("Ders Adı", ""),
            course,
        )
    ]

    program = detect_program(
        question,
        records,
    )

    if program:
        matches = [
            record
            for record in matches
            if exact_or_fuzzy_match(
                record.get("Program", ""),
                program,
            )
        ]

    if exam_type:
        matches = [
            record
            for record in matches
            if record_exam_type(record) == exam_type
        ]

    if not matches:
        return None

    # -----------------------------------------------------
    # ÖĞRETİM ÜYESİ
    # -----------------------------------------------------

    if kind == "teacher":

        pairs = _unique_pairs(
            matches,
            "Öğretim Üyesi",
        )

        if not pairs:
            return None

        # Program belirtilmişse doğrudan cevap
        if program:

            teachers = _unique_values(
                matches,
                "Öğretim Üyesi",
            )

            if len(teachers) == 1:
                return (
                    f"📚 {course}\n"
                    f"👤 Öğretim Üyesi: {teachers[0]}"
                )

            return (
                f"📚 {course}\n"
                "Bu programda birden fazla öğretim üyesi kaydı bulundu:\n"
                + "\n".join(
                    f"• {teacher}"
                    for teacher in teachers
                )
            )

        # Program belirtilmemişse programları ayır
        grouped = defaultdict(list)

        for prog, teacher in pairs:
            grouped[prog].append(teacher)

        if len(grouped) == 1:

            teachers = _unique_values(
                matches,
                "Öğretim Üyesi",
            )

            if len(teachers) == 1:
                return (
                    f"📚 {course}\n"
                    f"👤 Öğretim Üyesi: {teachers[0]}"
                )

        lines = [
            f"📚 {course} dersi birden fazla programda bulunuyor:"
        ]

        for prog, teachers in grouped.items():

            unique_teachers = list(
                dict.fromkeys(teachers)
            )

            for teacher in unique_teachers:
                lines.append(
                    f"• {prog}: {teacher}"
                )

        lines.append(
            "\nDoğru kaydı belirlemek için program adını belirtin."
        )

        return "\n".join(lines)

    # -----------------------------------------------------
    # DERSLİK
    # -----------------------------------------------------

    if kind == "room":

        pairs = _unique_pairs(
            matches,
            "Derslik",
        )

        if not pairs:
            return None

        if program:

            rooms = _unique_values(
                matches,
                "Derslik",
            )

            if len(rooms) == 1:
                return (
                    f"📚 {course}\n"
                    f"📍 Derslik: {rooms[0]}"
                )

            return (
                f"📚 {course}\n"
                "Birden fazla derslik kaydı bulundu:\n"
                + "\n".join(
                    f"• {room}"
                    for room in rooms
                )
            )

        lines = [
            f"📚 {course} dersi için derslik kayıtları:"
        ]

        for prog, room in pairs:
            lines.append(
                f"• {prog}: {room}"
            )

        if len(pairs) > 1:
            lines.append(
                "\nDoğru kaydı belirlemek için program adını belirtin."
            )

        return "\n".join(lines)

    # -----------------------------------------------------
    # SINAV TARİHİ
    # -----------------------------------------------------

    if kind == "date":

        values = []
        seen = set()

        for record in matches:

            date = clean(
                record.get("Sınav Tarihi", "")
            )

            time = clean(
                record.get("Sınav Saati", "")
            )

            prog = clean(
                record.get("Program", "")
            )

            exam = record_exam_type(
                record
            )

            if not date and not time:
                continue

            value = " ".join(
                x
                for x in (
                    date,
                    time,
                )
                if x
            )

            key = (
                norm_phrase(prog),
                norm_phrase(value),
                exam,
            )

            if key in seen:
                continue

            seen.add(key)

            values.append(
                (
                    prog,
                    value,
                    exam,
                )
            )

        if not values:
            return None

        # Aynı kayıtların tekrarlarını azalt
        unique_values = list(
            dict.fromkeys(
                (
                    prog,
                    value,
                    exam,
                )
                for prog, value, exam in values
            )
        )

        # Program belli
        if program:

            lines = [
                f"📚 {course}"
            ]

            for _, value, exam in unique_values:

                label = exam_label(
                    exam_type or exam
                )

                lines.append(
                    f"📅 {label}: {value}"
                )

            return "\n".join(lines)

        # Tek sonuç
        if len(unique_values) == 1:

            _, value, exam = unique_values[0]

            label = exam_label(
                exam_type or exam
            )

            return (
                f"📚 {course}\n"
                f"📅 {label}: {value}"
            )

        # Birden fazla program
        lines = [
            f"📚 {course} için birden fazla sınav kaydı bulundu:"
        ]

        for prog, value, exam in unique_values:

            label = exam_label(
                exam
            )

            lines.append(
                f"• {prog}: {label} — {value}"
            )

        lines.append(
            "\nDoğru kaydı belirlemek için program adını belirtin."
        )

        return "\n".join(lines)

    return None


# =========================================================
# AKADEMİK TAKVİM
# =========================================================

NOT_FOUND_MESSAGE = "Bu bilgi yüklenen belgelerde bulunamadı."


def _is_course_specific_query(question, records=None):
    """
    Ders adı açıkça tespit edilen sınav/öğretim üyesi/derslik
    sorgularını genel akademik takvim ve serbest RAG'dan ayırır.

    Örn. "Tıbbi Mikrobiyoloji finali ne zaman?" sorusunda
    ders tablosunda Final kaydı yoksa akademik takvimdeki
    genel Final haftası cevap olarak kullanılmaz.
    """
    if records is None:
        records = _table_records()

    if not records:
        return False

    course = detect_course(question, records)
    if not course:
        return False

    kind = question_kind(question)
    exam_type = detect_exam_type(question)

    return bool(
        exam_type
        or kind in {"date", "teacher", "room"}
    )


def _has_explicit_course_or_program(question, records=None):
    """Sorgunun belirli bir ders veya programa yönelik olup olmadığını belirtir."""
    if records is None:
        records = _table_records()

    if not records:
        return False

    return bool(
        detect_course(question, records)
        or detect_program(question, records)
    )

DATE_RE = re.compile(
    r"\b(?:"
    r"\d{1,2}\s+[A-Za-zÇĞİÖŞÜçğıöşü]+\s*[–—-]\s*"
    r"\d{1,2}\s+[A-Za-zÇĞİÖŞÜçğıöşü]+\s+\d{4}"
    r"|"
    r"\d{1,2}\s*[–—-]\s*\d{1,2}\s+"
    r"[A-Za-zÇĞİÖŞÜçğıöşü]+\s+\d{4}"
    r"|"
    r"\d{1,2}\s+[A-Za-zÇĞİÖŞÜçğıöşü]+\s+\d{4}"
    r")\b"
)


def detect_semester(question):
    q = normalize_text(question)

    if "bahar" in q:
        return "bahar"

    if "guz" in q:
        return "guz"

    return None


def _calendar_answer(question):
    q = normalize_text(question)

    # Ders adı açıkça geçiyorsa akademik takvimdeki genel
    # sınav haftalarını dersin sınav tarihi olarak kullanma.
    records = _table_records()
    if detect_course(question, records):
        return None

    if not any(x in q for x in (
        "ne zaman",
        "tarihi",
        "hangi tarih",
    )):
        return None

    semester = detect_semester(question)

    wants_start = any(
        x in q
        for x in (
            "dersler ne zaman",
            "dersleri ne zaman",
            "derslerin baslamasi",
            "derslerin baslangici",
            "dersleri basliyor",
            "donem ne zaman basliyor",
            "yariyil ne zaman basliyor",
        )
    )

    exam_type = detect_exam_type(question)

    if wants_start:
        labels = (
            "yariyili derslerinin baslamasi",
            "yariyili derslerin baslamasi",
            "derslerin baslamasi",
        )
    elif exam_type == "vize":
        labels = ("ara sinav haftasi", "ara sinavlar")
    elif exam_type == "final":
        labels = ("yariyil sonu sinav", "final haftasi", "sinav final")
    elif exam_type == "but":
        labels = ("butunleme sinavlari", "butunleme sinavi", "but sinavlari")
    elif exam_type == "tek_ders":
        labels = ("tek ders sinavi", "tek ders sinavlari")
    else:
        return None

    # Kayıtlar: (semester | None, date)
    results = []

    for text in get_full_documents().values():
        lines = [clean(x) for x in text.splitlines() if clean(x)]

        for i, line in enumerate(lines):
            nline = normalize_text(line)

            if not any(label in nline for label in labels):
                continue

            context_lines = lines[max(0, i - 12): i + 1]
            context = " ".join(normalize_text(x) for x in context_lines)

            # Dönem bilgisi yalnızca belgede açıkça bulunuyorsa kullanılır.
            source_semester = None
            if "bahar" in context:
                source_semester = "bahar"
            elif "guz" in context:
                source_semester = "guz"

            if semester and source_semester and source_semester != semester:
                continue

            if semester and not source_semester:
                # Kullanıcı dönem istedi ama kaynakta dönem bağlamı yoksa
                # tahmin yapma. Bu kayıt güvenle eşleştirilemez.
                continue

            for candidate in lines[i:i + 5]:
                match = DATE_RE.search(candidate)
                if not match:
                    continue

                date = clean(match.group(0))
                results.append({
                    "semester": source_semester,
                    "date": date,
                })
                break

    # Backend seviyesinde normalize + duplicate temizliği.
    unique = []
    seen = set()
    for item in results:
        key = (
            item["semester"],
            normalize_text(item["date"]),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    if not unique:
        return None

    # Kullanıcı dönem belirtmediyse ve kaynakta dönem açıkça varsa
    # dönemleri anlamlı biçimde grupla. Kaynakta dönem yoksa sadece tarihi göster.
    grouped = defaultdict(list)
    for item in unique:
        grouped[item["semester"]].append(item["date"])

    lines = []
    for group in ("guz", "bahar", None):
        dates = grouped.get(group, [])
        if not dates:
            continue

        if group == "guz":
            lines.append("🍂 Güz Yarıyılı")
        elif group == "bahar":
            lines.append("🌸 Bahar Yarıyılı")

        for date in dates:
            lines.append(f"📅 {date}")

        lines.append("")

    return "\n".join(lines).strip() if lines else None


# =========================================================
# NORMAL RAG
# =========================================================

def search_chunks(query, limit=12):

    rows = get_chunks()

    q = normalize_text(query)
    q_words = set(words(q))

    # Tablo kayıtlarını bir kere al
    records = _table_records()

    results = []

    for row in rows:

        if len(row) < 3 or not row[2]:
            continue

        pdf_name, chunk_no, content = row[:3]

        content = str(content)

        normalized_content = normalize_text(
            content
        )

        content_words = set(
            re.findall(
                r"[a-z0-9]+",
                normalized_content,
            )
        )

        score = len(
            q_words & content_words
        ) * 4

        # Sınav türleri
        if any(
            x in q
            for x in (
                "vize",
                "ara sinav",
            )
        ):
            if (
                "vize" in normalized_content
                or "ara sinav" in normalized_content
            ):
                score += 12

        if "final" in q:
            if "final" in normalized_content:
                score += 12

        if any(
            x in q
            for x in (
                "but",
                "butunleme",
            )
        ):
            if (
                "but" in normalized_content
                or "butunleme" in normalized_content
            ):
                score += 12

        if "tek ders" in q:
            if "tek ders" in normalized_content:
                score += 12

        if "derslik" in q:
            if "derslik" in normalized_content:
                score += 10

        # Program / ders güçlendirmesi
        for record in records:

            program = norm_phrase(
                record.get(
                    "Program",
                    "",
                )
            )

            course = norm_phrase(
                record.get(
                    "Ders Adı",
                    "",
                )
            )

            if (
                program
                and program in q
                and program in normalized_content
            ):
                score += 10

            if (
                course
                and course in q
                and course in normalized_content
            ):
                score += 14

        if score > 0:
            results.append(
                (
                    score,
                    pdf_name,
                    chunk_no,
                    content,
                )
            )

    results.sort(
        key=lambda x: (
            -x[0],
            str(x[1]),
            x[2],
        )
    )

    # Aynı bilgi farklı PDF/chunk kayıtlarından geliyorsa retrieval
    # katmanında tekilleştir. Chunk ID veya PDF adı farklı olsa bile
    # aynı metin / aynı tarih bilgisi ikinci kez dönmesin.
    unique = []
    seen = set()

    for item in results:
        score, pdf_name, chunk_no, content = item
        date_matches = tuple(
            normalize_text(x)
            for x in DATE_RE.findall(str(content))
        ) if 'DATE_RE' in globals() else ()

        if date_matches:
            key = (
                'dates',
                date_matches,
            )
        else:
            key = (
                'content',
                normalize_text(content),
            )

        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

        if len(unique) >= limit:
            break

    return unique


# =========================================================
# FOUNDRY / AI
# =========================================================

def generate_answer(question, context):

    system_prompt = """
Sen CampusAI adlı üniversite asistanısın.

Görevin yalnızca sana verilen belge içeriğine dayanarak
kullanıcının sorusunu cevaplamaktır.

KURALLAR:

1. Yalnızca verilen belgelerdeki bilgileri kullan.
2. Belgede bulunmayan hiçbir bilgiyi tahmin etme veya uydurma.
3. Tarihleri değiştirme veya tahmin etme.
4. Kullanıcının sorusuna doğrudan cevap ver.
5. Türkçe cevap ver.
6. Gereksiz açıklama yapma.
7. Birden fazla sonuç varsa ayrı satırlarda göster.
8. Aynı ders farklı programlarda bulunuyorsa programları ayır.
9. Kullanıcı program belirtmişse yalnızca o programa ait bilgiyi kullan.
10. Program belirtilmemişse ve aynı ders birden fazla programda bulunuyorsa programları ayrı göster.
11. Sınav türlerini kesinlikle karıştırma.
12. Vizeyi final olarak gösterme.
13. Finali bütünleme olarak gösterme.
14. Bütünlemeyi final olarak gösterme.
15. Tek ders sınavını final veya bütünleme olarak gösterme.
16. Güz ve bahar dönemlerini birbirine karıştırma.
17. Belgede olmayan öğretim üyesi, tarih, derslik veya program bilgisi üretme.
18. Cevabı mümkün olduğunca kısa tut.

Öğretim üyesi sorularında:

Ders:
Program:
Öğretim Üyesi:

Birden fazla program varsa:

Ders:
• Program: Öğretim Üyesi
• Program: Öğretim Üyesi

Programın dersleri soruluyorsa:

Program:
• Ders — Öğretim Üyesi
• Ders — Öğretim Üyesi

Eğer verilen belgelerde cevap yoksa:

Bu bilgi yüklenen belgelerde bulunamadı.
"""

    response = requests.post(
        f"{FOUNDRY_URL}/v1/chat/completions",

        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },

        json={
            "model": MODEL_NAME,

            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": (
                        f"BELGE:\n{context}\n\n"
                        f"SORU:\n{question}"
                    ),
                },
            ],

            "temperature": 0.0,
            "max_tokens": 350,
            "stream": False,
        },

        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return clean(
        data["choices"][0]["message"]["content"]
    )


# =========================================================
# ANA CEVAP
# =========================================================

def answer_question(question):

    if not question or not question.strip():
        return "Lütfen bir soru yazın."

    question = clean(question)
    records = _table_records()

    # -----------------------------------------------------
    # 1. Kesin tablo cevabı
    # -----------------------------------------------------
    answer = direct_table_answer(question)

    if answer:
        return answer

    # -----------------------------------------------------
    # 2. Ders bazlı yapılandırılmış sorgu güvenlik kilidi
    # -----------------------------------------------------
    # "Tıbbi Mikrobiyoloji finali ne zaman?" gibi bir sorguda
    # ders tablosunda Final kaydı yoksa genel akademik takvimdeki
    # "Final haftası" bilgisinin cevaba sızması engellenir.
    if _is_course_specific_query(question, records):
        return NOT_FOUND_MESSAGE

    # -----------------------------------------------------
    # 3. Akademik takvim
    # -----------------------------------------------------
    answer = _calendar_answer(question)

    if answer:
        return answer

    # -----------------------------------------------------
    # 4. RAG
    # -----------------------------------------------------
    results = search_chunks(
        question,
        limit=8,
    )

    if not results:
        return NOT_FOUND_MESSAGE

    context = "\n\n---\n\n".join(
        f"[Belge: {pdf_name}]\n{content}"
        for _, pdf_name, _, content in results
    )

    # -----------------------------------------------------
    # 5. AI
    # -----------------------------------------------------
    try:
        return generate_answer(
            question,
            context,
        )

    except requests.RequestException:
        return (
            "CampusAI modeliyle iletişim kurulamadı. "
            "Foundry sunucusunun çalıştığından emin olun."
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        return (
            "CampusAI yanıtı işlenirken "
            "bir hata oluştu."
        )
