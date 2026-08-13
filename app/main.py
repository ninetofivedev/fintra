import os, sqlite3, statistics, heapq, hashlib, hmac, secrets, csv, io, tempfile, random, time, math
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import quote
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse, Response, FileResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.background import BackgroundTask
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .version import __version__

BASE = Path(__file__).resolve().parent
DB = Path(os.getenv('DB_PATH', '/app/data/haushaltsbuch.db'))
DB.parent.mkdir(parents=True, exist_ok=True)

def session_secret() -> str:
    configured = os.getenv('FINTRA_SECRET_KEY')
    if configured:
        return configured
    secret_file = DB.parent / '.session_secret'
    try:
        if secret_file.exists():
            value = secret_file.read_text().strip()
            if value:
                return value
        value = secrets.token_urlsafe(48)
        secret_file.write_text(value)
        try:
            os.chmod(secret_file, 0o600)
        except OSError:
            pass
        return value
    except OSError:
        return secrets.token_urlsafe(48)


app = FastAPI(title='Fintra', version=__version__)
SECRET_KEY = session_secret()
SESSION_HTTPS_ONLY = os.getenv('FINTRA_HTTPS_ONLY', '0') == '1'
templates = Jinja2Templates(directory=str(BASE / 'templates'))
templates.env.globals['app_version'] = __version__
app.mount('/static', StaticFiles(directory=str(BASE / 'static')), name='static')

MONTHS = ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember']
MONTHS_SHORT = ['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez']
COLS = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
DEFAULT = [
    ('Gehalt','income'),('Zinsen','income'),('Rückerstattung','income'),('Sonstiges','income'),
    ('Einkauf','expense'),('Auswärtsessen','expense'),('Kraftstoff','expense'),('Freizeit','expense'),
    ('Kleidung','expense'),('Gesundheit','expense'),('Haushalt','expense'),('Auto','expense'),
    ('Mobilfunk','expense'),('Fitness','expense'),('Sonstiges','expense')
]

# A small application-owned index. The database remains the source of truth.
# category_id -> list of transaction ids. Building it is O(n), lookup is O(1) average.
class TransactionIndex:
    def __init__(self, rows):
        self.by_category = {}
        self.by_type = {'income': [], 'expense': []}
        for row in rows:
            tid = row['id']; cid = row['category_id']; typ = row['type']
            self.by_category.setdefault(cid, []).append(tid)
            self.by_type.setdefault(typ, []).append(tid)

    def category_count(self, category_id):
        return len(self.by_category.get(category_id, []))


def db():
    c = sqlite3.connect(DB, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    c.execute('PRAGMA busy_timeout=10000')
    return c


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=2**14, r=8, p=1)
    return f'scrypt${salt.hex()}${digest.hex()}'


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_hex, digest_hex = stored.split('$', 2)
        if scheme != 'scrypt':
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def validate_next(value: str | None) -> str:
    return value if value and value.startswith('/') and not value.startswith('//') else '/'


def check_csrf(request: Request, token: str) -> bool:
    expected = str(request.session.get('csrf_token', ''))
    return bool(expected) and hmac.compare_digest(token, expected)


def user_count() -> int:
    c = db(); n = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]; c.close(); return n


def valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, '%Y-%m-%d')
        return True
    except (TypeError, ValueError):
        return False


def cents(s, *, positive=False):
    raw = str(s).strip().replace('€', '').replace(' ', '')
    if not raw:
        return 0
    # Accept German 1.234,56 as well as 1234.56 / 1234,56.
    if ',' in raw:
        raw = raw.replace('.', '').replace(',', '.')
    try:
        value = Decimal(raw).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        raise ValueError('Ungültiger Geldbetrag.')
    if not value.is_finite():
        raise ValueError('Ungültiger Geldbetrag.')
    if value < 0:
        raise ValueError('Betrag darf nicht negativ sein.')
    if positive and value <= 0:
        raise ValueError('Betrag muss größer als 0 sein.')
    if value > Decimal('999999999.99'):
        raise ValueError('Betrag ist zu groß.')
    return int(value * 100)


def init():
    c = db()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL UNIQUE,
      password_hash TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS categories(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      type TEXT NOT NULL CHECK(type IN ('income','expense')),
      active INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS transactions(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      tx_date TEXT NOT NULL,
      type TEXT NOT NULL CHECK(type IN ('income','expense')),
      category_id INTEGER NOT NULL,
      amount_cents INTEGER NOT NULL,
      comment TEXT,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(category_id) REFERENCES categories(id)
    );
    CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(tx_date);
    CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);
    CREATE TABLE IF NOT EXISTS budgets(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      year INTEGER NOT NULL,
      month INTEGER NOT NULL,
      category_id INTEGER NOT NULL,
      amount_cents INTEGER NOT NULL DEFAULT 0,
      UNIQUE(year, month, category_id),
      FOREIGN KEY(category_id) REFERENCES categories(id)
    );
    CREATE INDEX IF NOT EXISTS idx_budgets_period ON budgets(year, month);
    ''')

    fixed_exists = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fixed_items'").fetchone()
    if not fixed_exists:
        c.execute('''CREATE TABLE fixed_items(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          year INTEGER NOT NULL,
          name TEXT NOT NULL,
          type TEXT NOT NULL CHECK(type IN ('income','expense')),
          jan INTEGER NOT NULL DEFAULT 0, feb INTEGER NOT NULL DEFAULT 0,
          mar INTEGER NOT NULL DEFAULT 0, apr INTEGER NOT NULL DEFAULT 0,
          may INTEGER NOT NULL DEFAULT 0, jun INTEGER NOT NULL DEFAULT 0,
          jul INTEGER NOT NULL DEFAULT 0, aug INTEGER NOT NULL DEFAULT 0,
          sep INTEGER NOT NULL DEFAULT 0, oct INTEGER NOT NULL DEFAULT 0,
          nov INTEGER NOT NULL DEFAULT 0, dec INTEGER NOT NULL DEFAULT 0
        )''')
    else:
        cols = [r['name'] for r in c.execute('PRAGMA table_info(fixed_items)').fetchall()]
        if 'year' not in cols:
            current_year = date.today().year
            c.execute(f'ALTER TABLE fixed_items ADD COLUMN year INTEGER NOT NULL DEFAULT {current_year}')

    if c.execute('SELECT COUNT(*) n FROM categories').fetchone()['n'] == 0:
        c.executemany('INSERT INTO categories(name,type) VALUES(?,?)', DEFAULT)
    if c.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0:
        bootstrap_user = os.getenv('FINTRA_USERNAME', '').strip()
        bootstrap_password = os.getenv('FINTRA_PASSWORD', '')
        if bootstrap_user and bootstrap_password:
            c.execute('INSERT INTO users(username,password_hash) VALUES(?,?)', (bootstrap_user, hash_password(bootstrap_password)))
    c.commit(); c.close()

init()


@app.middleware('http')
async def require_login(request: Request, call_next):
    public = request.url.path in {'/login', '/setup', '/health'} or request.url.path.startswith('/static/')
    if public:
        return await call_next(request)
    if user_count() == 0:
        return RedirectResponse('/setup', 303)
    if not request.session.get('user_id'):
        next_url = quote(request.url.path + (('?' + request.url.query) if request.url.query else ''), safe='')
        return RedirectResponse('/login?next=' + next_url, 303)
    request.session.setdefault('csrf_token', secrets.token_urlsafe(32))
    return await call_next(request)


app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, session_cookie='fintra_session', max_age=60 * 60 * 24 * 30, same_site='lax', https_only=SESSION_HTTPS_ONLY)


@app.get('/health', include_in_schema=False)
def health():
    try:
        c = db()
        c.execute('SELECT 1').fetchone()
        c.close()
        return {'status': 'ok', 'version': __version__}
    except sqlite3.Error:
        return JSONResponse(
            {'status': 'error', 'version': __version__},
            status_code=503
        )


@app.get('/login', response_class=HTMLResponse)
def login_page(request: Request, next: str = '/'):
    if request.session.get('user_id'):
        return RedirectResponse(validate_next(next), 303)
    return templates.TemplateResponse('login.html', {'request': request, 'next': validate_next(next), 'error': None})


@app.post('/login', response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...), next: str = Form('/')):
    c = db(); user = c.execute('SELECT * FROM users WHERE username=?', (username.strip(),)).fetchone(); c.close()
    if not user or not verify_password(password, user['password_hash']):
        return templates.TemplateResponse('login.html', {'request': request, 'next': validate_next(next), 'error': 'Benutzername oder Passwort ist falsch.'}, status_code=401)
    request.session.clear(); request.session['user_id'] = user['id']; request.session['username'] = user['username']
    return RedirectResponse(validate_next(next), 303)


@app.post('/logout')
def logout(request: Request, csrf_token: str = Form(...)):
    if not check_csrf(request, csrf_token):
        return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).', status_code=403)
    request.session.clear()
    return RedirectResponse('/login', 303)


@app.get('/profile', response_class=HTMLResponse)
def profile_page(request: Request, changed: int = 0):
    c = db()
    user = c.execute(
        'SELECT id,username,created_at FROM users WHERE id=?',
        (request.session.get('user_id'),)
    ).fetchone()
    c.close()

    if not user:
        request.session.clear()
        return RedirectResponse('/login', 303)

    return templates.TemplateResponse('profile.html', {
        'request': request,
        'user': user,
        'error': None,
        'success': 'Passwort erfolgreich geändert.' if changed else None,
    })


@app.post('/profile/password', response_class=HTMLResponse)
def change_profile_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    new_password_confirm: str = Form(...),
    csrf_token: str = Form('')
):
    if not check_csrf(request, csrf_token):
        return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).', status_code=403)

    c = db()
    user = c.execute(
        'SELECT * FROM users WHERE id=?',
        (request.session.get('user_id'),)
    ).fetchone()

    def render_error(message: str, status_code: int = 400):
        c.close()
        return templates.TemplateResponse('profile.html', {
            'request': request,
            'user': user,
            'error': message,
            'success': None,
        }, status_code=status_code)

    if not user:
        c.close()
        request.session.clear()
        return RedirectResponse('/login', 303)

    if not verify_password(current_password, user['password_hash']):
        return render_error('Das aktuelle Passwort ist nicht korrekt.', 400)

    if len(new_password) < 10:
        return render_error('Das neue Passwort muss mindestens 10 Zeichen lang sein.')

    if new_password != new_password_confirm:
        return render_error('Die neuen Passwörter stimmen nicht überein.')

    if verify_password(new_password, user['password_hash']):
        return render_error('Das neue Passwort muss sich vom aktuellen Passwort unterscheiden.')

    c.execute(
        'UPDATE users SET password_hash=? WHERE id=?',
        (hash_password(new_password), user['id'])
    )
    c.commit()
    c.close()

    return RedirectResponse('/profile?changed=1', 303)


@app.get('/setup', response_class=HTMLResponse)
def setup_page(request: Request):
    if user_count() > 0:
        return RedirectResponse('/login', 303)
    return templates.TemplateResponse('setup.html', {'request': request, 'error': None})


@app.post('/setup', response_class=HTMLResponse)
def setup(request: Request, username: str = Form(...), password: str = Form(...), password_confirm: str = Form(...)):
    username = username.strip()
    if len(username) < 3 or len(username) > 80:
        return templates.TemplateResponse('setup.html', {'request': request, 'error': 'Der Benutzername muss 3–80 Zeichen lang sein.'}, status_code=400)
    if len(password) < 10:
        return templates.TemplateResponse('setup.html', {'request': request, 'error': 'Das Passwort muss mindestens 10 Zeichen lang sein.'}, status_code=400)
    if password != password_confirm:
        return templates.TemplateResponse('setup.html', {'request': request, 'error': 'Die Passwörter stimmen nicht überein.'}, status_code=400)
    c = db()
    if c.execute('SELECT 1 FROM users LIMIT 1').fetchone():
        c.close(); return RedirectResponse('/login', 303)
    c.execute('INSERT INTO users(username,password_hash) VALUES(?,?)', (username, hash_password(password)))
    c.commit(); c.close()
    return RedirectResponse('/login', 303)



def euros(n):
    return f'{n/100:,.2f} €'.replace(',','X').replace('.',',').replace('X','.')


def month_path(year, month):
    return f'/month/{year}/{month:02d}'


def previous_month(year, month):
    return (year - 1, 12) if month == 1 else (year, month - 1)


def next_month(year, month):
    return (year + 1, 1) if month == 12 else (year, month + 1)


def month_bounds(year: int, month: int) -> tuple[str, str]:
    next_year, next_month_no = next_month(year, month)
    return f'{year:04d}-{month:02d}-01', f'{next_year:04d}-{next_month_no:02d}-01'


def year_bounds(year: int) -> tuple[str, str]:
    return f'{year:04d}-01-01', f'{year + 1:04d}-01-01'

def transaction_redirect_with_error(tx_date: str, message: str):
    try:
        y, m = map(int, str(tx_date).split('-')[:2])
        if not (1 <= m <= 12):
            raise ValueError
    except Exception:
        today = date.today()
        y, m = today.year, today.month
    return RedirectResponse(f'/month/{y}/{m:02d}?error=' + quote(message, safe=''), 303)



def fetch_year_month_transactions(c, year, month=None):
    query = '''
        SELECT t.*, c.name category
        FROM transactions t
        JOIN categories c ON c.id=t.category_id
        WHERE t.tx_date>=? AND t.tx_date<?
    '''
    if month is None:
        start, end = year_bounds(year)
    else:
        start, end = month_bounds(year, month)
    query += ' ORDER BY t.tx_date DESC, t.id DESC'
    return c.execute(query, (start, end)).fetchall()


@app.get('/new-transaction')
def new_transaction():
    today=date.today()
    return RedirectResponse(f'/month/{today.year}/{today.month:02d}',303)


@app.get('/')
def index(request: Request, year: int | None = None):
    y = year or date.today().year
    c = db()

    fixed = c.execute(
        'SELECT * FROM fixed_items WHERE year=? ORDER BY type,name,id',
        (y,)
    ).fetchall()

    start_date, end_date = year_bounds(y)
    transaction_totals = c.execute(
        '''
        SELECT
            CAST(substr(tx_date,6,2) AS INTEGER) month,
            type,
            COALESCE(SUM(amount_cents),0) total
        FROM transactions
        WHERE tx_date>=? AND tx_date<?
        GROUP BY month,type
        ''',
        (start_date, end_date)
    ).fetchall()

    variable = {
        (r['month'], r['type']): r['total']
        for r in transaction_totals
    }

    rows = []
    totals = [0, 0, 0, 0]

    for i, (month_name, col) in enumerate(zip(MONTHS_SHORT, COLS), 1):
        inc = variable.get((i, 'income'), 0)
        exp = variable.get((i, 'expense'), 0)
        fi = sum(r[col] for r in fixed if r['type'] == 'income')
        fe = sum(r[col] for r in fixed if r['type'] == 'expense')

        values = [inc, fi, exp, fe]
        for j, value in enumerate(values):
            totals[j] += value

        rows.append({
            'month': month_name,
            'income': inc,
            'fixed_income': fi,
            'expense': exp,
            'fixed_expense': fe,
            'balance': inc + fi - exp - fe,
        })

    cat_rows = c.execute(
        '''
        SELECT c.name, COALESCE(SUM(t.amount_cents),0) total
        FROM transactions t
        JOIN categories c ON c.id=t.category_id
        WHERE t.type='expense' AND t.tx_date>=? AND t.tx_date<?
        GROUP BY c.id,c.name
        ORDER BY total DESC
        ''',
        (start_date, end_date)
    ).fetchall()
    c.close()

    balance = totals[0] + totals[1] - totals[2] - totals[3]
    annual_income = totals[0] + totals[1]
    annual_expense = totals[2] + totals[3]
    savings_rate = round(balance / annual_income * 100, 1) if annual_income else 0.0
    category_chart = [{'name': r['name'], 'total': r['total']} for r in cat_rows[:10]]

    return templates.TemplateResponse('index.html', {
        'request': request,
        'year': y,
        'months': rows,
        'totals': totals,
        'balance': balance,
        'annual_income': annual_income,
        'annual_expense': annual_expense,
        'savings_rate': savings_rate,
        'category_chart': category_chart,
        'euros': euros,
        'today_month': date.today().month,
        'month_full': MONTHS,
    })


@app.get('/month/{year}/{month}')
def month(request: Request, year:int, month:int, error: str | None = None):
    if month < 1 or month > 12:
        return RedirectResponse(f'/?year={year}',303)
    py,pm=previous_month(year,month)
    ny,nm=next_month(year,month)
    c=db()
    tx=fetch_year_month_transactions(c,year,month)
    cats=c.execute('SELECT * FROM categories WHERE active=1 ORDER BY type,name').fetchall()
    fixed=c.execute('SELECT * FROM fixed_items WHERE year=? ORDER BY type,name,id',(year,)).fetchall()
    c.close()
    inc=sum(t['amount_cents'] for t in tx if t['type']=='income')
    exp=sum(t['amount_cents'] for t in tx if t['type']=='expense')
    fi=sum(r[COLS[month-1]] for r in fixed if r['type']=='income')
    fe=sum(r[COLS[month-1]] for r in fixed if r['type']=='expense')
    available=inc+fi-exp-fe
    return templates.TemplateResponse('month.html',{
        'request':request,'year':year,'month':month,'month_name':MONTHS[month-1],
        'tx':tx,'cats':cats,'income':inc,'expense':exp,'fixed_income':fi,'fixed_expense':fe,
        'available':available,'error':error,'euros':euros,'today_iso':date.today().isoformat(),
        'prev_url':month_path(py,pm),'next_url':month_path(ny,nm),
        'prev_label':f'{MONTHS[pm-1]} {py}','next_label':f'{MONTHS[nm-1]} {ny}'
    })


@app.post('/transaction')
def add_transaction(request: Request, tx_type:str=Form(...),tx_date:str=Form(...),category_id:int=Form(...),amount:str=Form(...),comment:str=Form(''),csrf_token:str=Form('')):
    if not check_csrf(request,csrf_token):
        return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).',status_code=403)
    if tx_type not in {'income','expense'} or not valid_date(tx_date):
        return transaction_redirect_with_error(tx_date,'Bitte überprüfe Datum und Buchungsart.')
    try:
        amount_cents=cents(amount,positive=True)
    except ValueError as exc:
        return transaction_redirect_with_error(tx_date,str(exc))
    c=db()
    cat=c.execute('SELECT type,active FROM categories WHERE id=?',(category_id,)).fetchone()
    if not cat or not cat['active'] or cat['type']!=tx_type:
        c.close()
        return transaction_redirect_with_error(tx_date,'Bitte wähle eine gültige Kategorie.')
    c.execute('INSERT INTO transactions(tx_date,type,category_id,amount_cents,comment) VALUES(?,?,?,?,?)',
              (tx_date,tx_type,category_id,amount_cents,comment.strip() or None))
    c.commit(); c.close()
    y,m=map(int,tx_date.split('-')[:2])
    return RedirectResponse(f'/month/{y}/{m:02d}',303)


@app.post('/transaction/{tx_id}/edit')
def edit_transaction(request: Request, tx_id:int, tx_type:str=Form(...),tx_date:str=Form(...),category_id:int=Form(...),amount:str=Form(...),comment:str=Form(''),csrf_token:str=Form('')):
    if not check_csrf(request,csrf_token):
        return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).',status_code=403)
    if tx_type not in {'income','expense'} or not valid_date(tx_date):
        return transaction_redirect_with_error(tx_date,'Bitte überprüfe Datum und Buchungsart.')
    try:
        amount_cents=cents(amount,positive=True)
    except ValueError as exc:
        return transaction_redirect_with_error(tx_date,str(exc))
    c=db()
    cat=c.execute('SELECT type,active FROM categories WHERE id=?',(category_id,)).fetchone()
    if not cat or not cat['active'] or cat['type']!=tx_type:
        c.close()
        return transaction_redirect_with_error(tx_date,'Bitte wähle eine gültige Kategorie.')
    c.execute('UPDATE transactions SET tx_date=?,type=?,category_id=?,amount_cents=?,comment=? WHERE id=?',
              (tx_date,tx_type,category_id,amount_cents,comment.strip() or None,tx_id))
    c.commit(); c.close()
    y,m=map(int,tx_date.split('-')[:2])
    return RedirectResponse(f'/month/{y}/{m:02d}',303)


@app.post('/transaction/{tx_id}/delete')
def delete_transaction(request: Request, tx_id:int,year:int=Form(...),month:int=Form(...),csrf_token:str=Form('')):
    if not check_csrf(request, csrf_token): return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).', status_code=403)
    c=db(); c.execute('DELETE FROM transactions WHERE id=?',(tx_id,)); c.commit(); c.close(); return RedirectResponse(f'/month/{year}/{month}',303)


@app.get('/fixed')
def fixed_redirect(year:int|None=None): return RedirectResponse(f'/fixed/{year or date.today().year}', 303)

@app.get('/fixed/{year}')
def fixed_page(request:Request, year:int, error:str|None=None):
    c = db()
    items = c.execute(
        'SELECT * FROM fixed_items WHERE year=? ORDER BY type,name,id',
        (year,)
    ).fetchall()
    c.close()
    return templates.TemplateResponse('fixed.html', {
        'request': request,
        'items': items,
        'months': MONTHS_SHORT,
        'cols': COLS,
        'year': year,
        'euros': euros,
        'error': error,
    })

@app.post('/fixed/{year}')
def add_fixed(request: Request, year:int,name:str=Form(...),item_type:str=Form(...),csrf_token:str=Form('')):
    if not check_csrf(request, csrf_token): return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).', status_code=403)
    name=name.strip()
    if not name or item_type not in {'income','expense'}:
        return HTMLResponse('Ungültige Fixkosten-Daten.', status_code=400)
    c=db(); c.execute('INSERT INTO fixed_items(year,name,type) VALUES(?,?,?)',(year,name,item_type)); c.commit(); c.close(); return RedirectResponse(f'/fixed/{year}',303)

@app.post('/fixed/{year}/{item_id}/update')
async def update_fixed(year:int,item_id:int,request:Request):
    f=await request.form()
    if not check_csrf(request, str(f.get('csrf_token', ''))): return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).', status_code=403)
    try:
        vals=[cents(str(f.get(x,'0'))) if str(f.get(x,'')).strip() else 0 for x in COLS]
    except ValueError as exc:
        return RedirectResponse(
            f'/fixed/{year}?error=' + quote(str(exc), safe=''),
            303
        )
    c=db(); c.execute('UPDATE fixed_items SET '+','.join(x+'=?' for x in COLS)+' WHERE id=? AND year=?',(*vals,item_id,year)); c.commit(); c.close(); return RedirectResponse(f'/fixed/{year}',303)

@app.post('/fixed/{year}/{item_id}/edit')
def edit_fixed(request: Request, year:int, item_id:int, name:str=Form(...), item_type:str=Form(...), csrf_token:str=Form('')):
    if not check_csrf(request,csrf_token):
        return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).',status_code=403)
    name=name.strip()
    if not name or item_type not in {'income','expense'}:
        return HTMLResponse('Ungültige Fixkosten-Daten.',status_code=400)
    c=db()
    c.execute('UPDATE fixed_items SET name=?,type=? WHERE id=? AND year=?',(name,item_type,item_id,year))
    c.commit(); c.close()
    return RedirectResponse(f'/fixed/{year}',303)


@app.post('/fixed/{year}/import')
def import_fixed(request: Request, year:int, source_year:int=Form(...), source_month:int=Form(...), target_month:int=Form(...), mode:str=Form(...), csrf_token:str=Form('')):
    if not check_csrf(request,csrf_token):
        return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).',status_code=403)
    if source_month not in range(1,13) or target_month not in range(1,13) or mode not in {'categories','values'}:
        return HTMLResponse('Ungültige Import-Auswahl.',status_code=400)
    source_col=COLS[source_month-1]
    target_col=COLS[target_month-1]
    c = db()
    source = c.execute(
        'SELECT * FROM fixed_items WHERE year=? ORDER BY type,name,id',
        (source_year,)
    ).fetchall()
    existing_rows = c.execute(
        'SELECT * FROM fixed_items WHERE year=?',
        (year,)
    ).fetchall()
    existing_by_key = {
        (row['name'], row['type']): row
        for row in existing_rows
    }

    for row in source:
        key = (row['name'], row['type'])
        existing = existing_by_key.get(key)

        if existing:
            if mode == 'values':
                c.execute(
                    f'UPDATE fixed_items SET {target_col}=? WHERE id=?',
                    (row[source_col], existing['id'])
                )
            continue

        c.execute(
            'INSERT INTO fixed_items(year,name,type) VALUES(?,?,?)',
            (year, row['name'], row['type'])
        )
        new_id = c.execute('SELECT last_insert_rowid()').fetchone()[0]

        if mode == 'values':
            c.execute(
                f'UPDATE fixed_items SET {target_col}=? WHERE id=?',
                (row[source_col], new_id)
            )

        existing_by_key[key] = {'id': new_id}

    c.commit()
    c.close()
    return RedirectResponse(f'/fixed/{year}',303)


@app.post('/fixed/{year}/{item_id}/delete')
def delete_fixed(request: Request, year:int,item_id:int,csrf_token:str=Form('')):
    if not check_csrf(request, csrf_token): return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).', status_code=403)
    c=db(); c.execute('DELETE FROM fixed_items WHERE id=? AND year=?',(item_id,year)); c.commit(); c.close(); return RedirectResponse(f'/fixed/{year}',303)


@app.get('/categories')
def categories(request:Request):
    c=db(); cats=c.execute('SELECT * FROM categories ORDER BY type,name').fetchall(); c.close(); return templates.TemplateResponse('categories.html',{'request':request,'cats':cats})

@app.post('/categories')
def add_category(request: Request, name:str=Form(...), cat_type:str=Form(...), csrf_token:str=Form('')):
    if not check_csrf(request, csrf_token):
        return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).', status_code=403)

    name = name.strip()
    if not name or cat_type not in {'income','expense'}:
        return HTMLResponse('Ungültige Kategorie.', status_code=400)

    c = db()
    duplicate = c.execute(
        'SELECT id FROM categories WHERE lower(name)=lower(?) AND type=? AND active=1',
        (name, cat_type)
    ).fetchone()
    if duplicate:
        c.close()
        return HTMLResponse('Diese Kategorie existiert bereits.', status_code=400)

    c.execute('INSERT INTO categories(name,type) VALUES(?,?)', (name, cat_type))
    c.commit()
    c.close()
    return RedirectResponse('/categories', 303)


@app.post('/categories/{cat_id}/edit')
def edit_category(request: Request, cat_id:int, name:str=Form(...), csrf_token:str=Form('')):
    if not check_csrf(request, csrf_token):
        return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).', status_code=403)

    name = name.strip()
    if not name:
        return HTMLResponse('Der Kategoriename darf nicht leer sein.', status_code=400)

    c = db()
    current = c.execute(
        'SELECT type FROM categories WHERE id=? AND active=1',
        (cat_id,)
    ).fetchone()
    if not current:
        c.close()
        return RedirectResponse('/categories', 303)

    duplicate = c.execute(
        '''
        SELECT id FROM categories
        WHERE id<>? AND lower(name)=lower(?) AND type=? AND active=1
        ''',
        (cat_id, name, current['type'])
    ).fetchone()
    if duplicate:
        c.close()
        return HTMLResponse('Diese Kategorie existiert bereits.', status_code=400)

    c.execute(
        'UPDATE categories SET name=? WHERE id=? AND active=1',
        (name, cat_id)
    )
    c.commit()
    c.close()
    return RedirectResponse('/categories', 303)


@app.post('/categories/{cat_id}/delete')
def delete_category(request: Request, cat_id:int, csrf_token:str=Form('')):
    if not check_csrf(request, csrf_token):
        return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).', status_code=403)

    c = db()
    transaction_refs = c.execute(
        'SELECT COUNT(*) n FROM transactions WHERE category_id=?',
        (cat_id,)
    ).fetchone()['n']
    budget_refs = c.execute(
        'SELECT COUNT(*) n FROM budgets WHERE category_id=?',
        (cat_id,)
    ).fetchone()['n']

    # Referenzierte Kategorien deaktivieren statt historische Daten/Budgets zu beschädigen.
    if transaction_refs or budget_refs:
        c.execute('UPDATE categories SET active=0 WHERE id=?', (cat_id,))
    else:
        c.execute('DELETE FROM categories WHERE id=?', (cat_id,))

    c.commit()
    c.close()
    return RedirectResponse('/categories', 303)


@app.get('/analysis')
def analysis(
    request: Request,
    year: int | None = None,
    category_id: int | None = None,
    n: int = 10000,
    k: int = 5
):
    y = year or date.today().year
    n = max(100, min(int(n), 100000))
    k = max(1, min(int(k), 20))

    c = db()
    rows = fetch_year_month_transactions(c, y)
    cats = c.execute('SELECT * FROM categories WHERE active=1 ORDER BY type,name').fetchall()
    c.close()

    # Die Analyse echter Fintra-Daten bezieht sich vollständig auf das gewählte Jahr.
    idx = TransactionIndex(rows)

    # ---------------------------------------------------------
    # 1) Hash Map vs. lineare Suche – echte Fintra-Daten
    # ---------------------------------------------------------
    if cats:
        selected_cat = next((cat for cat in cats if cat['id'] == category_id), cats[0])
        selected_category_id = selected_cat['id']
        selected_category_name = selected_cat['name']
    else:
        selected_category_id = None
        selected_category_name = 'Keine Kategorie'

    linear_comparisons = 0
    linear_matches = 0
    if selected_category_id is not None:
        for row in rows:
            linear_comparisons += 1
            if row['category_id'] == selected_category_id:
                linear_matches += 1
        hash_matches = idx.category_count(selected_category_id)
    else:
        hash_matches = 0

    # ---------------------------------------------------------
    # 2) Sliding Window – O(n)
    # ---------------------------------------------------------
    monthly = []
    for month_no in range(1, 13):
        total = sum(
            r['amount_cents']
            for r in rows
            if r['type'] == 'expense' and int(r['tx_date'][5:7]) == month_no
        )
        monthly.append(total)

    rolling = []
    window_size = 3
    running_sum = 0
    for i, value in enumerate(monthly):
        running_sum += value
        if i >= window_size:
            running_sum -= monthly[i - window_size]
        current_size = min(i + 1, window_size)
        rolling.append(round(running_sum / current_size) if current_size else 0)

    # ---------------------------------------------------------
    # 3) Top-K mit Min-Heap – O(n log k)
    # ---------------------------------------------------------
    by_cat = {}
    for row in rows:
        if row['type'] == 'expense':
            by_cat[row['category']] = by_cat.get(row['category'], 0) + row['amount_cents']

    heap = []
    heap_operations = 0
    for name, total in by_cat.items():
        item = (total, name)
        if len(heap) < k:
            heapq.heappush(heap, item)
            heap_operations += 1
        elif total > heap[0][0]:
            heapq.heapreplace(heap, item)
            heap_operations += 1

    top = sorted(heap, reverse=True)

    # Vergleich: vollständige Sortierung aller aggregierten Kategorien.
    sorted_top = sorted(
        ((total, name) for name, total in by_cat.items()),
        reverse=True
    )[:k]

    # ---------------------------------------------------------
    # 4) IQR-Ausreißer – O(n log n)
    # ---------------------------------------------------------
    expense_amounts = sorted(
        r['amount_cents'] for r in rows if r['type'] == 'expense'
    )

    q1 = q3 = iqr = upper = 0
    outliers = []
    if len(expense_amounts) >= 4:
        lower_half = expense_amounts[:len(expense_amounts)//2]
        upper_half = expense_amounts[(len(expense_amounts)+1)//2:]
        q1 = statistics.median(lower_half)
        q3 = statistics.median(upper_half)
        iqr = q3 - q1
        upper = q3 + 1.5 * iqr
        outliers = [
            r for r in rows
            if r['type'] == 'expense' and r['amount_cents'] > upper
        ][:8]

    # ---------------------------------------------------------
    # 5) Synthetischer Benchmark – nur RAM, niemals Datenbank
    # ---------------------------------------------------------
    rng = random.Random(42)
    synthetic_categories = 20
    synthetic = [
        (rng.randrange(1, synthetic_categories + 1), rng.randrange(100, 100000))
        for _ in range(n)
    ]
    target_category = 7

    # Lineare Suche
    start_ns = time.perf_counter_ns()
    synthetic_linear_matches = 0
    synthetic_linear_comparisons = 0
    for cid, _amount in synthetic:
        synthetic_linear_comparisons += 1
        if cid == target_category:
            synthetic_linear_matches += 1
    linear_ns = time.perf_counter_ns() - start_ns

    # Hash-Index: Aufbau O(n), Lookup durchschnittlich O(1)
    start_ns = time.perf_counter_ns()
    synthetic_index = {}
    for pos, (cid, _amount) in enumerate(synthetic):
        synthetic_index.setdefault(cid, []).append(pos)
    hash_build_ns = time.perf_counter_ns() - start_ns

    start_ns = time.perf_counter_ns()
    synthetic_hash_matches = len(synthetic_index.get(target_category, []))
    hash_lookup_ns = time.perf_counter_ns() - start_ns

    # Top-K-Vergleich über alle n synthetischen Transaktionen.
    # Damit beziehen sich Messung und Big-O-Angabe tatsächlich auf denselben Datenumfang.
    start_ns = time.perf_counter_ns()
    synthetic_sorted_top = sorted(
        enumerate(synthetic),
        key=lambda item: item[1][1],
        reverse=True
    )[:k]
    sort_ns = time.perf_counter_ns() - start_ns

    start_ns = time.perf_counter_ns()
    synthetic_heap = []
    synthetic_heap_ops = 0
    for pos, (_cid, amount) in enumerate(synthetic):
        item = (amount, pos)
        if len(synthetic_heap) < k:
            heapq.heappush(synthetic_heap, item)
            synthetic_heap_ops += 1
        elif amount > synthetic_heap[0][0]:
            heapq.heapreplace(synthetic_heap, item)
            synthetic_heap_ops += 1
    synthetic_heap_top = sorted(synthetic_heap, reverse=True)
    heap_ns = time.perf_counter_ns() - start_ns

    # Grobe theoretische Operationsgrößen zur Veranschaulichung der Skalierung.
    sort_work = round(n * math.log2(max(n, 2)))
    heap_work = round(n * math.log2(max(k, 2)))

    sorted_ids = {pos for pos, _row in synthetic_sorted_top}
    heap_ids = {pos for _amount, pos in synthetic_heap_top}

    benchmark = {
        'n': n,
        'k': k,
        'linear_matches': synthetic_linear_matches,
        'hash_matches': synthetic_hash_matches,
        'linear_comparisons': synthetic_linear_comparisons,
        'linear_us': linear_ns / 1000,
        'hash_build_us': hash_build_ns / 1000,
        'hash_lookup_us': hash_lookup_ns / 1000,
        'sort_us': sort_ns / 1000,
        'heap_us': heap_ns / 1000,
        'heap_ops': synthetic_heap_ops,
        'sort_work': sort_work,
        'heap_work': heap_work,
        'same_search_result': synthetic_linear_matches == synthetic_hash_matches,
        'same_top_result': sorted_ids == heap_ids,
    }

    # Budgetstatus wie bisher.
    current_month = date.today().month if y == date.today().year else 1
    c = db()
    budgets = c.execute(
        'SELECT b.*,c.name FROM budgets b JOIN categories c ON c.id=b.category_id '
        'WHERE b.year=? AND b.month=? ORDER BY c.name',
        (y, current_month)
    ).fetchall()
    c.close()

    spent_by = {}
    for row in rows:
        if row['type'] == 'expense' and int(row['tx_date'][5:7]) == current_month:
            spent_by[row['category']] = spent_by.get(row['category'], 0) + row['amount_cents']

    budget_rows = [
        {
            'name': b['name'],
            'budget': b['amount_cents'],
            'spent': spent_by.get(b['name'], 0),
            'pct': round(spent_by.get(b['name'], 0) / b['amount_cents'] * 100)
                   if b['amount_cents'] else 0
        }
        for b in budgets
    ]

    return templates.TemplateResponse('analysis.html', {
        'request': request,
        'year': y,
        'months_full': MONTHS,
        'monthly': monthly,
        'rolling': rolling,
        'top': top,
        'sorted_top': sorted_top,
        'heap_operations': heap_operations,
        'outliers': outliers,
        'q1': q1,
        'q3': q3,
        'iqr': iqr,
        'upper': upper,
        'euros': euros,
        'budget_rows': budget_rows,
        'current_month_name': MONTHS[current_month - 1],
        'index_categories': len(idx.by_category),
        'transaction_count': len(rows),
        'cats': cats,
        'selected_category_id': selected_category_id,
        'selected_category_name': selected_category_name,
        'linear_comparisons': linear_comparisons,
        'linear_matches': linear_matches,
        'hash_matches': hash_matches,
        'benchmark': benchmark,
        'k': k,
    })


@app.get('/budgets')
def budgets_page(request:Request, year:int|None=None, month:int|None=None, error:str|None=None):
    y=year or date.today().year
    m=month or date.today().month
    if m<1 or m>12:
        return RedirectResponse(f'/budgets?year={y}&month={date.today().month}',303)
    c=db()
    cats=c.execute("SELECT * FROM categories WHERE active=1 AND type='expense' ORDER BY name").fetchall()
    existing={r['category_id']:r for r in c.execute('SELECT * FROM budgets WHERE year=? AND month=?',(y,m)).fetchall()}
    start_date, end_date = month_bounds(y, m)
    spent = {
        r['category_id']: r['total']
        for r in c.execute(
            '''
            SELECT category_id,COALESCE(SUM(amount_cents),0) total
            FROM transactions
            WHERE type='expense' AND tx_date>=? AND tx_date<?
            GROUP BY category_id
            ''',
            (start_date, end_date)
        ).fetchall()
    }
    c.close()
    progress={}
    for cat in cats:
        budget=existing[cat['id']]['amount_cents'] if cat['id'] in existing else 0
        used=spent.get(cat['id'],0)
        pct=round(used/budget*100) if budget else 0
        progress[cat['id']]={'spent':used,'budget':budget,'remaining':max(0,budget-used),'pct':pct}
    return templates.TemplateResponse('budgets.html',{
        'request':request,'year':y,'month':m,'month_name':MONTHS[m-1],
        'cats':cats,'existing':existing,'progress':progress,'euros':euros,'error':error
    })


@app.post('/budgets/{year}/{month}')
async def save_budgets(year:int,month:int,request:Request):
    if month < 1 or month > 12:
        return RedirectResponse(f'/budgets?year={year}&month={date.today().month}&error=' + quote('Ungültiger Monat.', safe=''), 303)
    form=await request.form()
    if not check_csrf(request, str(form.get('csrf_token', ''))): return HTMLResponse('Ungültige Anfrage (CSRF-Schutz).', status_code=403)
    c = db()
    valid_category_ids = {
        row['id']
        for row in c.execute(
            "SELECT id FROM categories WHERE active=1 AND type='expense'"
        ).fetchall()
    }

    for key, val in form.items():
        if not key.startswith('budget_'):
            continue

        try:
            cid = int(key.split('_', 1)[1])
            amount = cents(str(val)) if str(val).strip() else 0
        except (ValueError, IndexError) as exc:
            c.close()
            return RedirectResponse(
                f'/budgets?year={year}&month={month}&error=' + quote(str(exc), safe=''),
                303
            )

        if cid not in valid_category_ids:
            c.close()
            return RedirectResponse(
                f'/budgets?year={year}&month={month}&error=' +
                quote('Ungültige Budget-Kategorie.', safe=''),
                303
            )

        c.execute(
            '''
            INSERT INTO budgets(year,month,category_id,amount_cents)
            VALUES(?,?,?,?)
            ON CONFLICT(year,month,category_id)
            DO UPDATE SET amount_cents=excluded.amount_cents
            ''',
            (year, month, cid, amount)
        )

    c.commit()
    c.close()
    return RedirectResponse(f'/budgets?year={year}&month={month}', 303)


@app.get('/export/transactions.csv')
def export_transactions_csv(year:int|None=None):
    c=db()
    if year:
        start_date, end_date = year_bounds(year)
        rows = c.execute(
            '''
            SELECT t.tx_date,t.type,c.name category,t.amount_cents,t.comment
            FROM transactions t
            JOIN categories c ON c.id=t.category_id
            WHERE t.tx_date>=? AND t.tx_date<?
            ORDER BY t.tx_date,t.id
            ''',
            (start_date, end_date)
        ).fetchall()
    else:
        rows=c.execute(
            "SELECT t.tx_date,t.type,c.name category,t.amount_cents,t.comment "
            "FROM transactions t JOIN categories c ON c.id=t.category_id ORDER BY t.tx_date,t.id"
        ).fetchall()
    c.close()
    out=io.StringIO()
    writer=csv.writer(out,delimiter=';')
    writer.writerow(['Datum','Typ','Kategorie','Betrag_EUR','Kommentar'])
    for r in rows:
        writer.writerow([r['tx_date'],r['type'],r['category'],f"{r['amount_cents']/100:.2f}".replace('.',','),r['comment'] or ''])
    suffix=f'-{year}' if year else ''
    return Response(out.getvalue(),media_type='text/csv; charset=utf-8',
                    headers={'Content-Disposition':f'attachment; filename="fintra-transaktionen{suffix}.csv"'})


@app.get('/backup/database')
def backup_database():
    fd,path=tempfile.mkstemp(prefix='fintra-backup-',suffix='.db')
    os.close(fd)
    source=db()
    target=sqlite3.connect(path)
    source.backup(target)
    target.close()
    source.close()
    return FileResponse(
        path,
        media_type='application/octet-stream',
        filename=f'fintra-backup-{date.today().isoformat()}.db',
        background=BackgroundTask(lambda: os.path.exists(path) and os.unlink(path)),
    )


@app.get('/algorithm')
def algorithm(request:Request):
    return templates.TemplateResponse('algorithm.html',{'request':request})
