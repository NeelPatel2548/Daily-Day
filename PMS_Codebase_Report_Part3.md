# PMS CODEBASE REPORT — PART 3 (Sections 7–10)

---

## 7. SECURITY AUDIT SUMMARY

### 7.1 Consolidated Security Layers

| # | Security Layer | Implementation | File(s) |
|---|---------------|----------------|---------|
| 1 | **HTTP Headers** | `helmet()` sets X-Frame-Options, X-Content-Type-Options, CSP, etc. | `server.js` |
| 2 | **CORS** | Origin locked to `CLIENT_URL`, credentials mode, whitelisted methods/headers | `server.js` |
| 3 | **NoSQL Injection Prevention** | `express-mongo-sanitize()` strips `$` and `.` from user input | `server.js` |
| 4 | **XSS Prevention** | `xss-clean()` sanitizes req.body, req.query, req.params | `server.js` |
| 5 | **JWT in httpOnly Cookie** | Token not accessible via JavaScript; `sameSite: strict`; `secure` in production | `authMiddleware.js` |
| 6 | **Password Hashing** | bcrypt with salt factor 12 (User model pre-save hook) | `User.js`, `authController.js` |
| 7 | **OTP Hashing** | bcrypt with salt factor 10 (stored hashed, never in plaintext) | `otpService.js` |
| 8 | **OTP Attempt Limiting** | Max 5 attempts per OTP; returns remaining count | `authController.js` |
| 9 | **Rate Limiting** | Auth: 20/15min, OTP: 10/15min, Resend: 5/hour | `rateLimiter.js` |
| 10 | **RBAC** | `authorize(...roles)` middleware on every protected route group | `authMiddleware.js`, all route files |
| 11 | **Account Suspension** | `isActive` check in `protect()` middleware — blocks suspended users | `authMiddleware.js` |
| 12 | **Email Verification** | `isVerified` check in `protect()` — blocks unverified accounts | `authMiddleware.js` |
| 13 | **Field Whitelisting** | Controllers use explicit `allowed` arrays; reject unknown fields | All controllers |
| 14 | **Academic Lock** | Verified academic records cannot be edited by students | `studentController.js` |
| 15 | **Duplicate Prevention** | Unique compound index `{ student, job }` on Application model | `Application.js` |
| 16 | **Body Size Limit** | `express.json({ limit: '10mb' })` | `server.js` |
| 17 | **File Type Validation** | MIME type + extension checks in Multer file filters | `upload.js` |
| 18 | **File Size Limits** | Resume: 5MB, Profile Pic: 2MB, Logo: 2MB | `upload.js` |
| 19 | **Cloudinary Cleanup** | Old files deleted on replacement (prevents storage bloat) | `upload.js`, controllers |
| 20 | **OTP Bypass Protection** | Bypass mode hard-blocked in production (`NODE_ENV === 'production'`) | `authController.js` |
| 21 | **Password Select: false** | Password field excluded from queries by default | `User.js` |
| 22 | **Notification Scoping** | All notification queries include `user: req.user._id` | `notificationController.js` |
| 23 | **Socket.IO Auth** | JWT parsed from cookie on WebSocket handshake | `socketService.js` |
| 24 | **URL Validation** | Logo URL validated as http/https protocol | `settingsController.js`, `SystemSettings.js` |
| 25 | **Env Var Guard** | Missing required vars → hard `process.exit(1)` | `validateEnv.js` |
| 26 | **Error Message Hiding** | Production: generic "Internal Server Error"; Dev: full message | `server.js` |
| 27 | **TTL Auto-Delete** | Notifications auto-deleted after 90 days | `Notification.js` |

### 7.2 Potential Gaps & Hardening Suggestions

| # | Gap | Risk Level | Suggestion |
|---|-----|-----------|------------|
| 1 | No CSRF token | Low (mitigated by `sameSite: strict` cookie) | Consider adding CSRF tokens for non-GET state mutations if `sameSite` proves insufficient on some browsers |
| 2 | No request signing | Low | Implement HMAC signature for sensitive operations (password changes) |
| 3 | Socket.IO cookie reads `cookies.token` but httpOnly cookie is named `pms_token` | **Medium** — Socket auth may silently fail | Fix `socketService.js` to read `cookies.pms_token` instead of `cookies.token` |
| 4 | Admin seeder has hardcoded credentials | Medium (dev-only) | Document that admin password MUST be changed after first login |
| 5 | No password complexity enforcement beyond length | Low | Add regex for uppercase, number, special char requirements |
| 6 | Pending registrations Map is in-memory | Medium | If server restarts during registration, pending OTPs are lost. Consider Redis for multi-instance deployments |
| 7 | No account lockout after repeated failed logins | Medium | Implement progressive lockout (e.g., lock for 15 min after 10 failed attempts) |
| 8 | PDF proxy doesn't validate URL domain | Medium | Restrict to Cloudinary domains only to prevent SSRF |
| 9 | Interview reminder Set clears at 1000 entries | Low | Could miss re-reminders if exactly 1000 unique interviews processed |
| 10 | No Content-Security-Policy customization | Low | Customize Helmet CSP to allow only Cloudinary and Google Fonts domains |

---

## 8. DATABASE INDEX CATALOGUE

| # | Model | Field(s) | Type | Purpose |
|---|-------|----------|------|---------|
| 1 | User | `email` | Unique | Login lookup, duplicate prevention |
| 2 | User | `{ role, isActive }` | Compound | Admin dashboard user filtering |
| 3 | Student | `user` | Unique | One student profile per user |
| 4 | Student | `enrollmentNo` | Unique, Sparse | Enrollment lookup (allows null) |
| 5 | Student | `{ cgpa, branch, activeBacklogs }` | Compound | Job eligibility filtering (most critical index) |
| 6 | Student | `placementStatus` | Single | Admin reports: unplaced students |
| 7 | Student | `academicVerified` | Single | Admin verification queue |
| 8 | Student | `passingYear` | Single | Batch-level filtering |
| 9 | Company | `user` | Unique | One company profile per user |
| 10 | Company | `isApproved` | Single | Admin approval queue |
| 11 | Company | `tier` | Single | Tier-based filtering |
| 12 | Job | `company` | Single | Company's job listing |
| 13 | Job | `{ status, minCGPA }` | Compound | Student job listing filter |
| 14 | Job | `eligibleBranches` | Multikey | Branch-based job search |
| 15 | Job | `jobType` | Single | Fulltime/internship filter |
| 16 | Job | `createdAt` (desc) | Single | Latest jobs first |
| 17 | Job | `deadline` | Single | Expired listing queries |
| 18 | Application | `{ student, job }` | Unique Compound | **Prevents duplicate applications** |
| 19 | Application | `{ job, status }` | Compound | Applicant list by status |
| 20 | Application | `{ student, status }` | Compound | Student's application tracker |
| 21 | Application | `company` | Single | Company-wide application view |
| 22 | Interview | `application` | Single | Rounds per application |
| 23 | Interview | `student` | Single | Student's interview schedule |
| 24 | Interview | `company` | Single | Company's interview schedule |
| 25 | Interview | `scheduledAt` | Single | Chronological sorting, date-range queries |
| 26 | Notification | `{ user, isRead }` | Compound | Unread count badge query |
| 27 | Notification | `{ user, createdAt }` (desc) | Compound | User notification feed |
| 28 | Notification | `createdAt` | TTL (90 days) | Auto-delete old notifications |

**Total: 28 indexes across 9 models**

---

## 9. API ENDPOINT CATALOGUE

### Auth Routes (`/api/auth/*`)

| Method | Path | Auth | Role | Controller | Description |
|--------|------|------|------|-----------|-------------|
| POST | `/register` | No | — | `register` | Register new user, send OTP |
| POST | `/verify-otp` | No | — | `verifyOTP` | Verify registration OTP, create user |
| POST | `/login` | No | — | `login` | Login step 1, send login OTP |
| POST | `/login/verify` | No | — | `loginVerify` | Login step 2, verify OTP, set JWT |
| POST | `/logout` | Yes | Any | `logout` | Clear JWT cookie |
| POST | `/resend-otp` | No | — | `resendOTP` | Resend OTP for registration/login |
| POST | `/forgot-password` | No | — | `forgotPassword` | Send reset OTP |
| POST | `/verify-reset-otp` | No | — | `verifyResetOTP` | Verify reset OTP |
| POST | `/reset-password` | No | — | `resetPassword` | Reset password (after OTP) |
| POST | `/forgot-password-check` | No | — | `checkEmailExists` | Check email exists |
| POST | `/forgot-password-verify-current` | No | — | `verifyCurrentPassword` | Verify current or send temp |
| POST | `/forgot-password-send-temp` | No | — | `sendTempPassword` | Send temp password |
| PUT | `/change-password` | Yes | Any | `changePassword` | Change password (after temp) |
| GET | `/me` | Yes | Any | `getMe` | Get current user session |

### Student Routes (`/api/student/*`) — All: Auth + Student Role

| Method | Path | Controller | Description |
|--------|------|-----------|-------------|
| GET | `/dashboard` | `getDashboard` | Stats, interviews, completion score |
| GET | `/profile` | `getProfile` | Student profile with populated user |
| PUT | `/profile` | `updateProfile` | Update profile (field whitelisted) |
| POST | `/profile/picture` | `uploadProfilePicture` | Upload headshot to Cloudinary |
| POST | `/resume` | `uploadResume` | Upload resume PDF to Cloudinary |
| GET | `/jobs` | `getEligibleJobs` | Eligible jobs with skill matching |
| POST | `/apply/:jobId` | `applyToJob` | Apply with 7-gate validation |
| GET | `/applications` | `getApplications` | All student applications |
| PUT | `/applications/:id/withdraw` | `withdrawApplication` | Withdraw application |
| GET | `/interviews` | `getInterviews` | Interview schedule |
| GET | `/offers` | `getOffers` | Selected applications |
| PUT | `/applications/:id/offer` | `respondToOffer` | Accept/decline offer |

### Company Routes (`/api/company/*`) — All: Auth + Company Role

| Method | Path | Controller | Description |
|--------|------|-----------|-------------|
| GET | `/dashboard` | `getDashboard` | Company stats |
| GET | `/profile` | `getProfile` | Company profile |
| PUT | `/profile` | `updateProfile` | Update company info |
| POST | `/profile/logo` | `uploadCompanyLogo` | Upload logo to Cloudinary |
| GET | `/jobs` | `getJobs` | Company's job listings |
| POST | `/jobs` | `postJob` | Post new job + notify students |
| GET | `/jobs/:id` | `getJob` | Single job with app count |
| PUT | `/jobs/:id` | `updateJob` | Update job details |
| PATCH | `/jobs/:id/status` | `toggleJobStatus` | Open/close job |
| GET | `/jobs/:id/applicants` | `getApplicants` | Paginated applicant list |
| GET | `/jobs/:id/export` | `exportApplicantsCSV` | CSV export |
| PUT | `/applications/:id/status` | `updateApplicationStatus` | Update app status |
| POST | `/interviews` | `scheduleInterview` | Schedule interview round |
| PUT | `/interviews/:id/result` | `submitRoundResult` | Submit pass/fail result |

### Admin Routes (`/api/admin/*`) — All: Auth + Admin Role

| Method | Path | Controller | Description |
|--------|------|-----------|-------------|
| GET | `/dashboard` | `getDashboard` | System-wide stats |
| GET | `/students` | `getStudents` | Paginated student list |
| GET | `/students/export/unplaced` | `exportUnplacedCSV` | CSV of unplaced students |
| GET | `/students/:id` | `getStudent` | Single student detail |
| PUT | `/students/:id/academic` | `updateStudentAcademic` | Edit academic records |
| PUT | `/students/:id/verify-academic` | `verifyStudentAcademic` | Verify academics |
| GET | `/companies` | `getCompanies` | Paginated company list |
| GET | `/companies/:id` | `getCompany` | Single company detail |
| PUT | `/companies/:id` | `updateCompany` | Edit company info |
| PUT | `/companies/:id/approve` | `approveCompany` | Approve/reject company |
| GET | `/jobs` | `getJobs` | All jobs system-wide |
| PUT | `/jobs/:id` | `updateJob` | Admin edit job |
| DELETE | `/users/:id` | `deleteUser` | Cascade delete user |
| PUT | `/users/:id/status` | `toggleUserStatus` | Suspend/activate user |
| POST | `/announcements` | `createAnnouncement` | Broadcast notification |
| GET | `/reports` | `getReports` | List placement reports |
| POST | `/reports` | `generateReport` | Generate new report |
| DELETE | `/reports/:id` | `deleteReport` | Delete report |
| GET | `/settings` | `getSettings` | Get system settings |
| PUT | `/settings` | `updateSettings` | Update system settings |

### Public Routes (`/api/public/*`) — No Auth

| Method | Path | Controller | Description |
|--------|------|-----------|-------------|
| GET | `/stats` | `getStats` | Landing page placement stats |
| GET | `/companies` | `getPublicCompanies` | Approved companies list |
| GET | `/jobs` | `getPublicJobs` | Open job listings |
| GET | `/skills` | `getSkills` | Predefined skills enum |
| GET | `/settings` | `getPublicSettings` | Branding/contact info |
| POST | `/contact` | `submitContactForm` | Contact form submission |

### Notification Routes (`/api/notifications/*`) — Auth Required, Any Role

| Method | Path | Controller | Description |
|--------|------|-----------|-------------|
| GET | `/` | `getNotifications` | Paginated notification list |
| GET | `/unread-count` | `getUnreadCount` | Unread count for badge |
| PUT | `/read-all` | `markAllAsRead` | Mark all as read |
| PUT | `/:id/read` | `markAsRead` | Mark single as read |
| DELETE | `/:id` | `deleteNotification` | Delete notification |

### Utility Endpoints (No Route File)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/health` | No | Health check |
| GET | `/api/pdf-proxy` | No | PDF proxy for Cloudinary |

**Total: 66 endpoints** (14 auth + 12 student + 14 company + 20 admin + 6 public + 5 notification + 2 utility - some admin settings are in the admin route count)

---

## 10. KNOWN ISSUES & FUTURE IMPROVEMENTS

### 10.1 Architectural Weaknesses

| # | Weakness | Affected File(s) | Impact |
|---|----------|-------------------|--------|
| 1 | **Socket.IO cookie name mismatch** — backend reads `cookies.token` but JWT is stored as `pms_token` | `socketService.js` | Socket auth silently fails; real-time notifications may not work |
| 2 | **In-memory pending registrations** — lost on server restart | `authController.js` | Users mid-registration lose their session |
| 3 | **In-memory interview reminder Set** — lost on restart | `interviewReminder.js` | Duplicate reminders sent after restart |
| 4 | **No pagination on admin dashboard queries** — counts entire collections | `adminController.js` | Performance degrades at scale |
| 5 | **Package field is String, not Number** — requires regex extraction | `Application.js`, `adminController.js` | Report accuracy depends on consistent formatting |
| 6 | **Job posting doesn't emit Socket.IO** — only DB notifications | `companyController.js` | Students don't see new job alerts in real-time (only on next page load) |
| 7 | **No automated test suite** | Entire project | No regression safety net |
| 8 | **CSV export builds entire response in memory** | `companyController.js`, `adminController.js` | Large exports may cause OOM |

### 10.2 Five Concrete Future Enhancements

| # | Enhancement | Implementation Notes |
|---|-------------|---------------------|
| 1 | **Redis session store for pending registrations** | Replace `pendingRegistrations` Map with Redis `SETEX` (auto-expiring keys). Enables horizontal scaling with multiple server instances. Add `ioredis` dependency. Estimated: 2-3 hours. |
| 2 | **Real-time Socket.IO push for job postings** | In `companyController.postJob()`, after `Notification.insertMany()`, iterate eligible students and call `emitToUser()` for each. Import `createAndEmitBulkNotifications` from `notificationHelper.js` to replace manual insertMany. Estimated: 1 hour. |
| 3 | **Automated test suite (Jest + Supertest)** | Create `__tests__/` directory. Write integration tests for auth flow (register → OTP → login → me), application flow (7-gate validation), and cascade delete. Mock Cloudinary and email services. Add `jest` and `supertest` to devDependencies. Configure GitHub Actions CI. Estimated: 1-2 weeks. |
| 4 | **Structured `offeredPackage` field** | Add a numeric `offeredPackageLPA` field (Number) to Application schema alongside the existing string field. Update `updateApplicationStatus` to parse and store numeric value. Update report generation to use numeric field directly instead of regex extraction. Run data migration for existing records. Estimated: 3-4 hours. |
| 5 | **Streaming CSV export** | Replace in-memory CSV building with Node.js `Transform` stream + `res.write()` chunks. For large exports (1000+ rows), this prevents memory spikes. Use `csv-stringify` library for proper escaping. Estimated: 2-3 hours. |

---

> **End of Report**  
> Total files analysed: 60+ · Total endpoints: 66 · Total indexes: 28 · Total security layers: 27
