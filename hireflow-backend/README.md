# HireFlow — Backend (Django REST Framework + SQLite/MySQL)

Implements the PRD's backend: three separate login flows (Student, Company, Officer), job postings with eligibility filtering, the full application status pipeline, interview scheduling, and officer reports — backed by SQLite locally and MySQL in production, exactly as the PRD specifies.

## ⚠️ How this was built — please read before assuming it's fully verified

Like the ShopSphere backend, this was written without a live Django environment to test against (no network access in the build sandbox to `pip install`). Every file passed a **Python syntax check** and I manually traced **every cross-app import** to confirm there's no circular dependency (the import graph here is more complex than ShopSphere's, since officer endpoints touch four other apps' models). That's a real check, but it's not the same as having actually run the server. Run through the setup steps below and treat any first-run errors as normal, not a sign something is fundamentally broken.

## The one big design decision worth understanding cold

**Student, Company, and Officer are three separate Django models — not one User model with a role field.** This was a deliberate choice (you can see the reasoning in `students/models.py`'s docstring) to match how the PRD itself describes them: genuinely different entities with different fields (a Company has no CGPA, a Student has no website), not the same thing wearing different hats.

The cost: Django REST Framework and SimpleJWT both assume one `AUTH_USER_MODEL`. The fix is in `config/authentication.py` — every JWT carries a custom `role` claim set at login, and a custom authentication class reads that claim to know whether to look the token up in the Student, Company, or Officer table. `AUTH_USER_MODEL` is technically set to `officers.Officer` (Django's admin needs it to point somewhere), but that's a technicality for `/admin/` to work — it doesn't make Officer "the" real user model. This is the single most likely thing an interviewer asks about, so it's worth being able to explain in your own words, not just point at the code.

## Setup (local development — SQLite, zero config)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Defaults work as-is for local dev — DJANGO_ENV=development uses SQLite automatically

python manage.py makemigrations
python manage.py migrate

# Officers aren't self-registered (see students/models.py docstring) —
# create one interactively:
python manage.py create_officer

# Optional: seed demo students/companies/jobs matching the frontend's demo data
python manage.py seed_demo_data

python manage.py runserver
```

API is now at `http://localhost:8000/api/`. Django admin (officer login only) at `http://localhost:8000/admin/`.

## Switching to MySQL (production)

Set `DJANGO_ENV=production` in `.env` and fill in `DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT` (or `DATABASE_URL` if your host provides one, e.g. Railway). No code changes needed — `config/settings.py` branches on `DJANGO_ENV` to pick the right database engine, which is exactly the PRD's stated success criterion: *"Can be deployed locally with SQLite and migrated to MySQL for production without major code changes."*

## Running tests

```bash
python manage.py test
```

Tests focus on the two highest-risk areas in a three-model auth design: `students/tests.py` covers registration/login and confirms a student's JWT genuinely can't access officer-only endpoints (role-mismatch is the main new failure mode this architecture introduces vs. ShopSphere's single-User model). `applications/tests.py` covers the apply/eligibility logic and — importantly — confirms Company A can never update Company B's applications, even by guessing an application ID.

## API Endpoints

### Students
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/students/register` | — | Register |
| POST | `/api/students/login` | — | JWT login |
| GET/PUT | `/api/students/profile` | student | Own profile |
| POST/DELETE | `/api/students/resume` | student | Upload/remove resume |

### Companies
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/companies/register` | — | Register (status starts "pending") |
| POST | `/api/companies/login` | — | JWT login |
| GET/PUT | `/api/companies/profile` | company | Own profile |

### Officers
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/officers/login` | — | JWT login (no self-registration — see `create_officer` command) |
| GET | `/api/officers/profile` | officer | Own profile |
| GET | `/api/officers/dashboard-stats` | officer | Total students/companies/applications/placement rate |
| GET | `/api/officers/reports` | officer | Department-wise + company-wise reports |

### Officer-only admin
| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/admin/students` | List all students / manually add one |
| GET/PUT/DELETE | `/api/admin/students/{id}` | Manage one student |
| GET | `/api/admin/companies` | List all companies |
| GET/PUT/DELETE | `/api/admin/companies/{id}` | Manage one company |
| POST | `/api/admin/companies/{id}/approve` | Approve a pending company |

### Jobs
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/jobs` | any | List (students: `?eligible_only=true` filters to jobs they qualify for) |
| POST | `/api/jobs` | company | Create (always under your own company) |
| GET/PUT/DELETE | `/api/jobs/{id}` | company (own) | Manage one job |
| GET | `/api/jobs/mine` | company | All your own jobs |

### Applications
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/applications` | student | Apply to a job (checks eligibility + resume) |
| GET | `/api/applications/mine` | student | Your own applications |
| GET | `/api/applications/for-company` | company | All applications across your jobs |
| PUT | `/api/applications/{id}/status` | company (owns the job) | Advance/reject |

### Interviews
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/interviews` | company | Schedule (also advances application status) |
| GET | `/api/interviews/mine` | student | Your own interviews |
| GET | `/api/interviews/for-company` | company | All interviews you've scheduled |
| GET/PUT | `/api/interviews/{id}` | company (owns it) | View/edit |

### Notifications
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/notifications` | any logged-in role | List announcements |
| POST | `/api/notifications` | officer | Send a new announcement |

All protected routes: `Authorization: Bearer <access_token>` header, token obtained from the relevant `/login` endpoint.

## Other design decisions worth knowing for an interview

- **Why `Job.is_eligible_for()` is a model method, not logic duplicated in views:** both the job-listing endpoint (`?eligible_only=true`) and the apply endpoint need the exact same eligibility check — keeping it in one place means they can't silently drift apart.
- **Why `ApplyToJobView` re-checks resume + eligibility server-side** even though the frontend prototype already checks this in the UI: client-side checks are a UX nicety, not a security boundary — anyone can call the API directly with curl/Postman, so the real check has to live here.
- **Why scheduling an interview also updates the application's status** (in one `transaction.atomic()` block, `interviews/views.py`): same reasoning as ShopSphere's order-placement transaction — these two writes represent one real-world event (the candidate is now in the interview stage) and should never partially succeed.
- **Why Officer is the one model that subclasses `AbstractBaseUser`** while Student/Company don't: see `officers/models.py`'s docstring — purely so Django's `/admin/` and permission framework, which need exactly one `AUTH_USER_MODEL`, have somewhere valid to point.

## Folder structure

```
hireflow-backend/
├── manage.py
├── requirements.txt / .env.example
├── config/
│   ├── settings.py        SQLite/MySQL switch via DJANGO_ENV
│   ├── authentication.py  MultiRoleJWTAuthentication — the key file
│   ├── tokens.py           Shared helper to issue role-tagged JWTs
│   └── urls.py
├── students/      Student model, own profile + resume upload, officer-admin CRUD
├── companies/     Company model (status: pending/approved), own profile, officer-admin CRUD + approve
├── officers/      Officer model (AUTH_USER_MODEL), login, dashboard stats, reports
├── jobs/          Job model with eligibility fields, eligibility-aware listing
├── applications/  Application model — the 6-state status pipeline
├── interviews/    Interview model, scheduling (atomic with status update)
└── notifications/ Notification model, officer broadcasts
```

## Connecting the frontend

Same situation as ShopSphere: `hireflow-frontend`'s `js/app.js` currently simulates all of this in `localStorage`. Wiring them together means replacing `Store`/`Auth`/`Jobs`/`Applications` calls in the frontend with `fetch()` calls to these endpoints, and storing the JWT (plus its role) instead of the fake session object. Not done in this zip — a reasonable next step once you've confirmed this backend runs on its own.
