/* ==========================================================================
   HireFlow — Mock Data
   Stands in for the Django + SQLite/MySQL backend per the PRD. Real models
   would be: Student, Company, PlacementDrive, Job, Application, Interview,
   Notification — this file's shapes mirror those tables directly.
   ========================================================================== */

const COMPANIES = [
  { id: "c1", name: "Nexora Technologies", email: "hr@nexora.com", website: "nexora.com", description: "Enterprise SaaS company building workflow automation tools.", status: "approved", logo: "🟦" },
  { id: "c2", name: "BrightPath Analytics", email: "hr@brightpath.com", website: "brightpath.com", description: "Data analytics and BI consulting firm.", status: "approved", logo: "🟩" },
  { id: "c3", name: "Verdant Systems", email: "hr@verdant.com", website: "verdant.io", description: "Cloud infrastructure and DevOps tooling startup.", status: "approved", logo: "🟪" },
  { id: "c4", name: "Quanta Robotics", email: "hr@quanta.com", website: "quantarobotics.com", description: "Industrial automation and robotics hardware.", status: "pending", logo: "🟧" },
];

const JOBS = [
  { id: "j1", companyId: "c1", title: "Software Engineer Trainee", location: "Bangalore", salary: 650000, type: "Full-time",
    eligibility: { minCgpa: 7.0, branches: ["CSE", "IT"] },
    deadline: "2026-07-15", driveDate: "2026-07-22",
    description: "Work on backend services for our workflow automation platform. 6-month training period followed by full-time role." },
  { id: "j2", companyId: "c2", title: "Data Analyst", location: "Pune", salary: 580000, type: "Full-time",
    eligibility: { minCgpa: 6.5, branches: ["CSE", "IT", "ECE"] },
    deadline: "2026-07-10", driveDate: "2026-07-18",
    description: "Analyze client datasets and build dashboards using SQL and Python. Strong stats fundamentals expected." },
  { id: "j3", companyId: "c3", title: "Cloud Engineer Intern", location: "Remote", salary: 35000, type: "Internship",
    eligibility: { minCgpa: 7.5, branches: ["CSE", "IT"] },
    deadline: "2026-07-20", driveDate: "2026-07-28",
    description: "6-month internship working on Kubernetes-based deployment tooling. Stipend per month." },
  { id: "j4", companyId: "c1", title: "Frontend Developer", location: "Bangalore", salary: 700000, type: "Full-time",
    eligibility: { minCgpa: 7.0, branches: ["CSE", "IT", "ECE"] },
    deadline: "2026-07-15", driveDate: "2026-07-22",
    description: "Build and maintain our React-based customer dashboard. Strong JS fundamentals required." },
  { id: "j5", companyId: "c2", title: "Business Analyst", location: "Pune", salary: 550000, type: "Full-time",
    eligibility: { minCgpa: 6.0, branches: ["CSE", "IT", "ECE", "MECH"] },
    deadline: "2026-07-12", driveDate: "2026-07-18",
    description: "Bridge client requirements and engineering teams. Good communication skills essential." },
];

const DRIVES = [
  { id: "d1", companyId: "c1", title: "Nexora Campus Drive 2026", jobIds: ["j1", "j4"], deadline: "2026-07-15", interviewDate: "2026-07-22", status: "open" },
  { id: "d2", companyId: "c2", title: "BrightPath Hiring Drive", jobIds: ["j2", "j5"], deadline: "2026-07-10", interviewDate: "2026-07-18", status: "open" },
  { id: "d3", companyId: "c3", title: "Verdant Internship Drive", jobIds: ["j3"], deadline: "2026-07-20", interviewDate: "2026-07-28", status: "open" },
];

// Demo students — in the real system these would be created via registration.
// One has a fuller profile/history to make the dashboards look populated.
const DEMO_STUDENTS = [
  { id: "s1", name: "Ananya Verma", email: "ananya@college.edu", phone: "9876543210", branch: "CSE", course: "B.Tech", cgpa: 8.4,
    skills: ["Python", "Django", "SQL", "React"], resumeName: "Ananya_Verma_Resume.pdf", profileComplete: 90 },
  { id: "s2", name: "Rohan Iyer", email: "rohan@college.edu", phone: "9123456780", branch: "IT", course: "B.Tech", cgpa: 7.2,
    skills: ["Java", "Spring Boot"], resumeName: null, profileComplete: 55 },
  { id: "s3", name: "Meera Pillai", email: "meera@college.edu", phone: "9988776655", branch: "ECE", course: "B.Tech", cgpa: 8.9,
    skills: ["C++", "Embedded Systems"], resumeName: "Meera_Pillai_CV.pdf", profileComplete: 100 },
];

// Demo applications — pre-seeded so the student/company/officer dashboards
// have something to show without requiring you to click through every flow first.
const DEMO_APPLICATIONS = [
  { id: "a1", studentId: "s1", jobId: "j1", status: "interview", appliedDate: "2026-06-20" },
  { id: "a2", studentId: "s1", jobId: "j2", status: "shortlisted", appliedDate: "2026-06-18" },
  { id: "a3", studentId: "s2", jobId: "j1", status: "review", appliedDate: "2026-06-22" },
  { id: "a4", studentId: "s3", jobId: "j3", status: "selected", appliedDate: "2026-06-15" },
  { id: "a5", studentId: "s2", jobId: "j5", status: "rejected", appliedDate: "2026-06-19" },
];

const DEMO_INTERVIEWS = [
  { id: "i1", applicationId: "a1", studentId: "s1", companyId: "c1", date: "2026-07-22", time: "10:00 AM", venue: "Seminar Hall A", status: "scheduled" },
  { id: "i2", applicationId: "a4", studentId: "s3", companyId: "c3", date: "2026-07-10", time: "2:00 PM", venue: "Online — Google Meet", status: "completed" },
];

const STATUS_FLOW = ["applied", "review", "shortlisted", "interview", "selected"];
// "rejected" can branch off at any point, handled separately in rendering

const NOTIFICATIONS = [
  { id: "n1", type: "drive", title: "New Drive: Nexora Campus Drive 2026", message: "Nexora Technologies is hiring for Software Engineer Trainee and Frontend Developer roles.", date: "2026-06-20", audience: "students" },
  { id: "n2", type: "deadline", title: "Application Deadline Approaching", message: "BrightPath Hiring Drive closes on July 10th. Apply before the deadline.", date: "2026-06-25", audience: "students" },
  { id: "n3", type: "interview", title: "Interview Scheduled", message: "Your interview with Nexora Technologies is scheduled for July 22nd, 10:00 AM at Seminar Hall A.", date: "2026-06-26", audience: "students" },
  { id: "n4", type: "result", title: "Placement Result Declared", message: "Congratulations to students selected in the Verdant Internship Drive!", date: "2026-06-24", audience: "students" },
];

const BRANCHES = ["CSE", "IT", "ECE", "MECH", "CIVIL", "EEE"];
