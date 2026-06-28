/* ==========================================================================
   HireFlow — App Core
   localStorage simulates the backend described in the PRD (Django + SQLite/
   MySQL). Three roles share this same demo-auth pattern: student, company,
   officer — each stored separately so logging in as one doesn't clash
   with another role's session in the same browser.
   ========================================================================== */

const Store = {
  KEYS: {
    SESSION: "hireflow_session",            // { role, id }
    STUDENTS: "hireflow_students",
    COMPANIES: "hireflow_companies",
    JOBS: "hireflow_jobs",
    DRIVES: "hireflow_drives",
    APPLICATIONS: "hireflow_applications",
    INTERVIEWS: "hireflow_interviews",
    NOTIFICATIONS: "hireflow_notifications",
    REGISTERED_USERS: "hireflow_registered_users", // {email, password, role, refId}
  },

  get(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch (e) {
      return fallback;
    }
  },
  set(key, value) { localStorage.setItem(key, JSON.stringify(value)); },

  // Lazily seed demo data into localStorage on first visit, then always
  // read/write from localStorage after that (so admin edits persist).
  ensureSeeded() {
    if (!localStorage.getItem(this.KEYS.STUDENTS)) this.set(this.KEYS.STUDENTS, DEMO_STUDENTS);
    if (!localStorage.getItem(this.KEYS.COMPANIES)) this.set(this.KEYS.COMPANIES, COMPANIES);
    if (!localStorage.getItem(this.KEYS.JOBS)) this.set(this.KEYS.JOBS, JOBS);
    if (!localStorage.getItem(this.KEYS.DRIVES)) this.set(this.KEYS.DRIVES, DRIVES);
    if (!localStorage.getItem(this.KEYS.APPLICATIONS)) this.set(this.KEYS.APPLICATIONS, DEMO_APPLICATIONS);
    if (!localStorage.getItem(this.KEYS.INTERVIEWS)) this.set(this.KEYS.INTERVIEWS, DEMO_INTERVIEWS);
    if (!localStorage.getItem(this.KEYS.NOTIFICATIONS)) this.set(this.KEYS.NOTIFICATIONS, NOTIFICATIONS);
    if (!localStorage.getItem(this.KEYS.REGISTERED_USERS)) {
      // Seed one demo login per role so the three separate login pages
      // all have a working "demo account" without requiring registration first.
      this.set(this.KEYS.REGISTERED_USERS, [
        { email: "ananya@college.edu", password: "demo1234", role: "student", refId: "s1" },
        { email: "hr@nexora.com", password: "demo1234", role: "company", refId: "c1" },
        { email: "officer@college.edu", password: "demo1234", role: "officer", refId: "officer1" },
      ]);
    }
  },

  students() { return this.get(this.KEYS.STUDENTS, []); },
  setStudents(v) { this.set(this.KEYS.STUDENTS, v); },
  companies() { return this.get(this.KEYS.COMPANIES, []); },
  setCompanies(v) { this.set(this.KEYS.COMPANIES, v); },
  jobs() { return this.get(this.KEYS.JOBS, []); },
  setJobs(v) { this.set(this.KEYS.JOBS, v); },
  drives() { return this.get(this.KEYS.DRIVES, []); },
  setDrives(v) { this.set(this.KEYS.DRIVES, v); },
  applications() { return this.get(this.KEYS.APPLICATIONS, []); },
  setApplications(v) { this.set(this.KEYS.APPLICATIONS, v); },
  interviews() { return this.get(this.KEYS.INTERVIEWS, []); },
  setInterviews(v) { this.set(this.KEYS.INTERVIEWS, v); },
  notifications() { return this.get(this.KEYS.NOTIFICATIONS, []); },
  setNotifications(v) { this.set(this.KEYS.NOTIFICATIONS, v); },
  registeredUsers() { return this.get(this.KEYS.REGISTERED_USERS, []); },
  setRegisteredUsers(v) { this.set(this.KEYS.REGISTERED_USERS, v); },

  session() { return this.get(this.KEYS.SESSION, null); },
  setSession(v) { this.set(this.KEYS.SESSION, v); },
  clearSession() { localStorage.removeItem(this.KEYS.SESSION); },
};

const Auth = {
  ROLE_LABELS: { student: "Student", company: "Company", officer: "Placement Officer" },

  login(email, password, role) {
    const user = Store.registeredUsers().find(
      u => u.email.toLowerCase() === email.toLowerCase() && u.password === password && u.role === role
    );
    if (!user) return { ok: false, error: `No ${this.ROLE_LABELS[role].toLowerCase()} account matches those credentials.` };
    Store.setSession({ role: user.role, refId: user.refId, email: user.email });
    return { ok: true };
  },

  registerStudent({ name, email, password, phone, branch, course, cgpa }) {
    const users = Store.registeredUsers();
    if (users.find(u => u.email.toLowerCase() === email.toLowerCase())) {
      return { ok: false, error: "An account with this email already exists." };
    }
    const students = Store.students();
    const id = "s" + (students.length + Date.now());
    students.push({ id, name, email, phone, branch, course, cgpa: parseFloat(cgpa), skills: [], resumeName: null, profileComplete: 30 });
    Store.setStudents(students);

    users.push({ email, password, role: "student", refId: id });
    Store.setRegisteredUsers(users);
    Store.setSession({ role: "student", refId: id, email });
    return { ok: true };
  },

  registerCompany({ name, email, password, website, description }) {
    const users = Store.registeredUsers();
    if (users.find(u => u.email.toLowerCase() === email.toLowerCase())) {
      return { ok: false, error: "An account with this email already exists." };
    }
    const companies = Store.companies();
    const id = "c" + (companies.length + Date.now());
    companies.push({ id, name, email, website, description, status: "pending", logo: "🏢" });
    Store.setCompanies(companies);

    users.push({ email, password, role: "company", refId: id });
    Store.setRegisteredUsers(users);
    Store.setSession({ role: "company", refId: id, email });
    return { ok: true, pending: true };
  },

  isLoggedIn() { return !!Store.session(); },
  currentRole() { return Store.session()?.role || null; },

  currentStudent() {
    const s = Store.session();
    if (!s || s.role !== "student") return null;
    return Store.students().find(st => st.id === s.refId) || null;
  },
  currentCompany() {
    const s = Store.session();
    if (!s || s.role !== "company") return null;
    return Store.companies().find(c => c.id === s.refId) || null;
  },

  logout() {
    Store.clearSession();
    window.location.href = "index.html";
  },

  // Call at the top of every protected page. Redirects if not logged in
  // as the required role, so a student can't load company.html etc.
  requireRole(requiredRole) {
    const session = Store.session();
    if (!session || session.role !== requiredRole) {
      window.location.href = "login-" + requiredRole + ".html";
      return false;
    }
    return true;
  },
};

const Jobs = {
  withCompany(job) {
    const company = Store.companies().find(c => c.id === job.companyId);
    return { ...job, company };
  },
  all() { return Store.jobs().map(this.withCompany); },
  byId(id) { return this.withCompany(Store.jobs().find(j => j.id === id)); },
  isEligible(job, student) {
    if (!student) return false;
    if (student.cgpa < job.eligibility.minCgpa) return false;
    if (job.eligibility.branches.length && !job.eligibility.branches.includes(student.branch)) return false;
    return true;
  },
};

const Applications = {
  forStudent(studentId) {
    return Store.applications().filter(a => a.studentId === studentId).map(a => ({ ...a, job: Jobs.byId(a.jobId) }));
  },
  forJob(jobId) {
    return Store.applications().filter(a => a.jobId === jobId).map(a => {
      const student = Store.students().find(s => s.id === a.studentId);
      return { ...a, student };
    });
  },
  hasApplied(studentId, jobId) {
    return Store.applications().some(a => a.studentId === studentId && a.jobId === jobId);
  },
  apply(studentId, jobId) {
    const apps = Store.applications();
    const id = "a" + Date.now();
    apps.push({ id, studentId, jobId, status: "applied", appliedDate: new Date().toISOString().slice(0, 10) });
    Store.setApplications(apps);
    return id;
  },
  updateStatus(applicationId, status) {
    const apps = Store.applications();
    const app = apps.find(a => a.id === applicationId);
    if (app) app.status = status;
    Store.setApplications(apps);
  },
};

const UI = {
  formatCurrency(amount) {
    if (amount >= 100000) return "₹" + (amount / 100000).toFixed(1).replace(/\.0$/, "") + " LPA";
    return "₹" + amount.toLocaleString("en-IN") + "/mo";
  },

  formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
  },

  initials(name) {
    return (name || "?").split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase();
  },

  toast(message, type = "success") {
    let el = document.getElementById("toast");
    if (!el) {
      el = document.createElement("div");
      el.id = "toast";
      document.body.appendChild(el);
    }
    el.className = "toast " + type;
    el.textContent = message;
    requestAnimationFrame(() => el.classList.add("show"));
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => el.classList.remove("show"), 2600);
  },

  statusPipelineHTML(status) {
    const isRejected = status === "rejected";
    const currentIndex = STATUS_FLOW.indexOf(status);
    const labels = { applied: "Applied", review: "Review", shortlisted: "Shortlisted", interview: "Interview", selected: "Selected" };

    return `
      <div class="status-pipeline">
        ${STATUS_FLOW.map((step, i) => {
          let stepClass = "";
          if (isRejected) {
            // When rejected, every step up to (but not including) the final
            // one is marked done; the step the rejection happened at is "rejected".
            stepClass = i < STATUS_FLOW.length - 1 ? "rejected" : "";
          } else if (i < currentIndex) {
            stepClass = "done";
          } else if (i === currentIndex) {
            stepClass = "current";
          }
          return `
            <div class="step ${stepClass}">
              <div class="line"></div>
              <div class="dot">${stepClass === "done" ? "✓" : i + 1}</div>
              <div class="label">${labels[step]}</div>
            </div>
          `;
        }).join("")}
      </div>
      ${isRejected ? `<p style="color:var(--red); font-size:0.8rem; font-weight:600; margin-top:6px;">Not selected for this role</p>` : ""}
    `;
  },
};

document.addEventListener("DOMContentLoaded", () => {
  Store.ensureSeeded();
});
