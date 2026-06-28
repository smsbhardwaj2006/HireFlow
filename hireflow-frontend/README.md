# HireFlow — Frontend Prototype

A frontend prototype of **HireFlow**, a College Placement Management System with three separate portals (Student, Company, Placement Officer). Built with plain **HTML, CSS, and JavaScript** — no frameworks, no build step. Open `index.html` in a browser to start.

> **Status:** Frontend-only prototype. The PRD specs a Django backend with SQLite (dev) / MySQL (production) — that's the next phase. All data (students, companies, jobs, applications, interviews) lives in browser `localStorage`, seeded with demo data on first load.

## Demo logins

Three separate login pages, one per role — pre-filled with working demo credentials:

| Role | Page | Email | Password |
|---|---|---|---|
| Student | `login-student.html` | ananya@college.edu | demo1234 |
| Company | `login-company.html` | hr@nexora.com | demo1234 |
| Placement Officer | `login-officer.html` | officer@college.edu | demo1234 |

Each role's session is tracked separately, so you can open three browser tabs (or three incognito windows) and be logged in as all three roles simultaneously to see the full flow — e.g. apply as a student in one tab, shortlist that application as the company in another, then check the officer's report in a third.

## What's implemented

**Public:** Home (with role selection), About, Contact, 3 login pages, 2 registration pages (Student, Company — officers aren't self-registered per the PRD)

**Student portal (8 pages):** Dashboard, Profile (editable + skills tags), Resume upload, Job listings (search/filter/eligibility), Job detail + apply, My Applications (visual status pipeline), Interview schedule, Notifications

**Company portal (6 pages):** Dashboard, Company profile, Manage jobs (add/edit/delete via modal), View applicants (advance/reject), Interview scheduling, Offer letters / result publishing

**Officer portal (6 pages):** Dashboard, Manage students (add/edit/delete), Manage companies (approve/remove), Placement drives (create/edit/delete), Reports (department-wise + company-wise stats), Send notifications

## The signature interaction

`student-applications.html` (and the dashboard) render a **status pipeline** — Applied → Review → Shortlisted → Interview → Selected, with a branch to Rejected — built in `js/app.js`'s `UI.statusPipelineHTML()`. This is the one piece of UI unique to this PRD's domain (vs. e.g. an e-commerce order status).

## What's intentionally not real yet

- No backend, no real database — `js/data.js` hardcodes the initial dataset
- "Resume upload" stores only the filename, not an actual file (no backend to persist it to)
- Three roles share `localStorage` in the same browser — in production, a Django backend with real authentication would isolate this properly per real user, not per browser
- Admin/company "approve", "advance", "schedule" actions are all real in the sense that they update localStorage and the UI reflects it — but none of this persists to a server

## Folder structure

```
hireflow/
├── index.html                  Home (role selection)
├── about.html / contact.html
├── login-student/company/officer.html
├── register-student/company.html
├── student-*.html               8 student portal pages
├── company-*.html                6 company portal pages
├── officer-*.html                 6 officer portal pages
├── css/style.css                   All styling
└── js/
    ├── data.js          Mock data: students, companies, jobs, drives, applications, interviews, notifications
    ├── app.js           Store (localStorage), Auth (3-role login), Jobs/Applications helpers, UI utilities
    └── sidebar.js       Shared dashboard sidebar, role-gated via Auth.requireRole()
```

## Running it

```bash
# Just open index.html in a browser, or for a local server:
python -m http.server 8000
# then visit http://localhost:8000
```

## Next steps (per PRD)

1. Build Django backend: Student, Company, PlacementDrive, Job, Application, Interview, Notification models
2. Real authentication with password hashing and role-based permissions (not shared localStorage)
3. Real resume file upload/storage (Django's `FileField` + media handling)
4. Replace `js/data.js` mock calls with `fetch()` calls to the real API
5. Deploy: frontend → Vercel/Netlify, backend → Railway/Render (same pattern as the ShopSphere project)
