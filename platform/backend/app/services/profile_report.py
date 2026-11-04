"""Printable profile transcript PDF.

Renders the payload from ``/api/profile/summary``: identity block, totals,
certificates of completion, every completed exercise, and course achievements.
"""

import base64
import io
from datetime import datetime, timezone

from fpdf import FPDF

from app.services.pdf_report import _sanitize_for_pdf
from app.timezones import UTC, resolve_timezone

MARGIN = 14
CONTENT_W = 210 - (MARGIN * 2)


class ProfileTranscriptPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(120, 130, 145)
        self.cell(0, 5, "OpenCyberRange Training Transcript", align="R")
        self.ln(2)
        self.set_draw_color(220, 225, 232)
        self.line(MARGIN, self.get_y(), 210 - MARGIN, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 148, 160)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}  |  OpenCyberRange", align="C")


def _sanitize(value) -> str:
    return _sanitize_for_pdf(str(value or ""))


def _truncate(value, length: int) -> str:
    text = _sanitize(value)
    if len(text) <= length:
        return text
    return text[: max(0, length - 2)] + ".."


def _format_date(value, with_time: bool = False, local_tz=UTC) -> str:
    if not value:
        return "-"
    try:
        text = str(value).replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        parsed = parsed.astimezone(local_tz)
        return parsed.strftime("%d %b %Y %H:%M" if with_time else "%d %b %Y")
    except Exception:
        return _sanitize(value)


def _section_heading(pdf: FPDF, title: str):
    if pdf.get_y() > 255:
        pdf.add_page()
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 7, _sanitize(title), new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(176, 141, 60)
    pdf.line(MARGIN, pdf.get_y(), 210 - MARGIN, pdf.get_y())
    pdf.ln(3)


def _table_header(pdf: FPDF, headers, widths):
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(37, 99, 235)
    pdf.set_text_color(255, 255, 255)
    for header, width in zip(headers, widths, strict=False):
        pdf.cell(width, 6, _sanitize(header), fill=True, align="C")
    pdf.ln()
    pdf.set_text_color(51, 65, 85)


def _draw_avatar(pdf: FPDF, data_url, x: float, y: float, size: float):
    """Embed the profile avatar if it is a usable data URL."""
    try:
        if not data_url or ";base64," not in data_url:
            return
        raw = base64.b64decode(data_url.split(",", 1)[1])
        from PIL import Image, ImageOps
        with Image.open(io.BytesIO(raw)) as source:
            image = ImageOps.fit(
                source.convert("RGB"), (240, 240), Image.Resampling.LANCZOS
            )
        pdf.image(image, x=x, y=y, w=size, h=size)
    except Exception:
        # A bad or unsupported avatar must never block the transcript.
        return


def _draw_identity(pdf: FPDF, summary: dict, local_tz=UTC):
    user = summary.get("user", {})
    _draw_avatar(pdf, user.get("avatar_data"), MARGIN, 17, 26)

    text_x = MARGIN + (34 if user.get("avatar_data") else 0)
    pdf.set_xy(text_x, 15)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(138, 109, 47)
    pdf.cell(0, 4, "OPENCYBERRANGE  /  TRAINING RECORD", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(text_x)
    pdf.set_font("Helvetica", "B", 21)
    pdf.set_text_color(17, 24, 39)
    pdf.cell(0, 9, _truncate(user.get("display_name") or user.get("username"), 52), new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(text_x)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(
        0, 5,
        _sanitize(f"@{user.get('username', '')}   |   {user.get('email', '')}"),
        new_x="LMARGIN", new_y="NEXT",    )
    if user.get("organization"):
        pdf.set_x(text_x)
        pdf.cell(0, 5, _truncate(user.get("organization"), 70), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(text_x)
    pdf.cell(
        0, 5,
        _sanitize(
            f"Member since {_format_date(user.get('created_at'), local_tz=local_tz)}   |   "
            f"Generated {_format_date(datetime.now(timezone.utc).isoformat(), True, local_tz)} {local_tz.key}"
        ),
        new_x="LMARGIN", new_y="NEXT",    )


def _draw_totals(pdf: FPDF, totals: dict):
    pdf.set_y(50)
    boxes = [
        ("Certificates", totals.get("certificates", 0)),
        (
            "Exercises completed",
            f"{totals.get('labs_completed', 0)}/{totals.get('labs_total', 0)}",
        ),
        ("Overall progress", f"{totals.get('progress_percent', 0)}%"),
        ("Achievements", totals.get("achievements", 0)),
    ]
    gap = 4
    width = (CONTENT_W - gap * (len(boxes) - 1)) / len(boxes)
    x = MARGIN
    y = pdf.get_y()
    for label, value in boxes:
        pdf.set_fill_color(246, 248, 251)
        pdf.set_draw_color(218, 224, 232)
        pdf.rect(x, y, width, 20, style="DF")
        pdf.set_xy(x, y + 3)
        pdf.set_font("Helvetica", "B", 15)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(width, 7, _sanitize(value), align="C")
        pdf.set_xy(x, y + 11)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(width, 4, _sanitize(label), align="C")
        x += width + gap
    pdf.set_y(y + 25)


def _draw_certificates(pdf: FPDF, certificates: list, local_tz=UTC):
    _section_heading(pdf, "Certificates of Completion")
    if not certificates:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(120, 128, 140)
        pdf.cell(
            0, 6,
            "No certificates yet. Complete every exercise in a level to earn one.",
            new_x="LMARGIN", new_y="NEXT",        )
        return

    widths = [48, 52, 50, 32]
    _table_header(pdf, ["Certificate ID", "Track", "Level", "Awarded"], widths)
    for index, certificate in enumerate(certificates):
        if pdf.get_y() > 267:
            pdf.add_page()
            _table_header(pdf, ["Certificate ID", "Track", "Level", "Awarded"], widths)
        if index % 2 == 0:
            pdf.set_fill_color(250, 251, 253)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Helvetica", "", 7.5)
        values = [
            _truncate(certificate.get("certificate_id"), 34),
            _truncate(certificate.get("track_name"), 38),
            _truncate(
                f"Level {certificate.get('level_number')}: {certificate.get('level_name')}",
                40,
            ),
            _format_date(certificate.get("issued_on"), local_tz=local_tz),
        ]
        for column, (value, width) in enumerate(zip(values, widths, strict=False)):
            pdf.cell(width, 6, value, fill=True, align="C" if column == 3 else "L")
        pdf.ln()


def _draw_track_progress(pdf: FPDF, tracks: list):
    _section_heading(pdf, "Track Progress")
    if not tracks:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(120, 128, 140)
        pdf.cell(0, 6, "No track progress recorded yet.", new_x="LMARGIN", new_y="NEXT")
        return

    headers = ["Track", "Completed", "Total", "Progress", "Status"]
    widths = [78, 28, 24, 26, 26]
    _table_header(pdf, headers, widths)
    for index, track in enumerate(tracks):
        if pdf.get_y() > 267:
            pdf.add_page()
            _table_header(pdf, headers, widths)
        if index % 2 == 0:
            pdf.set_fill_color(250, 251, 253)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Helvetica", "", 8)
        values = [
            _truncate(track.get("track_name"), 60),
            str(track.get("completed_labs", 0)),
            str(track.get("total_labs", 0)),
            f"{track.get('progress_percent', 0)}%",
            "Complete" if track.get("is_complete") else "In progress",
        ]
        for column, (value, width) in enumerate(zip(values, widths, strict=False)):
            pdf.cell(width, 6, value, fill=True, align="L" if column == 0 else "C")
        pdf.ln()


def _draw_completions(pdf: FPDF, completions: list, local_tz=UTC):
    _section_heading(pdf, "Completed Exercises")
    if not completions:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(120, 128, 140)
        pdf.cell(0, 6, "No exercises completed yet.", new_x="LMARGIN", new_y="NEXT")
        return

    headers = ["Track", "Level", "Exercise", f"Completed ({local_tz.key})", "Att.", "Hints", "Min"]
    widths = [34, 30, 60, 30, 9, 9, 10]
    _table_header(pdf, headers, widths)
    for index, row in enumerate(completions):
        if pdf.get_y() > 267:
            pdf.add_page()
            _table_header(pdf, headers, widths)
        if index % 2 == 0:
            pdf.set_fill_color(250, 251, 253)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Helvetica", "", 7.2)
        values = [
            _truncate(row.get("track_name"), 28),
            _truncate(row.get("level_name"), 24),
            _truncate(row.get("lab_name"), 50),
            _format_date(row.get("completed_at"), True, local_tz),
            str(row.get("attempts") or 0),
            str(row.get("hints_used") or 0),
            str(row.get("time_spent_minutes") or "-"),
        ]
        for column, (value, width) in enumerate(zip(values, widths, strict=False)):
            pdf.cell(width, 5.5, value, fill=True, align="L" if column <= 2 else "C")
        pdf.ln()


def _draw_achievements(pdf: FPDF, achievements: list):
    _section_heading(pdf, "Achievements")
    if not achievements:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(120, 128, 140)
        pdf.cell(0, 6, "No course achievements earned yet.", new_x="LMARGIN", new_y="NEXT")
        return

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(51, 65, 85)
    for achievement in achievements:
        context = []
        if achievement.get("lab_name"):
            context.append(achievement["lab_name"])
        if achievement.get("course_code"):
            context.append(achievement["course_code"])
        suffix = f"  ({_sanitize(' / '.join(context))})" if context else ""
        label = _sanitize(achievement.get("label"))
        pdf.multi_cell(
            0, 5.5,
            f"- {label}{suffix}",
            new_x="LMARGIN", new_y="NEXT",
        )
        description = achievement.get("description")
        if description:
            pdf.set_font("Helvetica", "I", 7.5)
            pdf.set_text_color(120, 128, 140)
            pdf.set_x(MARGIN + 4)
            pdf.multi_cell(
                0, 4.5, _sanitize(description),
                new_x="LMARGIN", new_y="NEXT",
            )
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(51, 65, 85)


def generate_profile_transcript(summary: dict, timezone_name: str | None = None) -> bytes:
    """Build the transcript PDF from a profile summary payload."""
    pdf = ProfileTranscriptPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(MARGIN, 14, MARGIN)
    pdf.add_page()

    local_tz = resolve_timezone(timezone_name)
    _draw_identity(pdf, summary, local_tz)
    _draw_totals(pdf, summary.get("totals", {}))
    _draw_certificates(pdf, summary.get("certificates", []), local_tz)
    _draw_track_progress(pdf, summary.get("tracks", []))
    _draw_completions(pdf, summary.get("completions", []), local_tz)
    _draw_achievements(pdf, summary.get("achievements", []))

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(140, 148, 160)
    pdf.multi_cell(
        0, 4.5,
        "Certificate IDs above match the IDs shown on each OpenCyberRange "
        "certificate page. This transcript is generated from the platform's "
        "completion record.",
        new_x="LMARGIN", new_y="NEXT",
    )

    return bytes(pdf.output())
