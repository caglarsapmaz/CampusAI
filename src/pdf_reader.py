import re
import fitz


COURSE_CODE_RE = re.compile(
    r"^[A-ZÇĞİÖŞÜ]{2,}\d{2,4}(?:[.\-]\d+)?$",
    re.IGNORECASE,
)


# =========================================================
# NORMALİZASYON
# =========================================================

def _norm(value):

    value = str(
        value or ""
    )

    value = value.replace(
        "İ",
        "i"
    ).lower()

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

        value = value.replace(
            old,
            new
        )

    return value


# =========================================================
# SATIRLARI Y KOORDİNATINA GÖRE GRUPLA
# =========================================================

def _group_words_by_y(
    words,
    tolerance=2.5,
):

    rows = []

    for word in sorted(
        words,
        key=lambda w: (
            w[1],
            w[0],
        ),
    ):

        y = word[1]

        target = None

        for row in rows:

            if abs(
                row["y"] - y
            ) <= tolerance:

                target = row
                break

        if target is None:

            target = {
                "y": y,
                "words": [],
            }

            rows.append(
                target
            )

        target["words"].append(
            word
        )

    for row in rows:

        row["words"].sort(
            key=lambda w: w[0]
        )

        row["text"] = " ".join(
            w[4]
            for w in row["words"]
        ).strip()

    return sorted(
        rows,
        key=lambda r: r["y"]
    )


# =========================================================
# TABLO BAŞLIĞINI BUL
# =========================================================

def _find_header_row(
    rows
):

    for row in rows:

        text = _norm(
            row["text"]
        )

        if (
            "program" in text
            and "ders kodu" in text
            and "ders adi" in text
        ):

            return row

    return None


# =========================================================
# SÜTUN BAŞLANGIÇLARI
# =========================================================

def _column_starts(
    header_row
):

    starts = {

        "program": 50,

        "course_code": 190,

        "course": 240,

        "teacher": 385,

        "exam_type": 550,

        "date": 600,

        "time": 655,

        "room": 710,
    }

    if not header_row:

        return starts

    ders = [
        w
        for w in header_row["words"]
        if _norm(w[4]) == "ders"
    ]

    sinav = [
        w
        for w in header_row["words"]
        if _norm(w[4]) == "sinav"
    ]

    for word in header_row["words"]:

        token = _norm(
            word[4]
        )

        if token == "program":

            starts["program"] = word[0]

        elif token == "dersten":

            starts["teacher"] = word[0]

        elif token == "derslik":

            starts["room"] = word[0]

    if len(ders) >= 2:

        starts["course_code"] = (
            ders[0][0]
        )

        starts["course"] = (
            ders[1][0]
        )

    if len(sinav) >= 3:

        starts["exam_type"] = (
            sinav[0][0]
        )

        starts["date"] = (
            sinav[1][0]
        )

        starts["time"] = (
            sinav[2][0]
        )

    return starts


# =========================================================
# X KOORDİNATINDAN SÜTUN BUL
# =========================================================

def _column_for_x(
    x,
    starts,
):

    ordered = [

        (
            starts["program"],
            "program",
        ),

        (
            starts["course_code"],
            "course_code",
        ),

        (
            starts["course"],
            "course",
        ),

        (
            starts["teacher"],
            "teacher",
        ),

        (
            starts["exam_type"],
            "exam_type",
        ),

        (
            starts["date"],
            "date",
        ),

        (
            starts["time"],
            "time",
        ),

        (
            starts["room"],
            "room",
        ),
    ]

    ordered.sort()

    result = ordered[0][1]

    for start, name in ordered:

        if x >= start:

            result = name

        else:

            break

    return result


# =========================================================
# BİRLEŞTİRİLMİŞ DERSLİK HÜCRELERİNİ BUL
# =========================================================

def _room_groups(
    page,
    header_y,
    room_x,
):

    label_rows = _group_words_by_y(
        [
            w
            for w in page.get_text(
                "words"
            )
            if (
                w[0] >= room_x - 10
                and w[1] > header_y
            )
        ],
        tolerance=3.0,
    )

    labels = [
        (
            row["y"],
            row["text"],
        )
        for row in label_rows
        if row["text"]
    ]

    segments = []

    for drawing in page.get_drawings():

        rect = drawing.get(
            "rect"
        )

        if not rect:
            continue

        # Dış çerçeveyi değil,
        # derslik sütunundaki iç dikey çizgileri al.
        if (
            room_x - 10
            <= rect.x0
            <= room_x + 10
            and rect.height > 40
            and rect.y0 > header_y
        ):

            segments.append(
                (
                    rect.y0,
                    rect.y1,
                )
            )

    segments.sort()

    result = []

    for y0, y1 in segments:

        matching = [
            (
                y,
                text,
            )
            for y, text in labels
            if y0 <= y <= y1
        ]

        if matching:

            text = min(
                matching,
                key=lambda item:
                abs(
                    item[0]
                    - (
                        y0 + y1
                    ) / 2
                ),
            )[1]

            result.append(
                (
                    y0,
                    y1,
                    text,
                )
            )

    return result


# =========================================================
# TABLO PARSER
# =========================================================

def _extract_table_page(
    page
):

    words = page.get_text(
        "words"
    )

    rows = _group_words_by_y(
        words
    )

    header = _find_header_row(
        rows
    )

    if not header:

        return None

    starts = _column_starts(
        header
    )

    room_groups = _room_groups(
        page,
        header["y"],
        starts["room"],
    )

    structured = []

    for row in rows:

        if (
            row["y"]
            <= header["y"] + 3
        ):
            continue

        code = next(
            (
                w[4]
                for w in row["words"]
                if COURSE_CODE_RE.match(
                    w[4]
                )
            ),
            None,
        )

        if not code:

            continue

        columns = {

            "program": [],

            "course_code": [],

            "course": [],

            "teacher": [],

            "exam_type": [],

            "date": [],

            "time": [],
        }

        for word in row["words"]:

            x0 = word[0]

            text = word[4]

            column = _column_for_x(
                x0,
                starts,
            )

            if column in columns:

                columns[
                    column
                ].append(
                    text
                )

        values = {

            key: " ".join(
                value
            ).strip()

            for key, value
            in columns.items()
        }

        if (
            not values["course_code"]
            or not values["course"]
        ):

            continue

        room = ""

        for (
            y0,
            y1,
            room_name,
        ) in room_groups:

            if (
                y0
                <= row["y"]
                <= y1
            ):

                room = room_name
                break

        if (
            not room
            and room_groups
        ):

            room = min(
                room_groups,
                key=lambda g:
                abs(
                    (
                        g[0]
                        + g[1]
                    ) / 2
                    - row["y"]
                ),
            )[2]

        structured.append(

            "Program: {program} | "
            "Ders Kodu: {course_code} | "
            "Ders Adı: {course} | "
            "Öğretim Üyesi: {teacher} | "
            "Sınav Şekli: {exam_type} | "
            "Sınav Tarihi: {date} | "
            "Sınav Saati: {time} | "
            "Derslik: {room}".format(

                program=values[
                    "program"
                ],

                course_code=values[
                    "course_code"
                ],

                course=values[
                    "course"
                ],

                teacher=values[
                    "teacher"
                ],

                exam_type=values[
                    "exam_type"
                ],

                date=values[
                    "date"
                ],

                time=values[
                    "time"
                ],

                room=room,
            )
        )

    if structured:

        return structured

    return None


# =========================================================
# ANA PDF OKUYUCU
# =========================================================

def extract_text(
    uploaded_file
):

    pdf = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf",
    )

    pages = []

    for page in pdf:

        structured = _extract_table_page(
            page
        )

        if structured:

            pages.append(
                "\n".join(
                    structured
                )
            )

        else:

            # Akademik takvim gibi tablo olmayan
            # PDF'ler normal metin olarak okunur.
            pages.append(
                page.get_text()
            )

    return "\n\n".join(
        pages
    )