from flask import Flask, render_template_string, request, redirect, url_for, send_file, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime, timedelta
import csv
import io
import os
import base64

app = Flask(__name__)
app.secret_key = os.urandom(32)
DB_NAME = 'asset_system.db'

BASE_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=Tajawal:wght@400;500;700;900&display=swap');

    :root { 
        --primary: #0284c7; 
        --primary-hover: #0369a1;
        --bg: #030712; 
        --card: rgba(15, 23, 42, 0.88); 
        --border: rgba(56, 189, 248, 0.35);
        --text: #f8fafc; 
        --text-muted: #94a3b8;
        --danger: #ef4444; 
        --danger-hover: #dc2626; 
        --success: #10b981;
        --accent: #38bdf8; 
        --warning: #f59e0b; 
        --neon-glow: 0 0 25px rgba(56, 189, 248, 0.25);
        --neon-glow-strong: 0 0 35px rgba(56, 189, 248, 0.4);
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif; }
    
    body { 
        background-color: var(--bg); 
        color: var(--text); 
        padding: 12px; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        min-height: 100vh; 
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(2, 132, 199, 0.22) 0%, transparent 65%),
            radial-gradient(circle at 80% 80%, rgba(14, 116, 144, 0.15) 0%, transparent 50%),
            linear-gradient(to bottom, #090d16, #030712);
        background-attachment: fixed;
    }

    .container { 
        width: 100%; 
        max-width: 1250px; 
        background: var(--card); 
        padding: 26px; 
        border-radius: 24px; 
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.9), var(--neon-glow); 
        border: 1px solid var(--border); 
        max-height: 96vh; 
        overflow-y: auto; 
        overflow-x: auto; 
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }

    .container::-webkit-scrollbar { width: 6px; height: 6px; }
    .container::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--primary), var(--accent)); border-radius: 10px; }
    .container::-webkit-scrollbar-track { background: rgba(2, 6, 23, 0.6); }

    h2 { 
        text-align: center; 
        color: var(--accent); 
        margin-bottom: 22px; 
        font-size: 1.5rem; 
        font-weight: 800; 
        border-bottom: 2px solid rgba(56, 189, 248, 0.3); 
        padding-bottom: 14px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        gap: 12px;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
        letter-spacing: 0.5px;
    }
    
    .form-group { margin-bottom: 16px; }
    label { display: block; margin-bottom: 7px; font-weight: 700; font-size: 0.9rem; color: var(--accent); text-shadow: 0 0 8px rgba(56, 189, 248, 0.2); }
    
    input, select, textarea { 
        width: 100%; 
        padding: 12px 16px; 
        border: 1px solid var(--border); 
        border-radius: 14px; 
        font-size: 0.95rem; 
        outline: none; 
        background: rgba(2, 6, 23, 0.85); 
        color: #fff; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
    }
    
    input[type="date"], input[type="month"] {
        cursor: pointer;
    }
    
    input:focus, select:focus, textarea:focus { 
        border-color: var(--accent); 
        box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.25), var(--neon-glow); 
        background: rgba(2, 6, 23, 0.98);
        transform: translateY(-1px);
    }
    
    select option { background: #020617; color: #fff; padding: 12px; }
    
    button { 
        width: 100%; 
        padding: 13px 20px; 
        border: none; 
        border-radius: 14px; 
        font-weight: 800; 
        cursor: pointer; 
        color: white; 
        font-size: 1rem; 
        margin-top: 10px; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
        box-shadow: 0 4px 20px rgba(0,0,0,0.5); 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        gap: 10px; 
        letter-spacing: 0.3px;
    }
    
    button:hover { 
        transform: translateY(-3px) scale(1.01); 
        box-shadow: 0 8px 25px rgba(0,0,0,0.7), var(--neon-glow); 
    }
    button:active { transform: translateY(0); }

    .btn-primary { background: linear-gradient(135deg, #0284c7, #0369a1); border: 1px solid rgba(56, 189, 248, 0.4); } 
    .btn-primary:hover { background: linear-gradient(135deg, #0369a1, #075985); }
    .btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); border: 1px solid rgba(248, 113, 113, 0.3); } 
    .btn-danger:hover { background: linear-gradient(135deg, #dc2626, #b91c1c); }
    .btn-secondary { background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid var(--border); } 
    .btn-secondary:hover { background: linear-gradient(135deg, #334155, #1e293b); color: var(--accent); }
    .btn-warning { background: linear-gradient(135deg, #f59e0b, #d97706); color: #000; font-weight: 900; }
    
    .error-msg { background: rgba(239, 68, 68, 0.18); border: 1px solid var(--danger); color: #fca5a5; padding: 14px; border-radius: 12px; text-align: center; margin-bottom: 18px; font-size: 0.95rem; font-weight: 700; backdrop-filter: blur(8px); box-shadow: 0 4px 15px rgba(239,68,68,0.2); }
    .success-msg { background: rgba(16, 185, 129, 0.18); border: 1px solid var(--success); color: #6ee7b7; padding: 14px; border-radius: 12px; text-align: center; margin-bottom: 18px; font-size: 0.95rem; font-weight: 700; backdrop-filter: blur(8px); box-shadow: 0 4px 15px rgba(16,185,129,0.2); }
    
    .footer-signature { text-align: center; margin-top: 25px; font-size: 0.88rem; color: var(--text-muted); border-top: 1px solid var(--border); padding-top: 16px; font-weight: 700; letter-spacing: 0.5px; text-shadow: 0 0 10px rgba(255,255,255,0.05); }
    .year-badge { background: linear-gradient(135deg, rgba(2, 132, 199, 0.4), rgba(30, 58, 138, 0.6)); color: #e0f2fe; padding: 8px 22px; border-radius: 30px; font-size: 0.92rem; font-weight: 800; display: inline-block; margin-bottom: 18px; box-shadow: var(--neon-glow); border: 1px solid var(--accent); }
    
    .table-container { max-height: 420px; overflow-y: auto; overflow-x: auto; border: 1px solid var(--border); border-radius: 16px; margin-top: 18px; background: rgba(2, 6, 23, 0.75); box-shadow: inset 0 0 20px rgba(0,0,0,0.8); }
    .table-container::-webkit-scrollbar { width: 6px; height: 6px; }
    .table-container::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 6px; }
    
    table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 0.88rem; table-layout: fixed; }
    th, td { padding: 12px 8px; text-align: center; border-bottom: 1px solid rgba(56, 189, 248, 0.15); border-left: 1px solid rgba(56, 189, 248, 0.15); white-space: normal; word-wrap: break-word; word-break: break-word; vertical-align: middle; }
    th:last-child, td:last-child { border-left: none; }
    th { background: rgba(15, 23, 42, 0.98); color: var(--accent); font-weight: 800; position: sticky; top: 0; z-index: 10; border-bottom: 2px solid var(--accent); text-shadow: 0 0 10px rgba(56,189,248,0.3); }
    tr.clickable-row { cursor: pointer; transition: all 0.2s ease; }
    tr.clickable-row:hover { background: rgba(56, 189, 248, 0.12); transform: scale(1.001); }

    .assets-table-container {
        max-height: 550px;
        overflow-y: auto;
        overflow-x: auto;
        border: 1px solid var(--border);
        border-radius: 16px;
        margin-top: 18px;
        background: rgba(2, 6, 23, 0.75);
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
    }
    .assets-table-container table {
        width: 100%;
        min-width: 1400px;
        table-layout: auto;
    }
    .assets-table-container th, .assets-table-container td {
        white-space: nowrap;
        padding: 14px 16px;
        font-size: 0.95rem;
    }

    .tabs-nav { display: flex; gap: 10px; margin-bottom: 22px; border-bottom: 2px solid var(--border); padding-bottom: 12px; flex-wrap: wrap; justify-content: center; }
    .tab-btn { background: rgba(30, 41, 59, 0.7); color: var(--text-muted); border: 1px solid var(--border); padding: 12px 22px; border-radius: 14px; cursor: pointer; font-weight: 800; font-size: 0.92rem; transition: all 0.3s ease; width: auto; margin-top: 0; }
    .tab-btn:hover { background: rgba(56, 189, 248, 0.2); color: #fff; transform: translateY(-2px); }
    .tab-btn.active { background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; box-shadow: var(--neon-glow); border-color: var(--accent); }
    .tab-content { display: none; }
    .tab-content.active { display: block; animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1); }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    .printable-report-card { 
        position: relative;
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(3, 7, 18, 0.98));
        border: 1.5px solid var(--accent); 
        padding: 22px; 
        border-radius: 20px; 
        margin-bottom: 22px; 
        max-width: 100%; 
        overflow-x: auto; 
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.7), var(--neon-glow);
        transition: all 0.3s ease;
    }

    .handover-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 12px;
        background: rgba(2, 6, 23, 0.75);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 14px;
    }

    .handover-field {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 10px 14px;
        transition: all 0.2s ease;
    }

    .handover-field label {
        color: var(--accent);
        font-size: 0.82rem;
        margin-bottom: 3px;
        font-weight: 800;
    }

    .handover-field span {
        color: var(--text);
        font-size: 0.95rem;
        font-weight: 700;
    }

    .signatures-box {
        display: flex;
        justify-content: space-between;
        margin-top: 24px;
        padding-top: 16px;
        border-top: 2px dashed var(--accent);
        page-break-inside: avoid;
    }
    .signature-item {
        text-align: center;
        flex: 1;
        padding: 0 8px;
    }
    .signature-title {
        font-weight: 800;
        font-size: 0.88rem;
        color: var(--accent);
        margin-bottom: 22px;
        text-shadow: 0 0 10px rgba(56,189,248,0.3);
    }
    .signature-line {
        font-size: 0.85rem;
        color: var(--text-muted);
        line-height: 1.5;
        font-weight: 600;
    }
    
    .modal-overlay {
        display: none;
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.85);
        backdrop-filter: blur(10px);
        z-index: 1000;
        justify-content: center;
        align-items: center;
    }
    .modal-box {
        background: var(--card);
        border: 2px solid var(--accent);
        border-radius: 20px;
        padding: 25px;
        width: 90%;
        max-width: 550px;
        box-shadow: 0 0 35px rgba(56, 189, 248, 0.4);
    }

    .online-users-box {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid var(--success);
        border-radius: 14px;
        padding: 12px;
        margin-bottom: 18px;
        text-align: center;
    }
    .online-badge {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: var(--success);
        border-radius: 50%;
        margin-left: 6px;
        box-shadow: 0 0 8px var(--success);
    }
    .user-chip {
        display: inline-block;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid var(--border);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 3px;
        color: #fff;
    }

    @media (max-width: 768px) {
        body { padding: 6px; }
        .container { padding: 16px; border-radius: 16px; max-height: 98vh; }
        h2 { font-size: 1.22rem; }
        button { font-size: 0.92rem; padding: 11px; }
        .signatures-box { flex-direction: column; gap: 18px; }
        .handover-grid { grid-template-columns: 1fr; }
        .tabs-nav { gap: 6px; }
        .tab-btn { padding: 8px 14px; font-size: 0.82rem; flex: 1 1 auto; text-align: center; }
    }

    @media print {
        @page { size: A4 portrait; margin: 8mm; }
        body { background: #fff !important; color: #000 !important; display: block; padding: 0; font-size: 8.5pt; font-family: 'Cairo', sans-serif !important; }
        .container { max-width: 100% !important; width: 100% !important; box-shadow: none !important; border: none !important; background: #fff !important; color: #000 !important; padding: 0 !important; margin: 0 !important; max-height: none !important; overflow: visible !important; backdrop-filter: none !important; }
        .no-print { display: none !important; }
        
        .report-header { 
            display: flex !important; 
            justify-content: space-between !important;
            align-items: center !important;
            border-bottom: 2px solid #000 !important; 
            margin-bottom: 12px !important; 
            padding-bottom: 8px !important; 
            direction: rtl !important;
        }
        
        .printable-report-card { 
            border: 2px solid #0284c7 !important; 
            padding: 16px !important; 
            margin-bottom: 20px !important; 
            border-radius: 8px !important; 
            background: #fff !important; 
            box-shadow: none !important; 
            page-break-inside: avoid; 
        }

        .handover-grid { background: #f8fafc !important; border: 1.5px solid #cbd5e1 !important; padding: 10px !important; margin-bottom: 12px !important; display: grid !important; grid-template-columns: repeat(3, 1fr) !important; gap: 10px !important; }
        .handover-field { background: #fff !important; border: 1px solid #94a3b8 !important; padding: 6px 10px !important; border-radius: 6px !important; }
        .handover-field label { color: #0284c7 !important; font-size: 8.5pt !important; font-weight: bold !important; }
        .handover-field span { color: #000 !important; font-size: 9.5pt !important; font-weight: bold !important; }

        .table-container, .assets-table-container { max-height: none !important; overflow: visible !important; border: none !important; background: #fff !important; box-shadow: none !important; }
        table { page-break-inside: auto; width: 100% !important; border: 1.5px solid #000 !important; table-layout: fixed !important; min-width: 100% !important; }
        tr { page-break-inside: avoid; page-break-after: auto; }
        th { position: static !important; background: #e2e8f0 !important; color: #000 !important; border: 1px solid #000 !important; font-weight: bold !important; text-shadow: none !important; font-size: 8.5pt !important; padding: 6px 3px !important; }
        td { border: 1px solid #64748b !important; color: #000 !important; padding: 6px 3px !important; font-weight: 600 !important; white-space: normal !important; word-wrap: break-word !important; word-break: break-word !important; font-size: 8pt !important; }
        
        .signatures-box { border-top: 2px solid #000 !important; margin-top: 20px !important; padding-top: 12px !important; display: flex !important; flex-direction: row !important; }
        .signature-title { color: #000 !important; font-size: 9pt !important; font-weight: bold !important; margin-bottom: 30px !important; text-shadow: none !important; }
        .signature-line { color: #000 !important; font-size: 9pt !important; font-weight: bold !important; }
        
        .declaration-box { background: #f8fafc !important; border: 1px dashed #000 !important; color: #000 !important; }
        .declaration-box p { color: #000 !important; }
    }
</style>
"""

def get_head(title_text):
    return f"""<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title_text}</title>{BASE_STYLE}</head>"""

def init_db():
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS management (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS departments (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, management_id TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS device_types (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS device_statuses (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS fiscal_years (id INTEGER PRIMARY KEY AUTOINCREMENT, year_name TEXT UNIQUE NOT NULL, is_active INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS assets (id INTEGER PRIMARY KEY AUTOINCREMENT, barcode TEXT, name TEXT NOT NULL, type TEXT, management TEXT, department TEXT, status TEXT, serial TEXT, notes TEXT, fiscal_year TEXT, added_by TEXT, added_time TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS reports_table (id INTEGER PRIMARY KEY AUTOINCREMENT, barcode TEXT, device_name TEXT NOT NULL, management TEXT, department TEXT, issue_description TEXT, status TEXT, report_date TEXT, technician_notes TEXT, fiscal_year TEXT, added_by TEXT, added_time TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS handover_records (id INTEGER PRIMARY KEY AUTOINCREMENT, handover_from TEXT, department_to TEXT, management_to TEXT, asset_type TEXT, manufacturer TEXT, model TEXT, barcode TEXT, asset_status TEXT, notes TEXT, purpose TEXT, directive TEXT, handover_notes TEXT, fiscal_year TEXT, added_by TEXT, added_time TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS active_sessions (username TEXT PRIMARY KEY, last_active TEXT)''')

    for table in ['assets', 'reports_table', 'handover_records']:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [col[1] for col in cursor.fetchall()]
        if 'fiscal_year' not in cols: cursor.execute(f"ALTER TABLE {table} ADD COLUMN fiscal_year TEXT")
        if 'added_by' not in cols: cursor.execute(f"ALTER TABLE {table} ADD COLUMN added_by TEXT")
        if 'added_time' not in cols: cursor.execute(f"ALTER TABLE {table} ADD COLUMN added_time TEXT")

    hashed_pw = generate_password_hash('qaid@1986@00')
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', ?, 'مسؤول')", [hashed_pw])
        
    cursor.execute("SELECT * FROM fiscal_years WHERE year_name = '2026'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO fiscal_years (year_name, is_active) VALUES ('2026', 1)")
        
    db.commit()
    db.close()

init_db()

def get_active_year():
    row = query_db("SELECT year_name FROM fiscal_years WHERE is_active = 1", one=True)
    return row['year_name'] if row else '2026'

def query_db(query, args=(), one=False):
    db = sqlite3.connect(DB_NAME)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    db.close()
    return (rv[0] if rv else None) if one else rv

def modify_db(query, args=()):
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    cursor.execute(query, args)
    db.commit()
    db.close()

def get_online_users():
    time_threshold = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    users = query_db("SELECT username FROM active_sessions WHERE last_active >= ?", [time_threshold])
    return [u['username'] for u in users]

@app.before_request
def update_user_activity():
    if 'username' in session:
        uname = session['username']
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db = sqlite3.connect(DB_NAME)
        cursor = db.cursor()
        cursor.execute('INSERT OR REPLACE INTO active_sessions (username, last_active) VALUES (?, ?)', [uname, now_str])
        db.commit()
        db.close()

def get_report_header(dynamic_title="مركز التقارير الشاملة والشبكات"):
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png")
    img_base64 = ""
    if os.path.exists(img_path):
        with open(img_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            
    img_tag = f'<img src="data:image/png;base64,{img_base64}" alt="شعار الشركة" class="header-img">' if img_base64 else '<span style="font-size: 8pt; color: #666;">[شعار الشركة]</span>'

    return f"""
<div class="report-header">
    <div class="right-text">
        <strong>الجمهورية اليمنية</strong><br>
        شركة النفط اليمنيّة - فرع الحديدة<br>
        تقنية المعلومات - قسم الصيانة والشبكات
    </div>
    <div class="center-logo">
        {img_tag}
    </div>
    <div class="left-info">
        التاريخ: <span id="p_date"></span><br>
        الوقت: <span id="p_time"></span><br>
        طباعة رقم: <span id="p_count">1</span>
    </div>
</div>

<div class="page-title-container">
    <h2 class="main-page-title" id="dynamic-report-title">{dynamic_title}</h2>
</div>

<style>
.report-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 8px;
    margin-bottom: 12px;
    direction: rtl;
}}
.right-text, .left-info {{
    font-size: 9pt;
    line-height: 1.4;
    text-align: right;
    font-weight: 700;
}}
.left-info {{
    text-align: left;
}}
.center-logo {{
    text-align: center;
    flex: 1;
}}
.header-img {{
    max-height: 52px;
    width: auto;
    filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.3));
}}
.page-title-container {{
    text-align: center;
    margin-bottom: 14px;
    border-bottom: 1.5px solid var(--accent);
    padding-bottom: 6px;
}}
.main-page-title {{
    margin: 0;
    font-size: 13pt;
    font-weight: 800;
    color: var(--accent, #0284c7);
    letter-spacing: 0.5px;
}}
@media print {{
    .main-page-title {{ color: #000 !important; }}
    .header-img {{ filter: none !important; }}
    .page-title-container {{ border-bottom: 1.5px solid #000 !important; }}
}}
</style>

<script>
    let now = new Date();
    document.getElementById('p_date').innerText = now.toLocaleDateString('ar-YE');
    document.getElementById('p_time').innerText = now.toLocaleTimeString('ar-YE');
    let printCount = localStorage.getItem('ypc_print_count') ? parseInt(localStorage.getItem('ypc_print_count')) + 1 : 1;
    localStorage.setItem('ypc_print_count', printCount);
    document.getElementById('p_count').innerText = printCount;
</script>
"""

def get_signatures_html():
    return """
<div class="signatures-box">
    <div class="signature-item">
        <div class="signature-title">رئيس قسم الصيانة والشبكات</div>
        <div class="signature-line">م. قائد الصيادي<br>...........................</div>
    </div>
    <div class="signature-item">
        <div class="signature-title">مراجعة مدير تقنية المعلومات</div>
        <div class="signature-line"><br>...........................</div>
    </div>
    <div class="signature-item">
        <div class="signature-title">اعتماد مدير عام الفرع</div>
        <div class="signature-line"><br>...........................</div>
    </div>
</div>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
""" + get_head("تسجيل الدخول - نظام الصيانة") + """
<body>
<div class="container" style="max-width: 420px;">
    <h2>🔐 تسجيل الدخول</h2>
    {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}
    <form method="POST">
        <div class="form-group">
            <label>اسم المستخدم</label>
            <input type="text" name="username" required autofocus placeholder="اسم المستخدم">
        </div>
        <div class="form-group">
            <label>كلمة المرور</label>
            <input type="password" name="password" required placeholder="كلمة المرور">
        </div>
        <button type="submit" class="btn-primary">دخول النظام</button>
    </form>
    <div class="footer-signature">إعداد وتطوير: رئيس قسم الصيانة والشبكات / م .قائد الصيادي</div>
</div>
</body>
</html>
"""

MAIN_MENU_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
""" + get_head("قسم الصيانة والشبكات - القائمة الرئيسية") + """
<body>
<div class="container" style="text-align: center;">
    <h2>⚡ نظام الصيانة والشبكات - فرع الحديدة</h2>
    <div style="font-size: 0.98rem; color: #94a3b8; margin-bottom: 12px; font-weight: 600;">👤 المستخدم: <span style="color: var(--accent); font-weight: bold;">{{ session.username }}</span> ({{ session.role }})</div>
    <div class="year-badge">📅 السنة النشطة: {{ active_year }}</div>

    <div class="online-users-box">
        <div style="font-weight: bold; color: var(--success); margin-bottom: 6px;">
            <span class="online-badge"></span>المستخدمون المتواجدون حالياً للنظام: ({{ online_users|length }})
        </div>
        <div>
            {% for u in online_users %}
                <span class="user-chip">👤 {{ u }}</span>
            {% else %}
                <span style="font-size: 0.85rem; color: var(--text-muted);">لا يوجد مستخدمون متصلون</span>
            {% endfor %}
        </div>
    </div>
    
    <div style="display: flex; flex-direction: column; gap: 14px; margin-top: 15px;">
        {% if session.role == 'مسؤول' %}
        <a href="/users" style="text-decoration: none;"><button class="btn-primary" style="background: linear-gradient(135deg, #0284c7, #0369a1);">👤 إدارة المستخدمين</button></a>
        {% endif %}
        <a href="/change_password" style="text-decoration: none;"><button class="btn-primary" style="background: linear-gradient(135deg, #0e7490, #155e75);">🔑 تغيير كلمة السر</button></a>
        <a href="/assets_mgmt" style="text-decoration: none;"><button class="btn-primary" style="background: linear-gradient(135deg, #0f766e, #115e59);">💻 إدارة الأصول، الأجهزة، والشبكات</button></a>
        <a href="/unified_reports" style="text-decoration: none;"><button class="btn-primary" style="background: linear-gradient(135deg, #047857, #065f46);">📊 مركز التقارير الشامل (الأصول، الصيانة، والمحاضر)</button></a>
        <a href="/maintenance_reports" style="text-decoration: none;"><button class="btn-primary" style="background: linear-gradient(135deg, #b45309, #92400e);">🛠️ واجهة إرسال واستقبال بلاغات الصيانة</button></a>
        <a href="/handover_mgmt" style="text-decoration: none;"><button class="btn-primary" style="background: linear-gradient(135deg, #7c2d12, #9a3412);">📋 واجهة حفظ أو تعديل محضر التسليم</button></a>
        {% if session.role == 'مسؤول' %}
        <a href="/backup_mgmt" style="text-decoration: none;"><button class="btn-primary" style="background: linear-gradient(135deg, #475569, #334155);">💾 النسخ الاحتياطي واستعادة قواعد البيانات</button></a>
        {% endif %}
    </div>
    
    <div style="margin-top: 25px;">
        <a href="/logout" style="text-decoration: none;"><button class="btn-danger">🚪 تسجيل الخروج من النظام</button></a>
    </div>
    <div class="footer-signature">إعداد وتطوير: رئيس قسم الصيانة والشبكات / م .قائد الصيادي</div>
</div>
</body>
</html>
"""

GENERIC_CRUD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
""" + get_head("إدارة القوائم والترميزات") + """
<body>
<div class="container" style="max-width: 600px;">
    <h2>⚙️ {{ title }}</h2>
    {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}

    <form method="POST">
        <div class="form-group">
            <label>{{ label }}</label>
            <input type="text" name="name" required placeholder="أدخل {{ label }}...">
        </div>
        
        {% if extra_field %}
        <div class="form-group">
            <label>تتبع لإدارة</label>
            <select name="management_id">
                <option value="">-- اختياري --</option>
                {% for m in managements %}
                <option value="{{ m.name }}">{{ m.name }}</option>
                {% endfor %}
            </select>
        </div>
        {% endif %}

        <button type="submit" class="btn-primary">إضافة للقائمة</button>
    </form>

    <h3 style="color: var(--accent); margin-top: 20px; font-size: 1rem; text-align: center;">العناصر المسجلة</h3>
    <div class="table-container">
        <table>
            <tr><th>#</th><th>الاسم</th>{% if extra_field %}<th>الإدارة التابعة</th>{% endif %}</tr>
            {% for r in rows %}
            <tr>
                <td>{{ r.id }}</td>
                <td>{{ r.name }}</td>
                {% if extra_field %}<td>{{ r.management_id or 'عام' }}</td>{% endif %}
            </tr>
            {% else %}
            <tr><td colspan="{% if extra_field %}3{% else %}2{% endif %}">لا توجد بيانات مسجلة</td></tr>
            {% endfor %}
        </table>
    </div>

    <a href="/assets_mgmt" style="text-decoration: none;"><button type="button" class="btn-secondary" style="margin-top: 15px;">الرجوع لصفحة الأصول</button></a>
</div>
</body>
</html>
"""

ASSETS_MGMT_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
""" + get_head("إدارة الأصول والأجهزة والشبكات") + """
<body>
<div class="container">
    <h2>💻 إدارة الأصول والشبكات والأجهزة</h2>
    {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}

    <div style="background: rgba(2, 6, 23, 0.85); padding: 15px; border-radius: 14px; margin-bottom: 15px; border: 1px solid var(--border);">
        <form method="GET" action="/assets_mgmt">
            <label style="color: var(--accent); margin-bottom: 6px; font-size: 0.88rem;">🔍 البحث برقم الباركود أو المعرف (ID) للتعديل السريع:</label>
            <div style="display: flex; gap: 8px;">
                <input type="text" name="search_barcode" value="{{ search_barcode }}" placeholder="أدخل رقم الباركود أو ID..." style="padding: 10px;">
                <button type="submit" class="btn-primary" style="width: 110px; margin-top:0;">استدعاء</button>
            </div>
        </form>
    </div>

    <div style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
        {% if session.role == 'مسؤول' %}
        <a href="/manage_lookup/management" style="text-decoration: none; flex: 1;"><button class="btn-secondary" style="margin-top:0;">🏢 إضافة إدارات</button></a>
        <a href="/manage_lookup/departments" style="text-decoration: none; flex: 1;"><button class="btn-secondary" style="margin-top:0;">📂 إضافة أقسام</button></a>
        <a href="/manage_lookup/device_types" style="text-decoration: none; flex: 1;"><button class="btn-secondary" style="margin-top:0;">💻 أنواع الأجهزة</button></a>
        <a href="/manage_lookup/device_statuses" style="text-decoration: none; flex: 1;"><button class="btn-secondary" style="margin-top:0;">⚙️ حالات الأجهزة</button></a>
        {% endif %}
    </div>

    <form method="POST">
        <input type="hidden" name="asset_id" id="a_asset_id" value="{{ loaded_asset.id if loaded_asset else '' }}">
        <input type="hidden" name="action" id="a_action" value="{{ 'update' if loaded_asset else 'add' }}">

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
            <div class="form-group"><label>رقم الباركود</label><input type="text" name="barcode" id="a_barcode" required placeholder="رقم الباركود" value="{{ loaded_asset.barcode if loaded_asset else search_barcode }}"></div>
            <div class="form-group"><label>اسم الجهاز / الموديل</label><input type="text" name="name" id="a_name" required placeholder="اسم الجهاز أو الموديل" value="{{ loaded_asset.name if loaded_asset else '' }}"></div>
            <div class="form-group"><label>نوع الجهاز</label>
                <select name="type" id="a_type">
                    {% for t in types %}
                    <option value="{{ t.name }}" {% if loaded_asset and loaded_asset.type == t.name %}selected{% endif %}>{{ t.name }}</option>
                    {% endfor %}
                </select>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
            <div class="form-group"><label>الإدارة</label>
                <select name="management" id="a_management">
                    {% for m in managements %}
                    <option value="{{ m.name }}" {% if loaded_asset and loaded_asset.management == m.name %}selected{% endif %}>{{ m.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group"><label>القسم</label>
                <select name="department" id="a_department">
                    {% for d in departments %}
                    <option value="{{ d.name }}" {% if loaded_asset and loaded_asset.department == d.name %}selected{% endif %}>{{ d.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group"><label>الحالة</label>
                <select name="status" id="a_status">
                    {% for s in statuses %}
                    <option value="{{ s.name }}" {% if loaded_asset and loaded_asset.status == s.name %}selected{% endif %}>{{ s.name }}</option>
                    {% endfor %}
                </select>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
            <div class="form-group"><label>الرقم التسلسلي (Serial Number)</label><input type="text" name="serial" id="a_serial" placeholder="الرقم التسلسلي" value="{{ loaded_asset.serial if loaded_asset else '' }}"></div>
            <div class="form-group"><label>ملاحظات</label><input type="text" name="notes" id="a_notes" placeholder="أي ملاحظات إضافية..." value="{{ loaded_asset.notes if loaded_asset else '' }}"></div>
        </div>

        <div style="display: flex; gap: 10px;">
            {% if loaded_asset %}
            <button type="submit" class="btn-primary" id="a_save_btn" style="background: #f59e0b; color: #000;">تعديل الأصل رقم (#{{ loaded_asset.id }})</button>
            {% else %}
            <button type="submit" class="btn-primary" id="a_save_btn">حفظ وتلقيم الأصل</button>
            {% endif %}
            <button type="button" class="btn-secondary" onclick="resetAssetForm()" style="margin-top: 8px;">إلغاء التحديد</button>
        </div>
    </form>

    <h3 style="color: var(--accent); margin-top: 25px; font-size: 1.05rem; text-align: center;">الأصول المسجلة بالنظام (اضغط للتعديل)</h3>
    <div class="assets-table-container">
        <table>
            <tr><th>#</th><th>الباركود</th><th>نوع الجهاز</th><th>الإدارة</th><th>القسم</th><th>اسم الجهاز</th><th>الحالة</th><th>السيريال</th><th>ملاحظات</th></tr>
            {% for a in assets %}
            <tr class="clickable-row" onclick="editAsset('{{ a.id }}', '{{ a.barcode }}', '{{ a.name }}', '{{ a.type }}', '{{ a.management }}', '{{ a.department }}', '{{ a.status }}', '{{ a.serial }}', '{{ a.notes }}')">
                <td>{{ a.id }}</td><td>{{ a.barcode }}</td><td>{{ a.type }}</td><td>{{ a.management }}</td><td>{{ a.department }}</td><td>{{ a.name }}</td><td>{{ a.status }}</td><td>{{ a.serial }}</td><td>{{ a.notes }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <a href="/menu" style="text-decoration: none;"><button type="button" class="btn-secondary" style="margin-top: 15px;">الرجوع للقائمة الرئيسية</button></a>
    <div class="footer-signature">إعداد: رئيس قسم الصيانة والشبكات / م .قائد الصيادي</div>
</div>

<script>
    function editAsset(id, barcode, name, type, mgmt, dept, status, serial, notes) {
        {% if session.role != 'مسؤول' %} return; {% endif %}
        document.getElementById('a_asset_id').value = id;
        document.getElementById('a_action').value = 'update';
        document.getElementById('a_barcode').value = barcode;
        document.getElementById('a_name').value = name;
        document.getElementById('a_type').value = type;
        document.getElementById('a_management').value = mgmt;
        document.getElementById('a_department').value = dept;
        document.getElementById('a_status').value = status;
        document.getElementById('a_serial').value = barcode ? serial : '';
        document.getElementById('a_notes').value = notes;
        
        let btn = document.getElementById('a_save_btn');
        if(btn) { btn.innerText = "تعديل الأصل رقم (#" + id + ")"; btn.style.background = "#f59e0b"; btn.style.color = "#000"; }
        window.scrollTo({top: 0, behavior: 'smooth'});
    }

    function resetAssetForm() {
        document.getElementById('a_asset_id').value = '';
        document.getElementById('a_action').value = 'add';
        document.getElementById('a_barcode').value = '';
        document.getElementById('a_name').value = '';
        document.getElementById('a_serial').value = '';
        document.getElementById('a_notes').value = '';
        
        let btn = document.getElementById('a_save_btn');
        if(btn) { btn.innerText = "حفظ وتلقيم الأصل"; btn.style.background = "var(--primary)"; btn.style.color = "#fff"; }
    }
</script>
</body>
</html>
"""

USERS_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
""" + get_head("إدارة المستخدمين") + """
<body>
<div class="container" style="max-width: 600px;">
    <h2>👤 إدارة مستخدمي النظام</h2>
    {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}
    {% if success %}<div class="success-msg">{{ success }}</div>{% endif %}

    <form method="POST">
        <div class="form-group"><label>اسم المستخدم</label><input type="text" name="username" required placeholder="اسم المستخدم الجديدة"></div>
        <div class="form-group"><label>كلمة المرور</label><input type="password" name="password" required placeholder="كلمة المرور"></div>
        <div class="form-group"><label>الصلاحية</label>
            <select name="role">
                <option value="مستخدم">مستخدم عادي (قراءة فقط)</option>
                <option value="مسؤول">مسؤول نظام (كامل الصلاحيات)</option>
            </select>
        </div>
        <button type="submit" class="btn-primary">إضافة مستخدم جديد</button>
    </form>

    <h3 style="color: var(--accent); margin-top: 20px; font-size: 1rem; text-align: center;">المستخدمون الحاليون</h3>
    <div class="table-container">
        <table>
            <tr><th>#</th><th>اسم المستخدم</th><th>الصلاحية</th></tr>
            {% for u in users %}
            <tr><td>{{ u.id }}</td><td>{{ u.username }}</td><td>{{ u.role }}</td></tr>
            {% endfor %}
        </table>
    </div>

    <a href="/menu" style="text-decoration: none;"><button type="button" class="btn-secondary" style="margin-top: 15px;">الرجوع للقائمة الرئيسية</button></a>
</div>
</body>
</html>
"""

CHANGE_PW_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
""" + get_head("تغيير كلمة السر") + """
<body>
<div class="container" style="max-width: 450px;">
    <h2>🔑 تغيير كلمة السر</h2>
    {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}
    {% if success %}<div class="success-msg">{{ success }}</div>{% endif %}

    <form method="POST">
        <div class="form-group"><label>كلمة المرور الحالية</label><input type="password" name="old_password" required></div>
        <div class="form-group"><label>كلمة المرور الجديدة</label><input type="password" name="new_password" required></div>
        <div class="form-group"><label>تأكيد كلمة المرور الجديدة</label><input type="password" name="confirm_password" required></div>
        <button type="submit" class="btn-primary">تحديث كلمة المرور</button>
    </form>

    <a href="/menu" style="text-decoration: none;"><button type="button" class="btn-secondary" style="margin-top: 15px;">الرجوع للقائمة الرئيسية</button></a>
</div>
</body>
</html>
"""

MAINTENANCE_FORM_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
""" + get_head("إدارة وإرسال بلاغات الصيانة") + """
<body>
<div class="container" style="max-width: {% if session.role == 'مسؤول' %}1350px{% else %}700px{% endif %};">
    <h2>🛠️ شاشة بلاغات الصيانة {% if session.role == 'مسؤول' %}(إرسال واستقبال){% else %}(إرسال بلاغ){% endif %}</h2>
    
    <div style="display: grid; grid-template-columns: {% if session.role == 'مسؤول' %}repeat(auto-fit, minmax(450px, 1fr)){% else %}1fr{% endif %}; gap: 20px; align-items: start;">
        
        <div style="background: rgba(2, 6, 23, 0.6); padding: 20px; border-radius: 18px; border: 1px solid var(--border);">
            <h3 style="color: var(--accent); font-size: 1.1rem; margin-bottom: 15px; border-bottom: 1px dashed var(--accent); padding-bottom: 8px;">📤 شاشة إرسال بلاغ جديد</h3>
            
            <form method="GET" action="/maintenance_reports" style="margin-bottom: 15px;">
                <label style="color: var(--accent); font-size: 0.85rem; font-weight: bold;">🔍 استدعاء سريع بالباركود:</label>
                <div style="display: flex; gap: 8px; margin-top: 5px;">
                    <input type="text" name="search_barcode" value="{{ search_barcode }}" placeholder="أدخل الباركود..." style="padding: 8px;">
                    <button type="submit" class="btn-primary" style="width: 100px; margin-top:0; padding: 8px;">استدعاء</button>
                </div>
            </form>

            <form method="POST">
                <input type="hidden" name="action" value="add">
                <input type="hidden" name="status" value="قيد المتابعة الفنية">
                <input type="hidden" name="technician_notes" value="">

                <div class="form-group"><label>رقم الباركود</label><input type="text" name="barcode" id="m_send_barcode" value="{{ search_barcode }}" placeholder="الباركود إن وجد"></div>
                <div class="form-group"><label>اسم الجهاز</label><input type="text" name="device_name" id="m_send_device_name" value="{{ device_name }}" required placeholder="اسم الجهاز والموديل"></div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div class="form-group"><label>الإدارة</label>
                        <select name="management" id="m_send_mgmt">
                            {% for m in managements %}<option value="{{ m.name }}" {% if selected_management == m.name %}selected{% endif %}>{{ m.name }}</option>{% endfor %}
                        </select>
                    </div>
                    <div class="form-group"><label>القسم</label>
                        <select name="department" id="m_send_dept">
                            {% for d in departments %}<option value="{{ d.name }}" {% if selected_department == d.name %}selected{% endif %}>{{ d.name }}</option>{% endfor %}
                        </select>
                    </div>
                </div>

                <div class="form-group"><label>تاريخ البلاغ</label><input type="date" name="report_date" value="{{ today_date }}" onclick="this.showPicker()" required></div>
                <div class="form-group"><label>وصف المشكلة / العطل</label><textarea name="issue_description" rows="3" required placeholder="صف العطل أو المشكلة بالتفصيل..."></textarea></div>

                <button type="submit" class="btn-primary" style="background: linear-gradient(135deg, #0284c7, #0369a1); font-size: 1.05rem;">📨 إرسال البلاغ للفني</button>
            </form>
        </div>

        {% if session.role == 'مسؤول' %}
        <div style="background: rgba(2, 6, 23, 0.6); padding: 20px; border-radius: 18px; border: 1px solid var(--border);">
            <h3 style="color: #f59e0b; font-size: 1.1rem; margin-bottom: 15px; border-bottom: 1px dashed #f59e0b; padding-bottom: 8px;">📥 جدول البلاغات الواردة (اضغط للرد والصيانة)</h3>
            
            <div class="table-container" style="max-height: 480px;">
                <table>
                    <tr>
                        <th>#</th>
                        <th>الباركود</th>
                        <th>الجهاز</th>
                        <th>الإدارة/القسم</th>
                        <th>العطل</th>
                        <th>التاريخ</th>
                    </tr>
                    {% for r in maint_reports %}
                    <tr class="clickable-row" onclick="openTechModal('{{ r.id }}', '{{ r.barcode }}', '{{ r.device_name }}', '{{ r.management }}', '{{ r.department }}', '{{ r.issue_description }}', '{{ r.report_date }}')">
                        <td>{{ r.id }}</td>
                        <td>{{ r.barcode }}</td>
                        <td>{{ r.device_name }}</td>
                        <td>{{ r.management }} - {{ r.department }}</td>
                        <td>{{ r.issue_description }}</td>
                        <td>{{ r.report_date }}</td>
                    </tr>
                    {% else %}
                    <tr><td colspan="6" style="padding: 20px; color: #10b981; font-weight: bold;">🎉 لا توجد بلاغات واردة معلقة حالياً</td></tr>
                    {% endfor %}
                </table>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 10px; text-align: center;">💡 عند قيام الفني بحفظ الإجراء وتحديث الحالة، يختفي البلاغ تلقائياً من هنا ويحفظ بالتقارير الموحدة.</p>
        </div>
        {% endif %}

    </div>

    {% if session.role == 'مسؤول' %}
    <div class="modal-overlay" id="techModal">
        <div class="modal-box">
            <h3 style="color: var(--accent); margin-bottom: 12px; text-align: center; border-bottom: 1px solid var(--border); padding-bottom: 8px;">🔧 معالجة البلاغ الوارد رقم (#<span id="modal_id_display"></span>)</h3>
            
            <form method="POST">
                <input type="hidden" name="action" value="update">
                <input type="hidden" name="maint_id" id="modal_maint_id">
                <input type="hidden" name="barcode" id="modal_barcode">
                <input type="hidden" name="device_name" id="modal_device_name">
                <input type="hidden" name="management" id="modal_management">
                <input type="hidden" name="department" id="modal_department">
                <input type="hidden" name="report_date" id="modal_report_date">
                <input type="hidden" name="issue_description" id="modal_issue_description">

                <div style="background: rgba(15, 23, 42, 0.9); padding: 10px; border-radius: 10px; margin-bottom: 12px; font-size: 0.88rem;">
                    <div><strong>الجهاز:</strong> <span id="info_device" style="color: var(--accent);"></span></div>
                    <div><strong>الجهة:</strong> <span id="info_dept"></span></div>
                    <div><strong>العطل:</strong> <span id="info_issue" style="color: #fca5a5;"></span></div>
                </div>

                <div class="form-group">
                    <label style="color: #f59e0b;">1. حالة الصيانة</label>
                    <select name="status" id="modal_status" required>
                        {% for s in statuses %}
                        <option value="{{ s.name }}">{{ s.name }}</option>
                        {% endfor %}
                    </select>
                </div>

                <div class="form-group">
                    <label style="color: #f59e0b;">2. الإجراء الفني المتخذ عند الصيانة</label>
                    <textarea name="technician_notes" id="modal_technician_notes" rows="3" required placeholder="اكتب الإجراء الفني المتخذ لمعالجة العطل..."></textarea>
                </div>

                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <button type="submit" class="btn-primary" style="background: linear-gradient(135deg, #10b981, #059669);">💾 حفظ وإغلاق البلاغ</button>
                    <button type="button" class="btn-secondary" onclick="closeTechModal()">إلغاء</button>
                </div>
            </form>
        </div>
    </div>
    {% endif %}

    <div style="margin-top: 20px;">
        <a href="/menu" style="text-decoration: none;"><button type="button" class="btn-secondary">الرجوع للقائمة الرئيسية</button></a>
    </div>
    <div class="footer-signature">إعداد: رئيس قسم الصيانة والشبكات / م .قائد الصيادي</div>
</div>

<script>
    function openTechModal(id, barcode, device, mgmt, dept, issue, rDate) {
        document.getElementById('modal_maint_id').value = id;
        document.getElementById('modal_id_display').innerText = id;
        document.getElementById('modal_barcode').value = barcode;
        document.getElementById('modal_device_name').value = device;
        document.getElementById('modal_management').value = mgmt;
        document.getElementById('modal_department').value = dept;
        document.getElementById('modal_report_date').value = rDate;
        document.getElementById('modal_issue_description').value = issue;

        document.getElementById('info_device').innerText = device + " (" + barcode + ")";
        document.getElementById('info_dept').innerText = mgmt + " - " + dept;
        document.getElementById('info_issue').innerText = issue;

        document.getElementById('techModal').style.display = 'flex';
    }

    function closeTechModal() {
        document.getElementById('techModal').style.display = 'none';
    }
</script>
</body>
</html>
"""

BACKUP_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
""" + get_head("النسخ الاحتياطي واستعادة البيانات") + """
<body>
<div class="container" style="max-width: 550px;">
    <h2>💾 النسخ الاحتياطي والإداري</h2>
    {% if error %}<div class="error-msg">{{ error }}</div>{% endif %}
    {% if success %}<div class="success-msg">{{ success }}</div>{% endif %}

    <div style="display: flex; flex-direction: column; gap: 15px; margin-top: 20px;">
        <a href="/download_backup" style="text-decoration: none;"><button class="btn-primary" style="background: linear-gradient(135deg, #047857, #065f46);">📥 تحميل نسخة احتياطية من قاعدة البيانات (.db)</button></a>
        
        <form method="POST" enctype="multipart/form-data" style="border: 1px dashed var(--border); padding: 15px; border-radius: 14px; margin-top: 10px; background: rgba(2, 6, 23, 0.5);">
            <label style="color: var(--accent); margin-bottom: 8px;">📂 استعادة قاعدة بيانات من ملف خارجي:</label>
            <input type="file" name="backup_file" accept=".db" required style="margin-bottom: 10px;">
            <button type="submit" class="btn-danger">⚠️ استعادة وإعادة كتابة القاعدة الحالية</button>
        </form>
    </div>

    <a href="/menu" style="text-decoration: none;"><button type="button" class="btn-secondary" style="margin-top: 20px;">الرجوع للقائمة الرئيسية</button></a>
</div>
</body>
</html>
"""

UNIFIED_REPORTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
""" + get_head("مركز التقارير الشاملة") + """
<body>
<div class="container">
    <div class="no-print">
        <h2>📊 مركز التقارير الموحدة والطباعة</h2>
        <div class="tabs-nav">
            <button class="tab-btn active" onclick="switchTab('tab1', this)">🖥️ 1. تقرير الأصول المصفى</button>
            <button class="tab-btn" onclick="switchTab('tab2', this)">🛠️ 2. بطاقة/كشف بلاغات الصيانة</button>
            <button class="tab-btn" onclick="switchTab('tab3', this)">📋 3. محاضر وتسليم الأصول</button>
        </div>
    </div>

    <!-- TAB 1: ASSETS REPORT -->
    <div id="tab1" class="tab-content active">
        <div class="no-print" style="background: rgba(2, 6, 23, 0.85); padding: 15px; border-radius: 14px; margin-bottom: 15px; border: 1px solid var(--border);">
            <form method="GET" action="/unified_reports">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px;">
                    <div class="form-group"><label>تصفية بالإدارة</label>
                        <select name="filter_mgmt" onchange="this.form.submit()">
                            <option value="">كافة الإدارات</option>
                            {% for m in managements %}<option value="{{ m.name }}" {% if filter_mgmt == m.name %}selected{% endif %}>{{ m.name }}</option>{% endfor %}
                        </select>
                    </div>
                    <div class="form-group"><label>تصفية بالقسم</label>
                        <select name="filter_dept" onchange="this.form.submit()">
                            <option value="">كافة الأقسام</option>
                            {% for d in departments %}<option value="{{ d.name }}" {% if filter_dept == d.name %}selected{% endif %}>{{ d.name }}</option>{% endfor %}
                        </select>
                    </div>
                    <div class="form-group"><label>تصفية بالنوع</label>
                        <select name="filter_type" onchange="this.form.submit()">
                            <option value="">كافة الأنواع</option>
                            {% for t in types %}<option value="{{ t.name }}" {% if filter_type == t.name %}selected{% endif %}>{{ t.name }}</option>{% endfor %}
                        </select>
                    </div>
                    <div class="form-group"><label>تصفية بالحالة</label>
                        <select name="filter_status" onchange="this.form.submit()">
                            <option value="">كافة الحالات</option>
                            {% for s in statuses %}<option value="{{ s.name }}" {% if filter_status == s.name %}selected{% endif %}>{{ s.name }}</option>{% endfor %}
                        </select>
                    </div>
                </div>
            </form>
            <div style="display: flex; gap: 10px; margin-top: 10px;">
                <button onclick="window.print()" class="btn-primary" style="background: linear-gradient(135deg, #0284c7, #0369a1);">🖨️ طباعة تقرير الأصول الحالية</button>
                <a href="/export_assets_excel?filter_dept={{ filter_dept }}&filter_mgmt={{ filter_mgmt }}&filter_status={{ filter_status }}&filter_type={{ filter_type }}" style="text-decoration: none; width: 100%;"><button class="btn-primary" style="background: linear-gradient(135deg, #047857, #065f46);">📥 تصدير كـ Excel</button></a>
            </div>
        </div>

        {{ report_header|safe }}

        <div class="table-container">
            <table>
                <tr><th>#</th><th>الباركود</th><th>نوع الجهاز</th><th>الإدارة</th><th>القسم</th><th>اسم الجهاز/الموديل</th><th>الحالة</th><th>السيريال</th><th>ملاحظات</th></tr>
                {% for a in filtered_assets %}
                <tr>
                    <td>{{ loop.index }}</td><td>{{ a.barcode }}</td><td>{{ a.type }}</td><td>{{ a.management }}</td><td>{{ a.department }}</td><td>{{ a.name }}</td><td>{{ a.status }}</td><td>{{ a.serial }}</td><td>{{ a.notes }}</td>
                </tr>
                {% else %}
                <tr><td colspan="9">لا توجد أصول مطابقة لخيارات التصفية المختارة</td></tr>
                {% endfor %}
            </table>
        </div>
        {{ signatures_html|safe }}
    </div>

    <!-- TAB 2: MAINTENANCE REPORTS -->
    <div id="tab2" class="tab-content">
        <div class="no-print" style="background: rgba(2, 6, 23, 0.85); padding: 15px; border-radius: 14px; margin-bottom: 15px; border: 1px solid var(--border);">
            <form method="GET" action="/unified_reports">
                <label style="color: var(--accent); font-weight: bold; font-size: 0.9rem;">🔍 بحث برقم الباركود أو رقم البلاغ لطباعة بطاقة صيانة فردية:</label>
                <div style="display: flex; gap: 8px; margin-top: 6px; margin-bottom: 12px;">
                    <input type="text" name="barcode_search_maint" value="{{ barcode_search_maint }}" placeholder="أدخل رقم الباركود أو ID البلاغ..." style="padding: 8px;">
                    <button type="submit" class="btn-primary" style="width: 110px; margin-top:0;">استدعاء</button>
                </div>
            </form>
            <hr style="border-color: var(--border); margin: 10px 0;">
            <form method="GET" action="/unified_reports">
                <label style="color: var(--accent); font-weight: bold; font-size: 0.9rem;">📅 تصفية كشف البلاغات بالشهر أو الفترة الزمنية للطباعة:</label>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-top: 6px;">
                    <div class="form-group"><label>اختر الشهر والسنة</label><input type="month" name="maint_month" value="{{ maint_month }}" onclick="this.showPicker()"></div>
                    <div class="form-group"><label>من تاريخ</label><input type="date" name="maint_from_date" value="{{ maint_from_date }}" onclick="this.showPicker()"></div>
                    <div class="form-group"><label>إلى تاريخ</label><input type="date" name="maint_to_date" value="{{ maint_to_date }}" onclick="this.showPicker()"></div>
                </div>
                <button type="submit" class="btn-primary" style="background: linear-gradient(135deg, #0e7490, #155e75); margin-top: 6px;">عرض وتصفية الكشف</button>
            </form>
            <div style="display: flex; gap: 10px; margin-top: 12px;">
                <button onclick="window.print()" class="btn-primary" style="background: linear-gradient(135deg, #0284c7, #0369a1);">🖨️ طباعة المحدّد حالياً</button>
                <a href="/export_maintenance_excel" style="text-decoration: none; width: 100%;"><button class="btn-primary" style="background: linear-gradient(135deg, #047857, #065f46);">📥 تصدير كافة البلاغات كـ Excel</button></a>
            </div>
        </div>

        {% if barcode_search_maint and filtered_maint %}
            {% for r in filtered_maint %}
            <div class="printable-report-card">
                {{ report_header|safe }}
                <h3 style="text-align: center; color: var(--accent); margin-bottom: 12px; font-size: 1.1rem;">بطاقة بلاغ وإنجاز صيانة (رقم #{{ r.id }})</h3>
                <div class="handover-grid">
                    <div class="handover-field"><label>رقم الباركود</label><span>{{ r.barcode }}</span></div>
                    <div class="handover-field"><label>اسم الجهاز</label><span>{{ r.device_name }}</span></div>
                    <div class="handover-field"><label>الإدارة / القسم</label><span>{{ r.management }} - {{ r.department }}</span></div>
                    <div class="handover-field"><label>تاريخ البلاغ</label><span>{{ r.report_date }}</span></div>
                    <div class="handover-field"><label>حالة الصيانة</label><span>{{ r.status }}</span></div>
                    <div class="handover-field"><label>تاريخ القيد للنظام</label><span>{{ r.added_time }}</span></div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.08); padding: 12px; border-radius: 10px; margin-bottom: 10px;">
                    <strong style="color: var(--accent); font-size: 0.88rem;">وصف العطل والمشكلة:</strong>
                    <p style="margin-top: 5px; font-size: 0.92rem;">{{ r.issue_description }}</p>
                </div>
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.08); padding: 12px; border-radius: 10px;">
                    <strong style="color: var(--accent); font-size: 0.88rem;">الإجراء الفني المتخذ والملاحظات:</strong>
                    <p style="margin-top: 5px; font-size: 0.92rem;">{{ r.technician_notes if r.technician_notes else 'قيد الفحص والمتابعة' }}</p>
                </div>
                <div class="declaration-box" style="margin-top: 10px; border: 1px dashed var(--border); padding: 10px; border-radius: 10px; background: rgba(255,255,255,0.02);">
                    <p style="font-size: 0.82rem; font-weight: bold; margin-bottom: 6px; color: var(--accent);">إقرار الاستلام:</p>
                    <p style="font-size: 0.8rem; margin-bottom: 12px; color: #cbd5e1;">(أقر أنا المستلم بموجبه بأنني عاينت الأصل الموضح أعلاه واستلمته وهو بحالة جيدة وصالح للاستخدام )</p>
                    <div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: bold; text-align: center; margin-top: 6px;">
                        <div>المستلم:<br><br>...........................</div>
                        <div>رئيس القسم:<br><br>...........................</div>
                        <div>مدير الإدارة:<br><br>...........................</div>
                    </div>
                </div>

                {{ signatures_html|safe }}
            </div>
            {% endfor %}
        {% else %}
            {{ report_header|safe }}
            <h3 style="text-align: center; color: var(--accent); margin-bottom: 10px;" class="no-print">{{ maint_table_title }}</h3>
            <div class="table-container">
                <table>
                    <tr><th>#</th><th>الباركود</th><th>اسم الجهاز</th><th>الإدارة</th><th>القسم</th><th>وصف العطل</th><th>حالة الصيانة</th><th>التاريخ</th><th>ملاحظات الفني</th></tr>
                    {% for r in all_maintenance_reports %}
                    <tr>
                        <td>{{ r.id }}</td><td>{{ r.barcode }}</td><td>{{ r.device_name }}</td><td>{{ r.management }}</td><td>{{ r.department }}</td><td>{{ r.issue_description }}</td><td>{{ r.status }}</td><td>{{ r.report_date }}</td><td>{{ r.technician_notes }}</td>
                    </tr>
                    {% else %}
                    <tr><td colspan="9">لا توجد بلاغات صيانة مسجلة بالفترة المحكددة</td></tr>
                    {% endfor %}
                </table>
            </div>
            {{ signatures_html|safe }}
        {% endif %}
    </div>

    <!-- TAB 3: HANDOVER RECORDS -->
    <div id="tab3" class="tab-content">
        <div class="no-print" style="background: rgba(2, 6, 23, 0.85); padding: 15px; border-radius: 14px; margin-bottom: 15px; border: 1px solid var(--border);">
            <form method="GET" action="/unified_reports">
                <label style="color: var(--accent); font-weight: bold; font-size: 0.9rem;">🔍 بحث بالباركود لاستدعاء بطاقة محضر تسليم مفردة:</label>
                <div style="display: flex; gap: 8px; margin-top: 6px; margin-bottom: 12px;">
                    <input type="text" name="barcode_search_handover" value="{{ barcode_search_handover }}" placeholder="أدخل رقم الباركود..." style="padding: 8px;">
                    <button type="submit" class="btn-primary" style="width: 110px; margin-top:0;">استدعاء المحضر</button>
                </div>
            </form>
            <hr style="border-color: var(--border); margin: 10px 0;">
            <form method="GET" action="/unified_reports">
                <label style="color: var(--accent); font-weight: bold; font-size: 0.9rem;">📅 تصفية كشف المحاضر بالشهر أو الفترة الزمنية:</label>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-top: 6px;">
                    <div class="form-group"><label>اختر الشهر والسنة</label><input type="month" name="handover_month" value="{{ handover_month }}" onclick="this.showPicker()"></div>
                    <div class="form-group"><label>من تاريخ</label><input type="date" name="handover_from_date" value="{{ handover_from_date }}" onclick="this.showPicker()"></div>
                    <div class="form-group"><label>إلى تاريخ</label><input type="date" name="handover_to_date" value="{{ handover_to_date }}" onclick="this.showPicker()"></div>
                </div>
                <button type="submit" class="btn-primary" style="background: linear-gradient(135deg, #0e7490, #155e75); margin-top: 6px;">عرض وتصفية الكشف</button>
            </form>
            <div style="display: flex; gap: 10px; margin-top: 12px;">
                <button onclick="window.print()" class="btn-primary" style="background: linear-gradient(135deg, #0284c7, #0369a1);">🖨️ طباعة المحدّد حالياً</button>
                <a href="/export_handover_excel" style="text-decoration: none; width: 100%;"><button class="btn-primary" style="background: linear-gradient(135deg, #047857, #065f46);">📥 تصدير المحاضر كـ Excel</button></a>
            </div>
        </div>

        {% if barcode_search_handover and filtered_handovers %}
            {% for h in filtered_handovers %}
            <div class="printable-report-card">
                {{ report_header|safe }}
                <h3 style="text-align: center; color: var(--accent); margin-bottom: 12px; font-size: 1.1rem;">محضر تسليم واستلام أصل (رقم #{{ h.id }})</h3>
                <div class="handover-grid">
                    <div class="handover-field"><label>المسلم (من)</label><span>{{ h.handover_from }}</span></div>
                    <div class="handover-field"><label>الإدارة المستلمة</label><span>{{ h.management_to }}</span></div>
                    <div class="handover-field"><label>القسم المستلم</label><span>{{ h.department_to }}</span></div>
                    <div class="handover-field"><label>نوع الأصل</label><span>{{ h.asset_type }}</span></div>
                    <div class="handover-field"><label>الشركة المصنعة</label><span>{{ h.manufacturer }}</span></div>
                    <div class="handover-field"><label>الموديل / Name</label><span>{{ h.model }}</span></div>
                    <div class="handover-field"><label>الباركود</label><span>{{ h.barcode }}</span></div>
                    <div class="handover-field"><label>حالة الجهاز</label><span>{{ h.asset_status }}</span></div>
                    <div class="handover-field"><label>تاريخ التسليم</label><span>{{ h.added_time }}</span></div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.08); padding: 10px 14px; border-radius: 10px; margin-bottom: 10px;">
                    <strong style="color: var(--accent); font-size: 0.88rem;">الغرض والوجب:</strong> <span style="font-size: 0.9rem;">{{ h.purpose }}</span> | 
                    <strong style="color: var(--accent); font-size: 0.88rem; margin-right: 10px;">التوجيه:</strong> <span style="font-size: 0.9rem;">{{ h.directive }}</span>
                </div>
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.08); padding: 10px 14px; border-radius: 10px;">
                    <strong style="color: var(--accent); font-size: 0.88rem;">ملاحظات التسليم:</strong> <span style="font-size: 0.9rem;">{{ h.handover_notes }}</span>
                </div>

                <div class="declaration-box" style="margin-top: 10px; border: 1px dashed var(--border); padding: 10px; border-radius: 10px; background: rgba(255,255,255,0.02);">
                    <p style="font-size: 0.82rem; font-weight: bold; margin-bottom: 6px; color: var(--accent);">إقرار الاستلام:</p>
                    <p style="font-size: 0.8rem; margin-bottom: 12px; color: #cbd5e1;">(أقر أنا المستلم بموجبه بأنني أستلمت الأصل الموضح بياناته أعلاه )</p>
                    <div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: bold; text-align: center; margin-top: 6px;">
                        <div>المستلم:<br><br>...........................</div>
                        <div>رئيس القسم:<br><br>...........................</div>
                        <div>مدير الإدارة:<br><br>...........................</div>
                    </div>
                </div>

                {{ signatures_html|safe }}
            </div>
            {% endfor %}
        {% else %}
            {{ report_header|safe }}
            <h3 style="text-align: center; color: var(--accent); margin-bottom: 10px;" class="no-print">{{ handover_table_title }}</h3>
            <div class="table-container">
                <table>
                    <tr><th>#</th><th>المسلم</th><th>الإدارة المستلمة</th><th>القسم المستلم</th><th>نوع الأصل</th><th>الموديل</th><th>الباركود</th><th>الحالة</th><th>التاريخ</th></tr>
                    {% for h in all_handover_records %}
                    <tr>
                        <td>{{ h.id }}</td><td>{{ h.handover_from }}</td><td>{{ h.management_to }}</td><td>{{ h.department_to }}</td><td>{{ h.asset_type }}</td><td>{{ h.model }}</td><td>{{ h.barcode }}</td><td>{{ h.asset_status }}</td><td>{{ h.added_time }}</td>
                    </tr>
                    {% else %}
                    <tr><td colspan="9">لا توجد محاضر تسليم مسجلة بالفترة المحددة</td></tr>
                    {% endfor %}
                </table>
            </div>
            {{ signatures_html|safe }}
        {% endif %}
    </div>

    <div class="no-print" style="margin-top: 20px;">
        <a href="/menu" style="text-decoration: none;"><button type="button" class="btn-secondary">الرجوع للقائمة الرئيسية</button></a>
    </div>
    <div class="footer-signature no-print">إعداد: رئيس قسم الصيانة والشبكات / م .قائد الصيادي</div>
</div>

<script>
    function switchTab(tabId, btn) {
        document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(tb => tb.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        btn.classList.add('active');
    }
</script>
</body>
</html>
"""

HANDOVER_FORM_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
""" + get_head("محاضر تسليم واستلام الأصول") + """
<body>
<div class="container">
    <h2>📋 واجهة تسجيل وتعديل محاضر تسليم واستلام الأصول</h2>
    
    <div style="background: rgba(2, 6, 23, 0.85); padding: 15px; border-radius: 14px; margin-bottom: 15px; border: 1px solid var(--border);">
        <form method="GET" action="/handover_mgmt">
            <label style="color: var(--accent); margin-bottom: 6px; font-size: 0.88rem;">🔍 البحث برقم الباركود لاستدعاء بيانات الأصل تلقائياً:</label>
            <div style="display: flex; gap: 8px;">
                <input type="text" name="search_barcode" value="{{ search_barcode }}" placeholder="أدخل رقم الباركود..." style="padding: 10px;">
                <button type="submit" class="btn-primary" style="width: 110px; margin-top:0;">استدعاء</button>
            </div>
        </form>
    </div>

    <form method="POST">
        <input type="hidden" name="record_id" id="h_record_id" value="">
        <input type="hidden" name="action" id="h_action" value="add">
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
            <div class="form-group"><label>سلمت من قبل (المسلم)</label><input type="text" name="handover_from" id="h_from" required placeholder="اسم جهة أو شخص المسلم..."></div>
            <div class="form-group"><label>الإدارة المستلمة</label>
                <select name="management_to" id="h_mgmt_to">
                    {% for m in managements %}<option value="{{ m.name }}" {% if selected_management == m.name %}selected{% endif %}>{{ m.name }}</option>{% endfor %}
                </select>
            </div>
            <div class="form-group"><label>القسم المستلم</label>
                <select name="department_to" id="h_dept_to">
                    {% for d in departments %}<option value="{{ d.name }}" {% if selected_department == d.name %}selected{% endif %}>{{ d.name }}</option>{% endfor %}
                </select>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
            <div class="form-group"><label>نوع الأصل</label>
                <select name="asset_type" id="h_type">
                    {% for t in types %}<option value="{{ t.name }}" {% if selected_type == t.name %}selected{% endif %}>{{ t.name }}</option>{% endfor %}
                </select>
            </div>
            <div class="form-group"><label>الشركة المصنعة</label><input type="text" name="manufacturer" id="h_manufacturer" value="{{ manufacturer }}" placeholder="مثال: HP / Dell / Cisco"></div>
            <div class="form-group"><label>اسم الجهاز / الموديل</label><input type="text" name="model" id="h_model" value="{{ model }}" required placeholder="الموديل والاسم"></div>
            <div class="form-group"><label>رقم الباركود</label><input type="text" name="barcode" id="h_barcode" value="{{ search_barcode }}"></div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
            <div class="form-group"><label>حالة الأصل عند التسليم</label>
                <select name="asset_status" id="h_status">
                    {% for s in statuses %}<option value="{{ s.name }}" {% if selected_status == s.name %}selected{% endif %}>{{ s.name }}</option>{% endfor %}
                </select>
            </div>
            <div class="form-group"><label>الغرض والوجب</label><input type="text" name="purpose" id="h_purpose" placeholder="مثال: استبدال جهاز تالف / عهدة جديدة"></div>
            <div class="form-group"><label>التوجيه الإداري</label><input type="text" name="directive" id="h_directive" placeholder="بناءً على توجيهات..."></div>
        </div>

        <div class="form-group"><label>ملاحظات إضافية على الأصل أو التسليم</label><textarea name="handover_notes" id="h_notes" rows="2" placeholder="أي ملاحظات حول الملحقات أو حالة الجهاز..."></textarea></div>

        <div style="display: flex; gap: 10px;">
            <button type="submit" class="btn-primary" id="h_save_btn">حفظ محضر التسليم</button>
            <button type="button" class="btn-secondary" onclick="resetHandoverForm()" style="margin-top: 8px;">إلغاء التحديد</button>
        </div>
    </form>

    <h3 style="color: var(--accent); margin-top: 25px; font-size: 1.05rem; text-align: center;">سجل المحاضر المسجلة (اضغط للتعديل)</h3>
    <div class="table-container">
        <table>
            <tr><th>#</th><th>المسلم</th><th>الإدارة المستلمة</th><th>القسم المستلم</th><th>نوع الأصل</th><th>الموديل</th><th>الباركود</th><th>الحالة</th><th>تاريخ التسليم</th></tr>
            {% for h in handovers %}
            <tr class="clickable-row" onclick="editHandover('{{ h.id }}', '{{ h.handover_from }}', '{{ h.management_to }}', '{{ h.department_to }}', '{{ h.asset_type }}', '{{ h.manufacturer }}', '{{ h.model }}', '{{ h.barcode }}', '{{ h.asset_status }}', '{{ h.purpose }}', '{{ h.directive }}', '{{ h.handover_notes }}')">
                <td>{{ h.id }}</td><td>{{ h.handover_from }}</td><td>{{ h.management_to }}</td><td>{{ h.department_to }}</td><td>{{ h.asset_type }}</td><td>{{ h.model }}</td><td>{{ h.barcode }}</td><td>{{ h.asset_status }}</td><td>{{ h.added_time }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <a href="/menu" style="text-decoration: none;"><button type="button" class="btn-secondary" style="margin-top: 15px;">الرجوع للقائمة الرئيسية</button></a>
    <div class="footer-signature">إعداد: رئيس قسم الصيانة والشبكات / م .قائد الصيادي</div>
</div>

<script>
    function editHandover(id, from, mgmt, dept, type, mfg, model, barcode, status, purpose, directive, notes) {
        {% if session.role != 'مسؤول' %} return; {% endif %}
        document.getElementById('h_record_id').value = id;
        document.getElementById('h_action').value = 'update';
        document.getElementById('h_from').value = from;
        document.getElementById('h_mgmt_to').value = mgmt;
        document.getElementById('h_dept_to').value = dept;
        document.getElementById('h_type').value = type;
        document.getElementById('h_manufacturer').value = mfg;
        document.getElementById('h_model').value = model;
        document.getElementById('h_barcode').value = barcode;
        document.getElementById('h_status').value = status;
        document.getElementById('h_purpose').value = purpose;
        document.getElementById('h_directive').value = directive;
        document.getElementById('h_notes').value = notes;
        
        let btn = document.getElementById('h_save_btn');
        if(btn) { btn.innerText = "تعديل محضر التسليم رقم (#" + id + ")"; btn.style.background = "#f59e0b"; btn.style.color = "#000"; }
        window.scrollTo({top: 0, behavior: 'smooth'});
    }

    function resetHandoverForm() {
        document.getElementById('h_record_id').value = '';
        document.getElementById('h_action').value = 'add';
        document.getElementById('h_from').value = '';
        document.getElementById('h_manufacturer').value = '';
        document.getElementById('h_model').value = '';
        document.getElementById('h_barcode').value = '';
        document.getElementById('h_purpose').value = '';
        document.getElementById('h_directive').value = '';
        document.getElementById('h_notes').value = '';
        
        let btn = document.getElementById('h_save_btn');
        if(btn) { btn.innerText = "حفظ محضر التسليم"; btn.style.background = "var(--primary)"; btn.style.color = "#fff"; }
    }
</script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        uname = request.form['username']
        pw = request.form['password']
        user = query_db("SELECT * FROM users WHERE username = ?", [uname], one=True)
        if user and check_password_hash(user['password'], pw):
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('menu'))
        else:
            error = "اسم المستخدم أو كلمة المرور غير صحيحة"
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/menu')
def menu():
    if 'username' not in session: return redirect(url_for('login'))
    online_users = get_online_users()
    return render_template_string(MAIN_MENU_TEMPLATE, active_year=get_active_year(), online_users=online_users)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/users', methods=['GET', 'POST'])
def users_mgmt():
    if 'username' not in session or session.get('role') != 'مسؤول': return redirect(url_for('menu'))
    error = None
    success = None
    if request.method == 'POST':
        uname = request.form['username']
        pw = request.form['password']
        role = request.form['role']
        if query_db("SELECT * FROM users WHERE username = ?", [uname], one=True):
            error = "اسم المستخدم موجود بالفعل"
        else:
            modify_db("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", [uname, generate_password_hash(pw), role])
            success = "تمت إضافة المستخدم بنجاح"
    return render_template_string(USERS_TEMPLATE, users=query_db("SELECT id, username, role FROM users"), error=error, success=success)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session: return redirect(url_for('login'))
    error = None
    success = None
    if request.method == 'POST':
        old_pw = request.form['old_password']
        new_pw = request.form['new_password']
        confirm_pw = request.form['confirm_password']
        
        user = query_db("SELECT * FROM users WHERE username = ?", [session['username']], one=True)
        if not check_password_hash(user['password'], old_pw):
            error = "كلمة المرور الحالية غير صحيحة"
        elif new_pw != confirm_pw:
            error = "كلمة المرور الجديدة وتأكيدها غير متطابقين"
        else:
            modify_db("UPDATE users SET password = ? WHERE username = ?", [generate_password_hash(new_pw), session['username']])
            success = "تم تحديث كلمة المرور بنجاح"
    return render_template_string(CHANGE_PW_TEMPLATE, error=error, success=success)

@app.route('/assets_mgmt', methods=['GET', 'POST'])
def assets_mgmt():
    if 'username' not in session: return redirect(url_for('login'))
    error = None
    search_barcode = request.args.get('search_barcode', '')
    loaded_asset = None

    if search_barcode:
        loaded_asset = query_db("SELECT * FROM assets WHERE barcode = ? OR id = ?", [search_barcode, search_barcode], one=True)
        if not loaded_asset:
            error = "لم يتم العثور على أصل بهذا الرقم أو الباركود"

    if request.method == 'POST':
        action = request.form.get('action', 'add')
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if action == 'add':
            modify_db("""INSERT INTO assets (barcode, name, type, management, department, status, serial, notes, fiscal_year, added_by, added_time) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                      [request.form.get('barcode'), request.form.get('name'), request.form.get('type'), 
                       request.form.get('management'), request.form.get('department'), request.form.get('status'), 
                       request.form.get('serial'), request.form.get('notes'), get_active_year(), 
                       session['username'], now_str])
        elif action == 'update' and session.get('role') == 'مسؤول':
            modify_db("""UPDATE assets SET barcode=?, name=?, type=?, management=?, department=?, status=?, serial=?, notes=? WHERE id=?""",
                      [request.form.get('barcode'), request.form.get('name'), request.form.get('type'), 
                       request.form.get('management'), request.form.get('department'), request.form.get('status'), 
                       request.form.get('serial'), request.form.get('notes'), request.form.get('asset_id')])
        return redirect(url_for('assets_mgmt'))

    return render_template_string(
        ASSETS_MGMT_TEMPLATE,
        search_barcode=search_barcode,
        loaded_asset=loaded_asset,
        managements=query_db("SELECT * FROM management"),
        departments=query_db("SELECT * FROM departments"),
        types=query_db("SELECT * FROM device_types"),
        statuses=query_db("SELECT * FROM device_statuses"),
        assets=query_db("SELECT * FROM assets WHERE fiscal_year = ?", [get_active_year()]),
        error=error
    )

@app.route('/manage_lookup/<lookup_type>', methods=['GET', 'POST'])
def manage_lookup(lookup_type):
    if 'username' not in session or session.get('role') != 'مسؤول': return redirect(url_for('menu'))
    
    config = {
        'management': {'table': 'management', 'title': 'إدارة الإدارات العامة', 'label': 'اسم الإدارة', 'extra': False},
        'departments': {'table': 'departments', 'title': 'إدارة الأقسام والوحدات', 'label': 'اسم القسم', 'extra': True},
        'device_types': {'table': 'device_types', 'title': 'إدارة أنواع الأجهزة', 'label': 'نوع الجهاز', 'extra': False},
        'device_statuses': {'table': 'device_statuses', 'title': 'إدارة حالات الأجهزة', 'label': 'حالة الجهاز', 'extra': False}
    }
    
    if lookup_type not in config: return redirect(url_for('assets_mgmt'))
    cfg = config[lookup_type]
    error = None

    if request.method == 'POST':
        name = request.form.get('name')
        mgmt_id = request.form.get('management_id')
        try:
            if cfg['extra']:
                modify_db(f"INSERT INTO {cfg['table']} (name, management_id) VALUES (?, ?)", [name, mgmt_id])
            else:
                modify_db(f"INSERT INTO {cfg['table']} (name) VALUES (?)", [name])
        except sqlite3.IntegrityError:
            error = "هذا العنصر مسجل مسبقاً"

    rows = query_db(f"SELECT * FROM {cfg['table']}")
    managements = query_db("SELECT * FROM management") if cfg['extra'] else []
    
    return render_template_string(
        GENERIC_CRUD_TEMPLATE,
        title=cfg['title'],
        label=cfg['label'],
        rows=rows,
        extra_field=cfg['extra'],
        managements=managements,
        error=error
    )

@app.route('/maintenance_reports', methods=['GET', 'POST'])
def maintenance_reports():
    if 'username' not in session: return redirect(url_for('login'))
    
    search_barcode = request.args.get('search_barcode', '')
    device_name = ""
    selected_mgmt = ""
    selected_dept = ""
    
    if search_barcode:
        asset = query_db("SELECT * FROM assets WHERE barcode = ?", [search_barcode], one=True)
        if asset:
            device_name = asset['name']
            selected_mgmt = asset['management']
            selected_dept = asset['department']

    if request.method == 'POST':
        action = request.form.get('action', 'add')
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if action == 'add':
            modify_db("""INSERT INTO reports_table 
                         (barcode, device_name, management, department, issue_description, status, report_date, technician_notes, fiscal_year, added_by, added_time) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      [request.form.get('barcode'), request.form.get('device_name'), request.form.get('management'),
                       request.form.get('department'), request.form.get('issue_description'), request.form.get('status', 'قيد المتابعة الفنية'),
                       request.form.get('report_date'), request.form.get('technician_notes', ''), get_active_year(),
                       session['username'], now_str])
        elif action == 'update' and session.get('role') == 'مسؤول':
            modify_db("""UPDATE reports_table 
                         SET barcode=?, device_name=?, management=?, department=?, issue_description=?, status=?, report_date=?, technician_notes=? 
                         WHERE id=?""",
                      [request.form.get('barcode'), request.form.get('device_name'), request.form.get('management'),
                       request.form.get('department'), request.form.get('issue_description'), request.form.get('status'),
                       request.form.get('report_date'), request.form.get('technician_notes'), request.form.get('maint_id')])
            
        return redirect(url_for('maintenance_reports'))

    pending_reports = []
    if session.get('role') == 'مسؤول':
        pending_reports = query_db("SELECT * FROM reports_table WHERE fiscal_year = ? AND (technician_notes IS NULL OR technician_notes = '' OR status LIKE '%متابعة%') ORDER BY id DESC", [get_active_year()])

    return render_template_string(
        MAINTENANCE_FORM_TEMPLATE,
        search_barcode=search_barcode,
        device_name=device_name,
        selected_management=selected_mgmt,
        selected_department=selected_dept,
        managements=query_db("SELECT * FROM management"),
        departments=query_db("SELECT * FROM departments"),
        statuses=query_db("SELECT * FROM device_statuses"),
        today_date=datetime.now().strftime('%Y-%m-%d'),
        maint_reports=pending_reports
    )

@app.route('/handover_mgmt', methods=['GET', 'POST'])
def handover_mgmt():
    if 'username' not in session: return redirect(url_for('login'))
    
    search_barcode = request.args.get('search_barcode', '')
    model = ""
    selected_mgmt = ""
    selected_dept = ""
    selected_type = ""
    selected_status = ""
    manufacturer = ""
    
    if search_barcode:
        asset = query_db("SELECT * FROM assets WHERE barcode = ?", [search_barcode], one=True)
        if asset:
            model = asset['name']
            selected_mgmt = asset['management']
            selected_dept = asset['department']
            selected_type = asset['type']
            selected_status = asset['status']

    if request.method == 'POST':
        action = request.form.get('action', 'add')
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if action == 'add':
            modify_db("""INSERT INTO handover_records 
                         (handover_from, department_to, management_to, asset_type, manufacturer, model, barcode, asset_status, purpose, directive, handover_notes, fiscal_year, added_by, added_time) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      [request.form.get('handover_from'), request.form.get('department_to'), request.form.get('management_to'),
                       request.form.get('asset_type'), request.form.get('manufacturer'), request.form.get('model'),
                       request.form.get('barcode'), request.form.get('asset_status'), request.form.get('purpose'),
                       request.form.get('directive'), request.form.get('handover_notes'), get_active_year(),
                       session['username'], now_str])
        elif action == 'update' and session.get('role') == 'مسؤول':
            modify_db("""UPDATE handover_records 
                         SET handover_from=?, department_to=?, management_to=?, asset_type=?, manufacturer=?, model=?, barcode=?, asset_status=?, purpose=?, directive=?, handover_notes=? 
                         WHERE id=?""",
                      [request.form.get('handover_from'), request.form.get('department_to'), request.form.get('management_to'),
                       request.form.get('asset_type'), request.form.get('manufacturer'), request.form.get('model'),
                       request.form.get('barcode'), request.form.get('asset_status'), request.form.get('purpose'),
                       request.form.get('directive'), request.form.get('handover_notes'), request.form.get('record_id')])
            
        return redirect(url_for('handover_mgmt'))

    return render_template_string(
        HANDOVER_FORM_TEMPLATE,
        search_barcode=search_barcode,
        model=model,
        manufacturer=manufacturer,
        selected_management=selected_mgmt,
        selected_department=selected_dept,
        selected_type=selected_type,
        selected_status=selected_status,
        managements=query_db("SELECT * FROM management"),
        departments=query_db("SELECT * FROM departments"),
        types=query_db("SELECT * FROM device_types"),
        statuses=query_db("SELECT * FROM device_statuses"),
        handovers=query_db("SELECT * FROM handover_records WHERE fiscal_year = ? ORDER BY id DESC", [get_active_year()])
    )

@app.route('/unified_reports')
def unified_reports():
    if 'username' not in session: return redirect(url_for('login'))
    
    filter_mgmt = request.args.get('filter_mgmt', '')
    filter_dept = request.args.get('filter_dept', '')
    filter_type = request.args.get('filter_type', '')
    filter_status = request.args.get('filter_status', '')

    assets_query = "SELECT * FROM assets WHERE fiscal_year = ?"
    params = [get_active_year()]
    if filter_mgmt:
        assets_query += " AND management = ?"
        params.append(filter_mgmt)
    if filter_dept:
        assets_query += " AND department = ?"
        params.append(filter_dept)
    if filter_type:
        assets_query += " AND type = ?"
        params.append(filter_type)
    if filter_status:
        assets_query += " AND status = ?"
        params.append(filter_status)
        
    filtered_assets = query_db(assets_query, params)

    barcode_search_maint = request.args.get('barcode_search_maint', '')
    maint_month = request.args.get('maint_month', '')
    maint_from_date = request.args.get('maint_from_date', '')
    maint_to_date = request.args.get('maint_to_date', '')

    filtered_maint = []
    if barcode_search_maint:
        filtered_maint = query_db("SELECT * FROM reports_table WHERE barcode = ? OR id = ?", [barcode_search_maint, barcode_search_maint])

    maint_query = "SELECT * FROM reports_table WHERE fiscal_year = ?"
    maint_params = [get_active_year()]
    maint_title = "كشف بلاغات الصيانة العامة"

    if maint_from_date and maint_to_date:
        maint_query += " AND report_date BETWEEN ? AND ?"
        maint_params.extend([maint_from_date, maint_to_date])
        maint_title = f"كشف بلاغات الصيانة للفترة من {maint_from_date} إلى {maint_to_date}"
    elif maint_month:
        maint_query += " AND report_date LIKE ?"
        maint_params.append(f"{maint_month}%")
        maint_title = f"كشف بلاغات الصيانة لشهر ({maint_month})"

    maint_query += " ORDER BY id DESC"
    all_maintenance_reports = query_db(maint_query, maint_params)

    barcode_search_handover = request.args.get('barcode_search_handover', '')
    handover_month = request.args.get('handover_month', '')
    handover_from_date = request.args.get('handover_from_date', '')
    handover_to_date = request.args.get('handover_to_date', '')

    filtered_handovers = []
    if barcode_search_handover:
        filtered_handovers = query_db("SELECT * FROM handover_records WHERE barcode = ? OR id = ?", [barcode_search_handover, barcode_search_handover])

    handover_query = "SELECT * FROM handover_records WHERE fiscal_year = ?"
    handover_params = [get_active_year()]
    handover_title = "كشف محاضر تسليم واستلام الأصول"

    if handover_from_date and handover_to_date:
        handover_query += " AND (added_time BETWEEN ? AND ? OR substr(added_time, 1, 10) BETWEEN ? AND ?)"
        handover_params.extend([handover_from_date, handover_to_date, handover_from_date, handover_to_date])
        handover_title = f"كشف محاضر التسليم للفترة من {handover_from_date} إلى {handover_to_date}"
    elif handover_month:
        handover_query += " AND added_time LIKE ?"
        handover_params.append(f"{handover_month}%")
        handover_title = f"كشف محاضر التسليم لشهر ({handover_month})"

    handover_query += " ORDER BY id DESC"
    all_handover_records = query_db(handover_query, handover_params)

    return render_template_string(
        UNIFIED_REPORTS_TEMPLATE,
        report_header=get_report_header(),
        signatures_html=get_signatures_html(),
        managements=query_db("SELECT * FROM management"),
        departments=query_db("SELECT * FROM departments"),
        types=query_db("SELECT * FROM device_types"),
        statuses=query_db("SELECT * FROM device_statuses"),
        filter_mgmt=filter_mgmt,
        filter_dept=filter_dept,
        filter_type=filter_type,
        filter_status=filter_status,
        filtered_assets=filtered_assets,
        barcode_search_maint=barcode_search_maint,
        maint_month=maint_month,
        maint_from_date=maint_from_date,
        maint_to_date=maint_to_date,
        filtered_maint=filtered_maint,
        all_maintenance_reports=all_maintenance_reports,
        maint_table_title=maint_title,
        barcode_search_handover=barcode_search_handover,
        handover_month=handover_month,
        handover_from_date=handover_from_date,
        handover_to_date=handover_to_date,
        filtered_handovers=filtered_handovers,
        all_handover_records=all_handover_records,
        handover_table_title=handover_title
    )

@app.route('/export_assets_excel')
def export_assets_excel():
    if 'username' not in session: return redirect(url_for('login'))
    
    filter_mgmt = request.args.get('filter_mgmt', '')
    filter_dept = request.args.get('filter_dept', '')
    filter_type = request.args.get('filter_type', '')
    filter_status = request.args.get('filter_status', '')

    assets_query = "SELECT * FROM assets WHERE fiscal_year = ?"
    params = [get_active_year()]
    if filter_mgmt: assets_query += " AND management = ?"; params.append(filter_mgmt)
    if filter_dept: assets_query += " AND department = ?"; params.append(filter_dept)
    if filter_type: assets_query += " AND type = ?"; params.append(filter_type)
    if filter_status: assets_query += " AND status = ?"; params.append(filter_status)
    
    assets = query_db(assets_query, params)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'الباركود', 'نوع الجهاز', 'الإدارة', 'القسم', 'اسم الجهاز', 'الحالة', 'السيريال', 'ملاحظات'])

    for a in assets:
        writer.writerow([a['id'], a['barcode'], a['type'], a['management'], a['department'], a['name'], a['status'], a['serial'], a['notes']])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='assets_report.csv'
    )

@app.route('/export_maintenance_excel')
def export_maintenance_excel():
    if 'username' not in session: return redirect(url_for('login'))
    
    reports = query_db("SELECT * FROM reports_table WHERE fiscal_year = ? ORDER BY id DESC", [get_active_year()])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'الباركود', 'اسم الجهاز', 'الإدارة', 'القسم', 'وصف العطل', 'حالة الصيانة', 'تاريخ البلاغ', 'ملاحظات الفني'])

    for r in reports:
        writer.writerow([r['id'], r['barcode'], r['device_name'], r['management'], r['department'], r['issue_description'], r['status'], r['report_date'], r['technician_notes']])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='maintenance_reports.csv'
    )

@app.route('/export_handover_excel')
def export_handover_excel():
    if 'username' not in session: return redirect(url_for('login'))
    
    handovers = query_db("SELECT * FROM handover_records WHERE fiscal_year = ? ORDER BY id DESC", [get_active_year()])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'المسلم', 'الإدارة المستلمة', 'القسم المستلم', 'نوع الأصل', 'الموديل', 'الباركود', 'الحالة', 'تاريخ التسليم'])

    for h in handovers:
        writer.writerow([h['id'], h['handover_from'], h['management_to'], h['department_to'], h['asset_type'], h['model'], h['barcode'], h['asset_status'], h['added_time']])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='handover_records.csv'
    )

@app.route('/backup_mgmt', methods=['GET', 'POST'])
def backup_mgmt():
    if 'username' not in session or session.get('role') != 'مسؤول': return redirect(url_for('menu'))
    error = None
    success = None
    if request.method == 'POST':
        if 'backup_file' in request.files:
            file = request.files['backup_file']
            if file and file.filename.endswith('.db'):
                file.save(DB_NAME)
                success = "تمت استعادة قاعدة البيانات بنجاح"
            else:
                error = "يرجى اختيار ملف قاعدة بيانات بصيغة .db"
    return render_template_string(BACKUP_TEMPLATE, error=error, success=success)

@app.route('/download_backup')
def download_backup():
    if 'username' not in session or session.get('role') != 'مسؤول': return redirect(url_for('menu'))
    return send_file(DB_NAME, as_attachment=True, download_name=f"asset_system_backup_{datetime.now().strftime('%Y%m%d')}.db")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
