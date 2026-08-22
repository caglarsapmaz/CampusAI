def create_chunks(
    text,
    chunk_size=1200,
):
    """
    Metni satır bütünlüğünü koruyarak böler.

    Özellikle ders tablolarındaki:

    Program
    Ders Kodu
    Ders Adı
    Öğretim Üyesi
    Sınav Tarihi
    Derslik

    bilgilerinin aynı chunk içerisinde kalmasını sağlar.
    """

    if not text:
        return []

    text = (
        str(text)
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    chunks = []

    current = []

    current_len = 0

    for line in lines:

        # Tek satır chunk boyutunu aşıyorsa
        # doğrudan böl.
        if len(line) > chunk_size:

            if current:

                chunks.append(
                    "\n".join(
                        current
                    )
                )

                current = []

                current_len = 0

            for i in range(
                0,
                len(line),
                chunk_size,
            ):

                chunks.append(
                    line[
                        i:
                        i + chunk_size
                    ]
                )

            continue

        extra = (
            len(line)
            + (
                1
                if current
                else 0
            )
        )

        if (
            current
            and
            current_len
            + extra
            > chunk_size
        ):

            chunks.append(
                "\n".join(
                    current
                )
            )

            current = []

            current_len = 0

        current.append(
            line
        )

        current_len += (
            len(line)
            + (
                1
                if len(current) > 1
                else 0
            )
        )

    if current:

        chunks.append(
            "\n".join(
                current
            )
        )

    return chunks