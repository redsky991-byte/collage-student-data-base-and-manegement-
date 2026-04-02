"""
Print utilities – generate HTML reports and open in browser for printing.
Works on any platform (Windows, macOS, Linux) without extra libraries.
"""

import os
import tempfile
import webbrowser
from datetime import datetime

import database as db


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _institution_info():
    name = db.get_setting("institution_name") or "College Management System"
    address = db.get_setting("institution_address") or ""
    phone = db.get_setting("institution_phone") or ""
    email = db.get_setting("institution_email") or ""
    return name, address, phone, email


def _html_page(title, body_html):
    name, address, phone, email = _institution_info()
    date_str = datetime.now().strftime("%B %d, %Y  %I:%M %p")
    contact_parts = [p for p in [address, phone, email] if p]
    contact_str = " &nbsp;|&nbsp; ".join(contact_parts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', Arial, sans-serif;
      font-size: 12px;
      color: #2C3E50;
      padding: 24px;
      background: #fff;
    }}
    .inst-header {{
      text-align: center;
      border-bottom: 3px solid #2C3E50;
      padding-bottom: 12px;
      margin-bottom: 18px;
    }}
    .inst-header h1 {{
      font-size: 22px;
      color: #2C3E50;
      margin-bottom: 4px;
    }}
    .inst-header .contact {{
      font-size: 11px;
      color: #7F8C8D;
      margin-top: 4px;
    }}
    .inst-header .report-title {{
      font-size: 16px;
      color: #3498DB;
      margin-top: 8px;
      font-weight: bold;
      letter-spacing: 0.5px;
    }}
    .inst-header .print-date {{
      font-size: 10px;
      color: #7F8C8D;
      margin-top: 4px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 6px;
    }}
    th {{
      background: #2C3E50;
      color: #fff;
      padding: 7px 10px;
      text-align: left;
      font-size: 11px;
      font-weight: bold;
    }}
    td {{
      padding: 6px 10px;
      border-bottom: 1px solid #ECF0F1;
      font-size: 11px;
    }}
    tr:nth-child(even) td {{ background: #F8F9FA; }}
    .section-title {{
      font-size: 15px;
      font-weight: bold;
      color: #2C3E50;
      margin: 18px 0 8px 0;
      border-left: 4px solid #3498DB;
      padding-left: 10px;
    }}
    .stats-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 18px;
    }}
    .stat-card {{
      padding: 12px 18px;
      border-radius: 6px;
      min-width: 110px;
      text-align: center;
    }}
    .stat-card .val {{ font-size: 22px; font-weight: bold; }}
    .stat-card .lbl {{ font-size: 10px; margin-top: 2px; }}
    .footer {{
      text-align: center;
      margin-top: 24px;
      font-size: 10px;
      color: #7F8C8D;
      border-top: 1px solid #ECF0F1;
      padding-top: 8px;
    }}
    @media print {{
      @page {{ margin: 1.2cm; }}
    }}
  </style>
</head>
<body>
  <div class="inst-header">
    <h1>{name}</h1>
    {f'<div class="contact">{contact_str}</div>' if contact_str else ''}
    <div class="report-title">{title}</div>
    <div class="print-date">Generated: {date_str}</div>
  </div>
  {body_html}
  <div class="footer">
    {name} &mdash; {date_str}
  </div>
  <script>
    window.addEventListener('load', function() {{ window.print(); }});
  </script>
</body>
</html>"""


def _open_html(title, body_html):
    """Write HTML to a temp file and open in default browser."""
    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".html",
        prefix="cms_print_", mode="w", encoding="utf-8"
    )
    tmp.write(_html_page(title, body_html))
    tmp.close()
    # Normalize path separators for the file:// URL
    url = "file:///" + tmp.name.replace("\\", "/")
    webbrowser.open(url)


# ─── Public helpers ───────────────────────────────────────────────────────────

def print_table(title, headers, rows, record_label="records"):
    """Print a generic table.

    headers  – list of column header strings
    rows     – list of row tuples/lists (values converted to str automatically)
    """
    th_html = "".join(f"<th>{h}</th>" for h in headers)
    rows_html = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    body = f"""
    <div class="section-title">{title}</div>
    <p style="font-size:11px; color:#7F8C8D; margin-bottom:8px;">
      Total {record_label}: {len(rows)}
    </p>
    <table>
      <thead><tr>{th_html}</tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    """
    _open_html(title, body)


def print_student_biodata(data):
    """Print a student's full biodata card."""
    name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
    sid = data.get("student_id", "")

    def _row(label, value):
        return (
            f"<tr>"
            f"<td style='font-weight:bold;width:38%;color:#7F8C8D;'>{label}</td>"
            f"<td>{value or '—'}</td>"
            f"</tr>"
        )

    rows = "".join([
        _row("Student ID", sid),
        _row("Program / Course", data.get("program", "")),
        _row("Semester", data.get("semester", "")),
        _row("Date of Birth", data.get("date_of_birth", "")),
        _row("Gender", data.get("gender", "")),
        _row("Blood Group", data.get("blood_group", "")),
        _row("Phone", data.get("phone", "")),
        _row("Email", data.get("email", "")),
        _row("Father's Name", data.get("father_name", "")),
        _row("Mother's Name", data.get("mother_name", "")),
        _row("Guardian Name", data.get("guardian_name", "")),
        _row("Guardian Phone", data.get("guardian_phone", "")),
        _row("Emergency Contact", data.get("emergency_contact", "")),
        _row("CNIC / ID Number", data.get("cnic", "")),
        _row("Nationality", data.get("nationality", "")),
        _row("Religion", data.get("religion", "")),
        _row("Address", data.get("address", "")),
        _row("Enrollment Date", data.get("enrollment_date", "")),
        _row("Status", data.get("status", "")),
    ])

    body = f"""
    <div class="section-title">&#127891; Student Biodata</div>
    <h2 style="font-size:18px;margin-bottom:4px;">{name}</h2>
    <div style="color:#3498DB;font-size:12px;margin-bottom:14px;">Student ID: {sid}</div>
    <table><tbody>{rows}</tbody></table>
    """
    _open_html(f"Student Biodata \u2013 {name}", body)


def print_staff_biodata(data):
    """Print a staff member's full biodata card."""
    name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
    sid = data.get("staff_id", "")

    def _row(label, value):
        return (
            f"<tr>"
            f"<td style='font-weight:bold;width:38%;color:#7F8C8D;'>{label}</td>"
            f"<td>{value or '—'}</td>"
            f"</tr>"
        )

    rows = "".join([
        _row("Staff ID", sid),
        _row("Department", data.get("department", "")),
        _row("Designation", data.get("designation", "")),
        _row("Date of Birth", data.get("date_of_birth", "")),
        _row("Gender", data.get("gender", "")),
        _row("Blood Group", data.get("blood_group", "")),
        _row("Phone", data.get("phone", "")),
        _row("Email", data.get("email", "")),
        _row("Father's Name", data.get("father_name", "")),
        _row("Mother's Name", data.get("mother_name", "")),
        _row("Emergency Contact", data.get("emergency_contact", "")),
        _row("CNIC / ID Number", data.get("cnic", "")),
        _row("Nationality", data.get("nationality", "")),
        _row("Religion", data.get("religion", "")),
        _row("Qualification", data.get("qualification", "")),
        _row("Experience (yrs)", data.get("experience_years", "")),
        _row("Join Date", data.get("join_date", "")),
        _row("Salary", data.get("salary", "")),
        _row("Status", data.get("status", "")),
    ])

    body = f"""
    <div class="section-title">&#128100; Staff Biodata</div>
    <h2 style="font-size:18px;margin-bottom:4px;">{name}</h2>
    <div style="color:#3498DB;font-size:12px;margin-bottom:14px;">Staff ID: {sid}</div>
    <table><tbody>{rows}</tbody></table>
    """
    _open_html(f"Staff Biodata \u2013 {name}", body)


def print_invoice(data):
    """Print a formatted invoice."""
    from utils import format_amount
    inv_no = data.get("invoice_number", "")
    amount_str = format_amount(data.get("amount", 0), data.get("currency", "USD"))

    notes_html = ""
    if data.get("notes"):
        notes_html = f"""
        <div style="margin-top:14px;">
          <strong>Notes:</strong>
          <p style="margin-top:6px;padding:10px;background:#F8F9FA;
                     border-left:4px solid #3498DB;border-radius:2px;">
            {data.get("notes", "")}
          </p>
        </div>"""

    body = f"""
    <div style="max-width:580px;margin:0 auto;">
      <div style="text-align:center;margin-bottom:20px;">
        <h2 style="font-size:24px;letter-spacing:4px;color:#3498DB;">INVOICE</h2>
        <div style="font-size:13px;color:#7F8C8D;">#{inv_no}</div>
      </div>
      <table style="margin-bottom:16px;">
        <tbody>
          <tr>
            <td style="font-weight:bold;width:36%;color:#7F8C8D;">Invoice Type</td>
            <td>{data.get("invoice_type", "")}</td>
          </tr>
          <tr>
            <td style="font-weight:bold;color:#7F8C8D;">Issue Date</td>
            <td>{data.get("issue_date", "") or "\u2014"}</td>
          </tr>
          <tr>
            <td style="font-weight:bold;color:#7F8C8D;">Due Date</td>
            <td>{data.get("due_date", "") or "\u2014"}</td>
          </tr>
          <tr>
            <td style="font-weight:bold;color:#7F8C8D;">Status</td>
            <td>{data.get("status", "")}</td>
          </tr>
          <tr>
            <td style="font-weight:bold;color:#7F8C8D;">Recipient</td>
            <td>{data.get("recipient_name", "")}</td>
          </tr>
          <tr>
            <td style="font-weight:bold;color:#7F8C8D;">Recipient Email</td>
            <td>{data.get("recipient_email", "") or "\u2014"}</td>
          </tr>
          <tr>
            <td style="font-weight:bold;color:#7F8C8D;">Reference ID</td>
            <td>{data.get("reference_id", "") or "\u2014"}</td>
          </tr>
        </tbody>
      </table>
      <div style="background:#ECF0F1;padding:14px 20px;border-radius:4px;
                  display:flex;justify-content:space-between;align-items:center;
                  margin-bottom:16px;">
        <span style="font-size:14px;font-weight:bold;">Total Amount</span>
        <span style="font-size:22px;font-weight:bold;color:#27AE60;">{amount_str}</span>
      </div>
      {notes_html}
      <div style="text-align:center;margin-top:30px;color:#7F8C8D;font-style:italic;">
        Thank you!
      </div>
    </div>
    """
    _open_html(f"Invoice {inv_no}", body)


def print_notice(data):
    """Print a notice/announcement."""
    title = data.get("title", "Notice")

    body = f"""
    <div class="section-title">&#128226; Notice / Announcement</div>
    <h2 style="font-size:18px;margin-bottom:8px;">{title}</h2>
    <table style="margin-bottom:16px;">
      <tbody>
        <tr>
          <td style="font-weight:bold;width:25%;color:#7F8C8D;">Category</td>
          <td>{data.get("category", "")}</td>
        </tr>
        <tr>
          <td style="font-weight:bold;color:#7F8C8D;">Audience</td>
          <td>{data.get("audience", "")}</td>
        </tr>
        <tr>
          <td style="font-weight:bold;color:#7F8C8D;">Posted By</td>
          <td>{data.get("posted_by", "") or "\u2014"}</td>
        </tr>
        <tr>
          <td style="font-weight:bold;color:#7F8C8D;">Date</td>
          <td>{data.get("posted_date", "")}</td>
        </tr>
        <tr>
          <td style="font-weight:bold;color:#7F8C8D;">Expiry Date</td>
          <td>{data.get("expiry_date", "") or "\u2014"}</td>
        </tr>
        <tr>
          <td style="font-weight:bold;color:#7F8C8D;">Status</td>
          <td>{"Active" if data.get("is_active") else "Inactive"}</td>
        </tr>
      </tbody>
    </table>
    <div style="margin-top:16px;">
      <strong>Content:</strong>
      <div style="margin-top:8px;padding:14px;background:#F8F9FA;
                  border-left:4px solid #3498DB;border-radius:2px;
                  white-space:pre-wrap;line-height:1.6;">
        {data.get("content", "")}
      </div>
    </div>
    """
    _open_html(f"Notice \u2013 {title}", body)


def print_dashboard(students, staff, fees, invoices, subjects, notices, att_data, fee_data):
    """Print a full dashboard summary report."""
    from utils import format_amount, get_default_currency
    currency = get_default_currency()

    active_students = sum(1 for s in students if s["status"] == "Active")
    active_staff = sum(1 for s in staff if s["status"] == "Active")
    pending_fees = sum(1 for f in fees if f["status"] == "Pending")
    total_collected = sum(f["amount"] for f in fees if f["status"] == "Paid")
    unpaid_invoices = sum(1 for i in invoices if i["status"] == "Unpaid")
    active_notices = sum(1 for n in notices)

    def _card(label, value, bg):
        return (
            f'<div class="stat-card" style="background:{bg};color:#fff;">'
            f'<div class="val">{value}</div>'
            f'<div class="lbl">{label}</div>'
            f'</div>'
        )

    cards_html = (
        _card("Active Students", active_students, "#3498DB") +
        _card("Total Students", len(students), "#2C3E50") +
        _card("Active Staff", active_staff, "#27AE60") +
        _card("Subjects", len(subjects), "#16A085") +
        _card("Pending Fees", pending_fees, "#F39C12") +
        _card("Fees Collected", format_amount(total_collected, currency), "#27AE60") +
        _card("Unpaid Invoices", unpaid_invoices, "#E74C3C") +
        _card("Active Notices", active_notices, "#D35400")
    )

    # Recent students table
    student_rows = "".join(
        f"<tr><td>{s['student_id']}</td>"
        f"<td>{s['first_name']} {s['last_name']}</td>"
        f"<td>{s.get('program','')}</td>"
        f"<td>{s.get('enrollment_date','')}</td>"
        f"<td>{s.get('status','')}</td></tr>"
        for s in students[:15]
    )

    # Recent fees table
    fee_rows = "".join(
        f"<tr><td>{f['student_id']}</td>"
        f"<td>{f['fee_type']}</td>"
        f"<td>{format_amount(f['amount'], f['currency'])}</td>"
        f"<td>{f.get('due_date','')}</td>"
        f"<td>{f['status']}</td></tr>"
        for f in fees[:15]
    )

    # Attendance summary
    student_att = att_data.get("student_attendance", {})
    total_att = sum(student_att.values())
    present_att = student_att.get("Present", 0) + student_att.get("Late", 0)
    att_pct = round(present_att / total_att * 100, 1) if total_att else 0

    body = f"""
    <div class="section-title">&#128202; Summary Statistics</div>
    <div class="stats-grid">{cards_html}</div>

    <div class="section-title">&#128203; Attendance (This Month)</div>
    <table style="max-width:500px;margin-bottom:16px;">
      <tbody>
        <tr>
          <td style="font-weight:bold;color:#7F8C8D;">Attendance Rate</td>
          <td style="font-weight:bold;color:{'#27AE60' if att_pct>=75 else '#E74C3C'};">
            {att_pct}%
          </td>
        </tr>
        <tr>
          <td style="font-weight:bold;color:#7F8C8D;">Present</td>
          <td>{student_att.get('Present',0)}</td>
        </tr>
        <tr>
          <td style="font-weight:bold;color:#7F8C8D;">Absent</td>
          <td>{student_att.get('Absent',0)}</td>
        </tr>
        <tr>
          <td style="font-weight:bold;color:#7F8C8D;">Late</td>
          <td>{student_att.get('Late',0)}</td>
        </tr>
        <tr>
          <td style="font-weight:bold;color:#7F8C8D;">Leave</td>
          <td>{student_att.get('Leave',0)}</td>
        </tr>
        <tr>
          <td style="font-weight:bold;color:#7F8C8D;">Total Collected</td>
          <td style="color:#27AE60;">{format_amount(fee_data.get('total_collected',0), currency)}</td>
        </tr>
        <tr>
          <td style="font-weight:bold;color:#7F8C8D;">Total Pending</td>
          <td style="color:#F39C12;">{format_amount(fee_data.get('total_pending',0), currency)}</td>
        </tr>
      </tbody>
    </table>

    <div class="section-title">&#127891; Recent Students (top 15)</div>
    <table>
      <thead>
        <tr>
          <th>Student ID</th><th>Name</th><th>Program</th>
          <th>Enrolled</th><th>Status</th>
        </tr>
      </thead>
      <tbody>{student_rows}</tbody>
    </table>

    <div class="section-title">&#128179; Recent Fee Records (top 15)</div>
    <table>
      <thead>
        <tr>
          <th>Student ID</th><th>Fee Type</th><th>Amount</th>
          <th>Due Date</th><th>Status</th>
        </tr>
      </thead>
      <tbody>{fee_rows}</tbody>
    </table>
    """
    _open_html("Dashboard Summary Report", body)
