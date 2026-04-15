# Grand Nirwana Hotel — Property Management System

> A full-featured hotel PMS built with Django + HTMX. Manages reservations, front desk, billing, housekeeping, POS, and reports.

---

## 🗺️ Quick Map — Where Is Everything?

```
0xManta/
│
├── apps/                   ← All business logic lives here
│   ├── core/               ← Shared tools used by every app
│   │   ├── models.py       ← BaseModel (UUID, timestamps, soft-delete)
│   │   ├── mixins.py       ← Role-based access control (RBAC)
│   │   ├── utils.py        ← Format currency, generate invoice numbers
│   │   ├── middleware.py   ← Sets hotel timezone per request
│   │   ├── context_processors.py ← Injects hotel_name into every template
│   │   └── templatetags/manta_tags.py ← {{ amount|idr }}, status badges
│   │
│   ├── accounts/           ← Staff login, user model, roles
│   ├── rooms/              ← Room types, room status management
│   ├── guests/             ← Guest profiles and history
│   ├── reservations/       ← Bookings, calendar, availability check
│   ├── frontdesk/          ← Check-in, check-out, walk-in operations
│   ├── billing/            ← Folio, charges, payments, PB1 tax
│   ├── housekeeping/       ← Room cleaning tasks and board
│   ├── inventory/          ← Stock management, auto-deduction
│   ├── pos/                ← Point of Sale terminal for F&B
│   └── reports/            ← Occupancy, revenue, tax reports
│
├── templates/              ← HTML files (one folder per app)
├── static/                 ← CSS, JS, fonts (all served locally, no CDN)
│   ├── css/app.css         ← Grand Nirwana brand styles (teal #14b8a6)
│   ├── js/app.js           ← Loading bar, error handler, toast system
│   └── fonts/              ← Inter + Poppins (downloaded locally)
│
├── manta/
│   ├── settings.py         ← All configuration in one place
│   └── urls.py             ← Root URL routing
│
└── .env                    ← Your secrets (never commit this!)
```

---

## 🚀 Running the App (First Timer)

**Step 1 — Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

**Step 2 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3 — Set up your environment**
```bash
# Copy the example and edit it
copy .env.example .env
```

**Step 4 — Run database migrations**
```bash
python manage.py migrate
```

**Step 5 — Create your first admin user**
```bash
python manage.py createsuperuser
```

**Step 6 — Load sample data (optional)**
```bash
python manage.py seed_demo
```

**Step 7 — Start the server**
```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 — you're in!

---

## ⚙️ Configuration (.env file)

All settings you'll ever need to change:

| Variable | What it does | Example |
|---|---|---|
| `SECRET_KEY` | Django's security key — change for production! | `your-long-random-string` |
| `DEBUG` | Shows error pages. Set `False` in production | `True` |
| `HOTEL_NAME` | Displayed everywhere in the UI | `Grand Nirwana Hotel` |
| `HOTEL_TAX_RATE` | PB1 hotel tax percentage | `10` |
| `HOTEL_SERVICE_CHARGE` | Service charge percentage | `11` |
| `TIMEZONE` | Hotel's timezone | `Asia/Pontianak` |
| `DB_PASSWORD` | Leave empty to use SQLite (local dev) | (your Supabase password) |

---

## 🏗️ How the App is Structured (Architecture)

Every Django app follows the same simple pattern:

```
models.py   ← What data we store (database tables)
views.py    ← What happens when a URL is visited
forms.py    ← Form validation rules
urls.py     ← Which URL calls which view
admin.py    ← Django admin panel configuration
```

### The Data Flow

```
Browser → URL → View → Model → Database
                  ↓
              Template (HTML)
```

### Key Design Decisions

1. **All models inherit from `BaseModel`** (`apps/core/models.py`)
   - Every table gets: UUID primary key, `created_at`, `updated_at`, soft delete
   - Soft delete = records are hidden, not actually deleted (safer for hotels)

2. **Role-based access control via Mixins** (`apps/core/mixins.py`)
   - Add `FrontDeskMixin` to a view → only Owner/Manager/Receptionist can access
   - Add `OwnerManagerMixin` → only Owner and Manager
   - This is enforced server-side, not just in the UI

3. **HTMX for fast page updates** (`static/js/htmx.min.js`)
   - Links and forms update parts of the page without a full reload
   - This is why navigation feels fast

4. **Zero CDN dependencies** — all JS, CSS, and fonts are local files
   - Works without internet after first setup
   - No GDPR issues from Google Fonts tracking

---

## 👮 Security Overview

This app has enterprise-level security built in. Here's what's protecting it:

### Access Control
- Every protected view uses a mixin from `apps/core/mixins.py`
- **Never remove a mixin from a view without understanding what it protects**
- Superusers can access everything — only give superuser to the owner

### Roles
| Role | Can Do |
|---|---|
| **Owner** | Everything |
| **Manager** | Everything except system settings |
| **Receptionist** | Front desk, reservations, billing |
| **Housekeeping** | Only housekeeping board |
| **POS Staff** | Only POS terminal |

Assign roles via Django Admin → Users → Groups.

### Security Headers (Production Only)
When `DEBUG=False`, these are automatically enabled:
- HTTPS redirect (SSL required)
- HSTS (browsers remember to always use HTTPS)
- XSS filter, CSRF protection
- Clickjacking prevention
- Secure cookies (HTTPONLY + SECURE)

### Database
- UUIDs as primary keys (no sequential IDs that attackers can guess)
- Soft delete (records can be recovered if deleted by mistake)
- All queries use Django ORM (no raw SQL = no SQL injection risk)

### Passwords
- Minimum 8 characters enforced
- Common passwords blocked
- Bcrypt hashing (Django default)

---

## 🔄 Common Maintenance Tasks

### Adding a New Staff Member
1. Go to Django Admin (`/admin/`)
2. Users → Add User
3. Set first name, last name, username, password
4. Add to the correct Group (Role)

### Changing the Hotel Name
Edit `.env`:
```
HOTEL_NAME=Your New Hotel Name
```
Restart the server. No code changes needed.

### Changing Tax Rate
Edit `.env`:
```
HOTEL_TAX_RATE=10   # Percentage (e.g., 10 = 10%)
```

### Deploying to Production
```bash
# 1. Set DEBUG=False in .env
# 2. Collect static files
python manage.py collectstatic --noinput
# 3. Run migrations
python manage.py migrate
# 4. Restart the server/gunicorn
```

### Adding a Room Type or Room
1. Django Admin → Room Types → Add
2. Django Admin → Rooms → Add
3. Or use the UI at `/rooms/`

---

## 🐛 Troubleshooting

### "Page not loading" / Loading bar stuck
- Check the terminal for error messages
- Common cause: database connection issue
- Check your `.env` DB settings

### "403 Forbidden"
- The logged-in user doesn't have the right role/group
- Go to Admin → Users → edit the user → add them to the correct Group

### "500 Internal Server Error"
- Set `DEBUG=True` temporarily to see the full error
- Check the terminal output — the error is always printed there
- **Remember to set `DEBUG=False` again after fixing!**

### Migrations error
```bash
python manage.py migrate --run-syncdb
```

### Static files not loading (production)
```bash
python manage.py collectstatic --noinput --clear
```

---

## 📊 Apps Reference

| App | URL prefix | What it does |
|---|---|---|
| `accounts` | `/accounts/` | Login, logout, profile |
| `dashboard` | `/` | Overview stats and charts |
| `rooms` | `/rooms/` | Room list, grid, management |
| `guests` | `/guests/` | Guest profiles and search |
| `reservations` | `/reservations/` | Bookings, calendar |
| `frontdesk` | `/frontdesk/` | Check-in/out, walk-in |
| `billing` | `/billing/` | Folios, charges, payments |
| `housekeeping` | `/housekeeping/` | Cleaning task board |
| `inventory` | `/inventory/` | Stock management |
| `pos` | `/pos/` | F&B Point of Sale |
| `reports` | `/reports/` | Revenue, occupancy, tax |

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Language |
| Django | 4.x | Web framework |
| HTMX | 2.0 | Partial page updates (no full reload) |
| Alpine.js | 3.x | Small UI interactions (dropdowns, toggles) |
| DaisyUI + Tailwind | Latest | CSS components |
| Lucide Icons | Latest | Icons |
| WhiteNoise | 6.x | Serves static files efficiently |
| PostgreSQL / SQLite | — | Database (Supabase in production) |

---

## 🤝 Contributing (How to Make Changes Safely)

### Before making any change:
1. Test locally first (`DEBUG=True`)
2. Never edit migration files manually
3. If you add a field to a model, run `python manage.py makemigrations` then `python manage.py migrate`
4. Keep comments — they explain the "why", not just the "what"

### If you add a new view:
- Add the appropriate role mixin (never leave a view unprotected)
- Add a URL in `urls.py`
- Create the template in `templates/<app_name>/`

### If you add a new model field:
```bash
python manage.py makemigrations <app_name>
python manage.py migrate
```

### Code style rules:
- Every file starts with a docstring explaining what it does
- Every class and function has a docstring
- Use `select_related()` and `prefetch_related()` when querying related objects
- Never use `.objects.get()` in a loop — use `.filter(pk__in=ids)` instead

---

## 📞 Contact / Reporting Issues

Hotel: **Grand Nirwana Hotel**  
Address: Jl. Teuku Umar No. 39, Pontianak Kota, Kalimantan Barat 78117  
Phone: +62 561 555 888  
Email: info@grandnirwana.com

---

*Built with ❤️ for Grand Nirwana Hotel — Pontianak, Kalimantan Barat*
