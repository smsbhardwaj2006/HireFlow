/* ==========================================================================
   HireFlow — Dashboard Sidebar
   One sidebar component shared by all three portals. Each portal page sets
   window.HIREFLOW_ROLE and window.HIREFLOW_ACTIVE_PAGE before this runs.
   ========================================================================== */

const SIDEBAR_NAV = {
  student: [
    { href: "student-dashboard.html", icon: "📊", label: "Dashboard" },
    { href: "student-profile.html", icon: "👤", label: "My Profile" },
    { href: "student-resume.html", icon: "📄", label: "Resume" },
    { href: "student-jobs.html", icon: "💼", label: "Job Listings" },
    { href: "student-applications.html", icon: "📋", label: "My Applications" },
    { href: "student-interviews.html", icon: "🗓️", label: "Interview Schedule" },
    { href: "student-notifications.html", icon: "🔔", label: "Notifications" },
  ],
  company: [
    { href: "company-dashboard.html", icon: "📊", label: "Dashboard" },
    { href: "company-profile.html", icon: "🏢", label: "Company Profile" },
    { href: "company-jobs.html", icon: "💼", label: "Manage Jobs" },
    { href: "company-applicants.html", icon: "👥", label: "View Applicants" },
    { href: "company-interviews.html", icon: "🗓️", label: "Interview Schedule" },
    { href: "company-offers.html", icon: "📨", label: "Offer Letters" },
  ],
  officer: [
    { href: "officer-dashboard.html", icon: "📊", label: "Dashboard" },
    { href: "officer-students.html", icon: "🎓", label: "Manage Students" },
    { href: "officer-companies.html", icon: "🏢", label: "Manage Companies" },
    { href: "officer-drives.html", icon: "🚀", label: "Placement Drives" },
    { href: "officer-reports.html", icon: "📈", label: "Reports" },
    { href: "officer-notifications.html", icon: "🔔", label: "Notifications" },
  ],
};

function renderDashboardShell(role, activePage) {
  if (!Auth.requireRole(role)) return; // redirects if wrong/no session, halts rendering

  const shell = document.getElementById("dash-shell-root");
  if (!shell) return;

  const navItems = SIDEBAR_NAV[role];
  const session = Store.session();

  let displayName = session.email;
  let avatarInitials = "U";
  if (role === "student") {
    const student = Auth.currentStudent();
    displayName = student ? student.name : session.email;
    avatarInitials = UI.initials(displayName);
  } else if (role === "company") {
    const company = Auth.currentCompany();
    displayName = company ? company.name : session.email;
    avatarInitials = UI.initials(displayName);
  } else {
    displayName = "Placement Officer";
    avatarInitials = "PO";
  }

  const sidebarHTML = `
    <aside class="dash-sidebar">
      <div class="sidebar-logo">
        <a href="index.html" class="logo"><span class="mark">H</span> HireFlow</a>
      </div>
      <div class="sidebar-role-tag">${Auth.ROLE_LABELS[role]} Portal</div>
      <nav>
        ${navItems.map(item => `
          <a href="${item.href}" class="${item.href === activePage ? 'active' : ''}">
            <span>${item.icon}</span> ${item.label}
          </a>
        `).join("")}
      </nav>
      <div class="sidebar-footer">
        <div class="sidebar-user-avatar">${avatarInitials}</div>
        <div>
          <div class="sidebar-user-name">${displayName}</div>
          <div class="sidebar-user-role">${session.email}</div>
        </div>
        <a href="#" class="sidebar-logout" id="logout-link" title="Log out">⏻</a>
      </div>
    </aside>
  `;

  shell.insertAdjacentHTML("afterbegin", sidebarHTML);
  document.getElementById("logout-link").addEventListener("click", (e) => {
    e.preventDefault();
    Auth.logout();
  });
}
