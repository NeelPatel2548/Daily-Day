# PMS CODEBASE REPORT — PART 2 (Sections 4–6)

---

## 4. FRONTEND FILE-BY-FILE ANALYSIS

### 4.1 ENTRY & CONFIG

#### `client/vite.config.js`
- **Responsibility**: Vite build config, dev proxy for API and WebSocket.
- **Core Logic**: Proxies `/api` → `http://localhost:5000` and `/socket.io` → same (with `ws: true` for WebSocket upgrade). Dev server on port 5173.

#### `client/src/main.jsx`
- **Responsibility**: React entry point — mounts `<App>` inside `<BrowserRouter>` and `<AuthProvider>`.
- **Exports**: None (entry)
- **State**: None (delegates to `AuthProvider`)

#### `client/src/App.jsx` (159 lines)
- **Responsibility**: All route definitions + layout logic (Navbar, Sidebar, ProtectedRoute wiring).
- **Hooks**: `useAuth()` for `loading` and `isAuthenticated`.
- **State**: Derives `showSidebar` and `showNavbar` from auth state and current pathname.
- **UI**: Conditional Navbar (hidden on `/contact`), conditional Sidebar (shown for authenticated non-landing pages). Routes organized into 4 groups: Public (7), Student (5), Company (8), Admin (7).
- **Connections**: Imports all page/component files. Uses `ProtectedRoute` with `allowedRoles` prop.

#### `client/src/index.css` (225 lines)
- **Responsibility**: Global styles + Bauhaus design token CSS utility classes.
- **Design System**: Imports Google Fonts `Outfit`. Defines `.bauhaus-card` (4px black border, 8px offset shadow), `.bauhaus-btn-primary` (red #D02020), `.bauhaus-btn-secondary` (blue #1040C0), `.bauhaus-btn-accent` (yellow #F0C020), `.bauhaus-btn-outline`, `.bauhaus-input`, `.bauhaus-badge`. Custom scrollbar (dark thumb). Bauhaus geometric loader animation (3-shape pulse with staggered delays). Marquee animations for landing page recruiter carousel.
- **Also uses**: Tailwind CSS (`@tailwind base/components/utilities`).

---

### 4.2 CONTEXT & SERVICES

#### `client/src/context/AuthContext.jsx` (145 lines)
- **Responsibility**: Global auth state, Socket.IO lifecycle, session restore, notification unread count.
- **Exports**: `AuthProvider` (component), `useAuth` (hook)
- **State**: `user` (object|null), `loading` (boolean), `unreadCount` (number)
- **API Calls**:
  - `checkAuth()` → `GET /api/auth/me` (on mount)
  - `login()` → `POST /api/auth/login`
  - `loginVerify()` → `POST /api/auth/login/verify` + `checkAuth()`
  - `register()` → `POST /api/auth/register`
  - `verifyOTP()` → `POST /api/auth/verify-otp` (no auto-login)
  - `logout()` → `POST /api/auth/logout`
  - Fetches `GET /api/notifications/unread-count` when user is set
- **Socket.IO**: Connects when `user` is truthy, listens for `notification` events, disconnects on logout.
- **Provided Values**: `user`, `loading`, `login`, `loginVerify`, `register`, `verifyOTP`, `logout`, `updateUser`, `checkAuth`, `isAuthenticated`, `unreadCount`, `decrementUnread`, `resetUnread`, `getSocket`

#### `client/src/services/api.js` (48 lines)
- **Responsibility**: Axios instance with `withCredentials: true`, 401 interceptor, PDF proxy URL builder.
- **Exports**: Default `api` instance, named `getPdfProxyUrl(cloudinaryUrl)`
- **Core Logic**: Base URL from `VITE_API_URL` or `/api`. Response interceptor redirects to `/login` on 401 (except for public paths). `getPdfProxyUrl` strips `/api` suffix and appends `/api/pdf-proxy?url=encoded`.

#### `client/src/services/socket.js` (53 lines)
- **Responsibility**: Socket.IO client connection management.
- **Exports**: `connectSocket`, `disconnectSocket`, `getSocket`
- **Core Logic**: Derives server URL from `VITE_API_URL` (strips `/api`). Connects with `withCredentials: true`, WebSocket + polling transports, 10 reconnection attempts with 2s delay. Logs connection lifecycle events.

---

### 4.3 DATA

#### `client/src/data/landingData.js` (156 lines)
- **Responsibility**: Static content arrays for landing page sections.
- **Exports**: `topRecruiters` (15 companies with name, package, hired count), `testimonials` (4 student stories), `placementStats` (6 stat cards), `howItWorks` (4 steps), `features` (6 feature descriptions).

---

### 4.4 PAGES (Public)

#### `client/src/pages/LandingPage.jsx`
- **Responsibility**: Dynamic hero, live stats, top recruiters marquee, how-it-works, features, testimonials, CTA.
- **API Calls**: `GET /api/public/stats` (on mount), `GET /api/public/companies` (on mount)
- **State**: `stats`, `publicCompanies`, `loading`
- **UI**: Hero section with animated geometric shapes, stats counter cards, dual-row marquee of recruiter logos (static + dynamic), step-by-step flow, feature grid, testimonial cards, CTA section.

#### `client/src/pages/ContactUs.jsx`
- **Responsibility**: Public contact form with its own standalone navigation bar.
- **API Calls**: `GET /api/public/settings` (on mount), `POST /api/public/contact` (on submit)
- **State**: `form` (name, email, subject, message), `publicSettings`, `status`, `loading`
- **UI**: Standalone nav (not the main Navbar), Bauhaus-styled form, contact info sidebar showing settings data.

#### `client/src/pages/NotFound.jsx`
- **Responsibility**: 404 page with Bauhaus geometric design.
- **UI**: Large "404" display, navigation back to home.

#### `client/src/pages/Unauthorized.jsx`
- **Responsibility**: Role mismatch redirect page.
- **UI**: Displays access denied message, redirects based on user's actual role.

---

### 4.5 AUTH COMPONENTS

#### `client/src/components/auth/Login.jsx`
- **Responsibility**: Email + password form (Step 1 of 2-step login), includes forgot password modal.
- **API Calls**: `login()` via `useAuth()`, forgot password endpoints.
- **State**: `email`, `password`, `error`, `loading`, `showForgotPassword`, `forgotStep`
- **UI**: Bauhaus-styled card form, conditional OTP redirect, multi-step forgot password modal.

#### `client/src/components/auth/Register.jsx`
- **Responsibility**: Multi-field registration form (name, email, password, role).
- **API Calls**: `register()` via `useAuth()`
- **State**: `formData`, `error`, `loading`
- **UI**: Role selector (student/company), password visibility toggle, navigates to `/verify-otp` on success.

#### `client/src/components/auth/VerifyOTP.jsx`
- **Responsibility**: Shared OTP verification screen for registration and login flows.
- **API Calls**: `verifyOTP()` or `loginVerify()` via `useAuth()`, `POST /api/auth/resend-otp`
- **State**: `otp` (6-digit), `error`, `loading`, `countdown` (resend timer)
- **UI**: 6-digit OTP input, resend button with cooldown timer, auto-submit on 6 digits.

---

### 4.6 COMMON / SHARED COMPONENTS

#### `client/src/components/common/Navbar.jsx`
- **Responsibility**: Top navigation bar, conditional rendering for auth/unauth states, notification bell.
- **Hooks**: `useAuth()`, `useNavigate()`
- **UI**: Logo + brand name, role-based nav links (dashboard link per role), notification bell with unread badge, user menu with logout.

#### `client/src/components/common/Sidebar.jsx`
- **Responsibility**: Role-specific collapsible side navigation.
- **Hooks**: `useAuth()`, `useLocation()`
- **State**: `isCollapsed`
- **UI**: Different navigation items per role — Student (Dashboard, Profile, Jobs, Applications, Interviews), Company (Dashboard, Profile, Post Job, My Jobs), Admin (Dashboard, Students, Companies, Jobs, Reports, Settings). Active link highlighting.

#### `client/src/components/common/Loader.jsx`
- **Responsibility**: Full-screen loading spinner shown during auth initialisation.
- **Props**: `text` (optional loading message)
- **UI**: Bauhaus geometric shapes (circle, square, triangle) with staggered pulse animations.

#### `client/src/components/common/ResumeViewer.jsx`
- **Responsibility**: PDF display with proxy iframe and Google Docs fallback.
- **Props**: `resumeUrl`
- **Core Logic**: Uses `getPdfProxyUrl()` to build proxied URL for iframe. Falls back to Google Docs Viewer if iframe fails.

#### `client/src/components/common/ProtectedRoute.jsx`
- **Responsibility**: Auth + role guard wrapper for private routes.
- **Props**: `allowedRoles` (array), `children`
- **Hooks**: `useAuth()`
- **Core Logic**: If not authenticated → redirect to `/login`. If role not in allowedRoles → redirect to `/unauthorized`. If `mustChangePassword` → redirect to `/change-password`. Otherwise render children.

#### `client/src/components/common/NotificationBell.jsx`
- **Responsibility**: Dropdown bell icon with unread badge, notification list, mark-read actions.
- **Hooks**: `useAuth()` (unreadCount, decrementUnread, resetUnread)
- **API Calls**: `GET /api/notifications` (on dropdown open), `PUT /api/notifications/:id/read`, `PUT /api/notifications/read-all`
- **State**: `notifications`, `isOpen`, `loading`
- **UI**: Bell icon with red unread count badge, dropdown list with notification items (title, message, time-ago, link), mark all read button.

---

### 4.7 STUDENT COMPONENTS

#### `client/src/components/student/StudentDashboard.jsx`
- **API Calls**: `GET /api/student/dashboard`
- **State**: `dashData`, `loading`
- **UI**: Welcome banner, stat cards (total apps, shortlisted, interviews, selected, rejected), profile completion progress bar with category breakdown, upcoming interviews list with countdown timers, offers section.

#### `client/src/components/student/StudentProfile.jsx`
- **API Calls**: `GET /api/student/profile`, `PUT /api/student/profile`, `POST /api/student/resume`, `POST /api/student/profile/picture`, `GET /api/public/skills`
- **State**: `profile`, `formData`, `activeTab`, `loading`, `uploading`
- **UI**: Tabbed form (Personal, Academic, Skills & Projects, Resume & Links). Profile picture upload with preview. Resume upload with PDF viewer. Skills multi-select from predefined list. Academic fields locked when verified (visual lock indicator).

#### `client/src/components/student/JobList.jsx`
- **API Calls**: `GET /api/student/jobs`, `POST /api/student/apply/:jobId`
- **State**: `jobs`, `loading`, `applying`, `search`, `filters`
- **UI**: Job cards with company logo, skill match badges (strong/partial/none with percentage), eligibility indicators, apply button, search/filter controls.

#### `client/src/components/student/ApplicationTracker.jsx`
- **API Calls**: `GET /api/student/applications`, `PUT /api/student/applications/:id/withdraw`
- **State**: `applications`, `loading`
- **UI**: Kanban-style pipeline view organized by status columns (Applied → Shortlisted → Interview → Selected/Rejected). Each card shows company, job title, status, date. Withdraw action on eligible applications.

#### `client/src/components/student/InterviewSchedule.jsx`
- **API Calls**: `GET /api/student/interviews`
- **State**: `interviews`, `loading`
- **UI**: Interview cards sorted chronologically with countdown timer, round name, company, mode (online/offline), venue/meeting link, status badges.

---

### 4.8 COMPANY COMPONENTS

#### `client/src/components/company/CompanyDashboard.jsx`
- **API Calls**: `GET /api/company/dashboard`
- **UI**: Approval status banner (if not approved), stat cards, recent jobs list.

#### `client/src/components/company/CompanyProfile.jsx`
- **API Calls**: `GET /api/company/profile`, `PUT /api/company/profile`, `POST /api/company/profile/logo`
- **UI**: Company info form (name, industry, location, website, description, HR details), logo upload with preview.

#### `client/src/components/company/PostJob.jsx`
- **API Calls**: `POST /api/company/jobs`, `GET /api/public/skills`
- **UI**: Multi-section job posting form (title, description, type, package, skills, eligibility criteria, deadline).

#### `client/src/components/company/EditJob.jsx`
- **API Calls**: `GET /api/company/jobs/:id`, `PUT /api/company/jobs/:id`
- **UI**: Pre-filled edit form mirroring PostJob structure.

#### `client/src/components/company/CompanyJobList.jsx`
- **API Calls**: `GET /api/company/jobs`, `PATCH /api/company/jobs/:id/status`
- **UI**: Job listing table with status toggle, edit link, view applicants link, application count.

#### `client/src/components/company/JobDetails.jsx`
- **API Calls**: `GET /api/company/jobs/:id/applicants`, `PUT /api/company/applications/:id/status`, `POST /api/company/interviews`, `GET /api/company/jobs/:id/export`
- **UI**: Applicant table with student details, status update dropdowns, interview scheduling modal, CSV export button, resume viewer.

---

### 4.9 ADMIN COMPONENTS

#### `client/src/components/admin/AdminDashboard.jsx`
- **API Calls**: `GET /api/admin/dashboard`
- **UI**: System-wide stat cards, placement rate percentage, branch-wise bar chart, recent applications table.

#### `client/src/components/admin/ManageStudents.jsx`
- **API Calls**: `GET /api/admin/students`, `PUT /api/admin/students/:id/verify-academic`, `PUT /api/admin/students/:id/academic`, `DELETE /api/admin/users/:id`, `PUT /api/admin/users/:id/status`, `GET /api/admin/students/export/unplaced`
- **UI**: Student table with search, branch/year/status filters, pagination. Academic verification toggle. Suspend/delete actions. Expandable student detail view. CSV export for unplaced students.

#### `client/src/components/admin/ManageCompanies.jsx`
- **API Calls**: `GET /api/admin/companies`, `PUT /api/admin/companies/:id/approve`, `PUT /api/admin/companies/:id`, `DELETE /api/admin/users/:id`
- **UI**: Company table with approval toggle, tier selector, edit modal, delete confirmation.

#### `client/src/components/admin/PlacementSettings.jsx`
- **API Calls**: `GET /api/admin/settings`, `PUT /api/admin/settings`
- **UI**: Settings form — placement season toggle, max applications, block placed students, min CGPA override, branding fields (logo URL, company name, contact email, phone, address).

#### `client/src/components/admin/PlacementReports.jsx`
- **API Calls**: `GET /api/admin/reports`, `POST /api/admin/reports`, `DELETE /api/admin/reports/:id`
- **UI**: Report generation form (academic year), reports table with branch-wise stats, avg/max package display, delete action.

---

## 5. SAME-NAME FILE COMPARISON SECTION

### 5.1 `api.js` — Backend Reference vs Frontend File

| Aspect | Backend (referenced by controllers) | Frontend (`client/src/services/api.js`) |
|--------|-------------------------------------|----------------------------------------|
| **(a) Why both exist** | The backend IS the API — Express routes define the API endpoints. There is no single `api.js` on the backend; the "API layer" is distributed across route files. | The frontend needs a configured HTTP client to call those endpoints. |
| **(b) What each does** | Express route handlers receive HTTP requests, apply middleware, call controllers | Axios instance preconfigured with `withCredentials`, base URL, 401 interceptor, and PDF proxy helper |
| **(c) Data contract** | All controllers return `{ success: boolean, message: string, data: any }` via `apiResponse.js` | Frontend reads `res.data.success`, `res.data.data`, `res.data.message` |
| **(d) Confusion risk** | **Low** — there is no literal `api.js` file on the backend. The user prompt's reference is conceptual. |
| **(e) Suggested rename** | None needed — the naming is clear and conventional. |

### 5.2 `interviewReminder.js` vs `InterviewSchedule.jsx`

| Aspect | Backend (`server/services/interviewReminder.js`) | Frontend (`InterviewSchedule.jsx`) |
|--------|------------------------------------------------|-----------------------------------|
| **(a) Why both exist** | Backend handles automated reminder delivery (email + notification). Frontend displays the schedule for student interaction. |
| **(b) What each does** | Background `setInterval` (30 min) queries DB for interviews within 24 hours, creates notifications via `createAndEmitNotification`, sends reminder emails via `sendInterviewReminderEmail`. Uses in-memory `Set` to prevent duplicates. | React component that calls `GET /api/student/interviews`, displays interview cards with countdown timers, mode, venue/meeting link, and status. |
| **(c) Data contract** | Both read from the same `Interview` model. Backend writes `Notification` docs + emits Socket.IO events. Frontend reads Interview documents via the student controller's `getInterviews()`. |
| **(d) Confusion risk** | **Medium** — the names suggest related but different concerns. A developer might search for "interview reminder" and find the backend file but miss the frontend schedule display, or vice versa. |
| **(e) Suggested rename** | Keep as-is. The naming correctly distinguishes the concern: "reminder" = proactive push, "schedule" = reactive display. Adding a comment cross-reference in each file would help. |

### 5.3 `Application.js` vs `ApplicationTracker.jsx`

| Aspect | Backend (`server/models/Application.js`) | Frontend (`ApplicationTracker.jsx`) |
|--------|----------------------------------------|-------------------------------------|
| **(a) Why both exist** | Backend defines the data structure and persistence layer for applications. Frontend provides the student-facing UI to view and manage their applications. |
| **(b) What each does** | Mongoose schema: 12 fields, 4 indexes (including unique compound `student+job`). Status enum: applied→shortlisted→interview→selected→rejected→withdrawn. Offer fields: `offerStatus`, `offeredPackage`, `offerLetterUrl`. | React component that fetches all student applications, displays in a Kanban-style pipeline view grouped by status, supports withdrawal action. |
| **(c) Data contract** | Model defines the shape. Controller `getApplications()` populates `job` (with nested `company`) and `company`. Frontend receives populated documents via `GET /api/student/applications`. Key fields consumed: `status`, `job.title`, `company.name`, `company.logo`, `createdAt`. |
| **(d) Confusion risk** | **Low** — `Application.js` (singular noun) clearly suggests a model/schema. `ApplicationTracker.jsx` (verb-noun compound with `.jsx`) clearly suggests a React component. |
| **(e) Suggested rename** | None needed. |

### 5.4 `Notification.js` vs `NotificationBell.jsx`

| Aspect | Backend (`server/models/Notification.js`) | Frontend (`NotificationBell.jsx`) |
|--------|------------------------------------------|----------------------------------|
| **(a) Why both exist** | Backend defines the notification data structure with TTL auto-cleanup. Frontend provides the interactive UI for reading notifications. |
| **(b) What each does** | Mongoose schema: 6 fields. TTL index at 90 days (7,776,000 seconds). Type enum: job_posted, application_update, interview_scheduled, offer_received, announcement, security. | React dropdown component: bell icon with unread badge, fetches notifications on open, mark individual/all as read, navigates to notification links. |
| **(c) Data contract** | Model defines the shape. `notificationController.js` provides paginated list, mark-read, delete, unread-count endpoints. Frontend calls these endpoints and also listens for `notification` Socket.IO events via `AuthContext`. Key fields consumed: `title`, `message`, `type`, `isRead`, `link`, `createdAt`. |
| **(d) Confusion risk** | **Low** — `.js` model vs `.jsx` component with descriptive "Bell" suffix. |
| **(e) Suggested rename** | None needed. |

---

## 6. DATA FLOW DIAGRAMS

### 6.1 Student Applies for a Job

```
1. Student clicks "Apply" on JobList.jsx
2. Frontend POST /api/student/apply/:jobId (Axios, withCredentials)
3. Express Router → protect() middleware verifies JWT cookie
4. authorize('student') checks role
5. studentController.applyToJob() begins 7-gate validation:
   Gate 1: SystemSettings.getSettings() → check placementSeasonActive
   Gate 2: Check student.placementStatus !== 'placed' (if blockPlacedFromApplying)
   Gate 3: Count active applications vs maxApplicationsPerStudent
   Gate 4: Validate personal fields (name, phone, gender, dob, address)
   Gate 5: Validate academic fields (enrollment, branch, CGPA, percentages, year, semester)
   Gate 6: Check skills.length > 0
   Gate 7: Check academicVerified === true
6. Load Job document → verify status === 'open' and deadline not passed
7. Re-check eligibility: effectiveMinCGPA, maxBacklogs, eligibleBranches
8. Check for duplicate Application (unique index student+job)
9. Application.create({ student, job, company, resumeUrl, status: 'applied' })
10. Notification.create({ user: studentUserId, title: 'Application Submitted', ... })
11. Return { success: true, data: application } → 201
12. Frontend receives response → updates UI → shows success toast
```

### 6.2 Company Posts a Job

```
1. Company fills PostJob.jsx form → clicks "Post Job"
2. Frontend POST /api/company/jobs (Axios, with express-validator body rules)
3. Express Router → protect() + authorize('company')
4. companyController.postJob() begins:
5. Load Company document → verify isApproved === true
6. Build jobData object from req.body (title, description, skills, package, etc.)
7. Job.create(jobData) → MongoDB creates document
8. Student.find({ cgpa: { $gte: minCGPA }, activeBacklogs: { $lte: maxBacklogs },
                   branch: { $in: eligibleBranches } }).populate('user', '_id')
9. Build notifications array: one per eligible student with title "New Job Posted"
10. Notification.insertMany(notifications) → bulk insert
11. [Note: Socket.IO real-time push NOT directly called here — uses DB insert only.
     Students see notifications on next fetch or via polling.]
12. Return { success: true, data: job } → 201
13. Frontend navigates to CompanyJobList
```

### 6.3 Interview Reminder Background Job

```
1. server.js calls startInterviewReminders() on boot
2. setTimeout(checkUpcomingInterviews, 10000) — first run after 10s warmup
3. setInterval(checkUpcomingInterviews, 30 * 60 * 1000) — then every 30 min
4. checkUpcomingInterviews() executes:
5. const now = new Date()
6. const in24Hours = new Date(now + 24h)
7. Interview.find({ scheduledAt: { $gte: now, $lte: in24Hours }, status: 'scheduled' })
     .populate('student', 'user')
     .populate('job', 'title')
     .populate('company', 'name')
8. For each interview not in remindedInterviews Set:
   a. Extract studentUserId from interview.student.user
   b. createAndEmitNotification({ userId, title: '📅 Interview Reminder', ... })
      → Notification.create() in DB
      → emitToUser(userId, 'notification', payload) via Socket.IO
   c. User.findById(studentUserId).select('email')
   d. sendInterviewReminderEmail(email, { roundName, companyName, jobTitle, date, time, mode, venue, meetingLink })
      → Nodemailer → Gmail SMTP → student inbox
   e. remindedInterviews.add(interviewId) — mark as reminded
9. If remindedInterviews.size > 1000, clear Set (prevent memory leak)
10. Log count of reminders sent
```
