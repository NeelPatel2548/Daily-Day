# PLACEMENT MANAGEMENT SYSTEM (PMS) — COMPREHENSIVE CODEBASE REPORT

> **Version**: 1.0 · **Date**: 19 May 2026 · **Stack**: MongoDB · Express.js · React 18 · Node.js  
> **Purpose**: Viva Examination Technical Reference Document  
> **Total Files Analysed**: 60+ (33 backend, 27+ frontend)

---

## 1. EXECUTIVE SUMMARY

The **Placement Management System (PMS)** is a full-stack web application that digitises the entire campus placement lifecycle — from company registration and job posting to student applications, multi-round interview scheduling, offer management, and placement reporting. It serves three distinct user roles: **Student**, **Company**, and **Admin**.

**Total file count**: ~33 backend files across 8 directories, ~27+ frontend files across 7 directories, plus shared config files (`.env`, `package.json`, `vite.config.js`).

**Key Architectural Decisions**:
1. **Monorepo with separate `server/` and `client/` trees** — simplifies deployment while keeping concerns separated.
2. **JWT in httpOnly cookies** (not localStorage) — mitigates XSS token theft; `sameSite: strict` prevents CSRF.
3. **Two-step OTP login** for students/companies — adds a second authentication factor without requiring a dedicated 2FA app.
4. **In-memory pending registration map** — avoids polluting the database with unverified users; only creates User documents after OTP confirmation.
5. **Singleton SystemSettings model** — provides a centralized, database-driven configuration for placement season rules, branding, and CGPA overrides.
6. **Socket.IO for real-time notifications** — push-based updates to connected clients rather than polling.
7. **Cloudinary for all file storage** — resumes (raw/PDF), profile pictures (image), company logos (image) with automatic transformation pipelines.
8. **Bauhaus design system** — a distinctive geometric, brutalist visual identity applied across all UI components and email templates.

---

## 2. ARCHITECTURE OVERVIEW

### 2.1 Backend–Frontend Connection

| Layer | Technology | Protocol |
|-------|-----------|----------|
| REST API | Express.js → Axios | HTTP/HTTPS with httpOnly cookie auth |
| Real-time | Socket.IO Server → socket.io-client | WebSocket (fallback: long-polling) |
| File Storage | Multer → multer-storage-cloudinary → Cloudinary | HTTPS (Cloudinary SDK) |
| Email | Nodemailer → Gmail SMTP | SMTP over TLS |
| Database | Mongoose ODM → MongoDB Atlas | MongoDB Wire Protocol |

### 2.2 Request Lifecycle

```
Browser → React Component → Axios (withCredentials) → Vite Dev Proxy (/api)
  → Express Router → Rate Limiter → express-validator → protect() middleware
  → authorize(role) → Controller Function → Mongoose Model → MongoDB Atlas
  → Response { success, message, data } → Axios Interceptor → setState → Re-render
```

### 2.3 External Service Integration

| Service | Purpose | Integration Point |
|---------|---------|-------------------|
| **MongoDB Atlas** | Primary database | `server/config/db.js` via Mongoose `connect()` |
| **Cloudinary** | File storage (resumes, images, logos) | `server/middleware/upload.js` via `multer-storage-cloudinary` |
| **Gmail SMTP** | Transactional emails (OTP, reminders, contact) | `server/services/emailService.js` via Nodemailer |
| **Logo.dev API** | Dynamic company logos on landing page | `client/src/pages/LandingPage.jsx` (client-side fetch) |

---

## 3. BACKEND FILE-BY-FILE ANALYSIS

### 3.1 CONFIG

#### `server/config/db.js`
- **Responsibility**: Connects to MongoDB Atlas with retry logic and runs idempotent data migrations.
- **Key Exports**: `connectDB` (async function)
- **Core Logic**: (1) Sets `autoIndex` based on `NODE_ENV` (on in dev, off in prod). (2) Calls `mongoose.connect()` with options: `maxPoolSize: 10`, `serverSelectionTimeoutMS: 5000`, `socketTimeoutMS: 45000`, `family: 4` (force IPv4). (3) Runs Migration 1: adds `academicVerified` fields to legacy students. (4) Runs Migration 2: filters invalid skills from student documents using `$filter` aggregation.
- **Dependencies**: `mongoose`, `../models/Student`, `../utils/constants`
- **Security**: Forces IPv4 to prevent timeout on cloud platforms; production disables autoIndex to prevent blocking.
- **Error Handling**: Catches connection errors, logs them, calls `process.exit(1)`.

#### `server/config/validateEnv.js`
- **Responsibility**: Fail-fast environment variable guard; called at startup before any service initialisation.
- **Key Exports**: `validateEnv` (function)
- **Core Logic**: Checks 10 required env vars (`PORT`, `MONGO_URI`, `JWT_SECRET`, `JWT_EXPIRES_IN`, `EMAIL_USER`, `EMAIL_PASS`, `CLIENT_URL`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`). If any missing, logs each and calls `process.exit(1)`.
- **Dependencies**: None (pure Node.js)
- **Error Handling**: Hard-stop with descriptive console output.

---

### 3.2 ENTRY POINT

#### `server/server.js`
- **Responsibility**: Express app bootstrap, HTTP server creation, Socket.IO init, middleware stack, route mounting, global error handler.
- **Key Exports**: `{ app, httpServer }`
- **Core Logic**: (1) Loads `.env` via dotenv. (2) Validates env vars. (3) Connects to MongoDB. (4) Creates HTTP server. (5) Initialises Socket.IO. (6) Starts interview reminder scheduler. (7) Applies security middleware: `helmet()`, `cors()`, `mongoSanitize()`, `xss()`. (8) Mounts 6 route groups under `/api/*`. (9) Provides `/api/health` endpoint. (10) PDF proxy endpoint at `/api/pdf-proxy` re-serves Cloudinary PDFs with correct `Content-Type: application/pdf`. (11) Global error handler (500 in prod hides stack). (12) 404 catch-all.
- **Dependencies**: `express`, `http`, `dotenv`, `mongoose`, `cors`, `helmet`, `express-mongo-sanitize`, `xss-clean`, `cookie-parser`, all route/service files.
- **Security**: Helmet headers, CORS locked to `CLIENT_URL`, mongo sanitization, XSS clean, body limit 10MB.

---

### 3.3 CONTROLLERS

#### `server/controllers/authController.js` (759 lines)
- **Responsibility**: All authentication flows — register, 2-step OTP login, password reset, forgot password, change password, session check.
- **Key Exports**: `register`, `verifyOTP`, `resendOTP`, `login`, `loginVerify`, `logout`, `forgotPassword`, `verifyResetOTP`, `resetPassword`, `getMe`, `checkEmailExists`, `verifyCurrentPassword`, `sendTempPassword`, `changePassword`
- **Core Logic**:
  - **Register**: Validates input → checks email uniqueness → hashes password (bcrypt 12 rounds) → generates 6-digit OTP → stores in `pendingRegistrations` Map (NOT DB) → sends OTP email. Bypass mode creates user directly.
  - **VerifyOTP**: Looks up pending registration → checks expiry → compares OTP → creates User document (skips pre-save hash since already hashed) → creates role-specific document (Student/Company) → deletes from Map.
  - **Login**: Step 1 validates credentials → Step 2 sends login OTP (5 min expiry, max 5 attempts). Admin bypasses OTP.
  - **Forgot Password**: Two flows — (A) OTP-based reset, (B) Temp password via email with `mustChangePassword` flag.
- **Dependencies**: `crypto`, `bcryptjs`, `express-validator`, User/Student/Company models, `otpService`, `emailService`, `authMiddleware`
- **Security**: OTP attempt limiting (5 max), bcrypt with salt 12, in-memory map cleanup every 15 min, bypass mode disabled in production.
- **Error Handling**: try/catch with standardised `apiResponse` helpers, detailed error logging.

#### `server/controllers/studentController.js` (729 lines)
- **Responsibility**: Student profile management, smart job matching, application submission with 7-gate validation, interview retrieval, offer response.
- **Key Exports**: `getProfile`, `updateProfile`, `uploadResume`, `uploadProfilePicture`, `getEligibleJobs`, `applyToJob`, `getApplications`, `withdrawApplication`, `getInterviews`, `getDashboard`, `getOffers`, `respondToOffer`
- **Core Logic**:
  - **updateProfile**: Whitelists personal vs academic fields. Blocks academic edits if `academicVerified`. Validates phone (10 digits), gender enum, DOB (not future), enrollment (13 digits), CGPA (0-10), percentages (0-100). Sanitizes skills against `SKILLS_LIST`.
  - **getEligibleJobs**: Builds dynamic MongoDB query: `status: open`, deadline not passed, `minCGPA ≤ studentCGPA`, `maxBacklogs ≥ studentBacklogs`, branch filter. Excludes already-applied jobs. Computes skill match scores (strong ≥3, partial ≥1). Sorts by match level then score.
  - **applyToJob**: 7-gate validation: (1) placement season active, (2) not already placed, (3) max applications cap, (4) personal profile complete, (5) academic profile complete, (6) skills non-empty, (7) academic verified. Then checks job open/deadline/eligibility/duplicate.
  - **respondToOffer**: Accept sets `placementStatus: placed`, `placedIn: companyId`. Decline resets if no other accepted offers. Both create notifications for the company.
  - **getDashboard**: Returns stats, upcoming interviews, offers, profile completion score (out of 100 across 5 categories).
- **Dependencies**: All core models, `SystemSettings`, `upload` middleware, `apiResponse`, `constants`
- **Security**: Field whitelisting, academic lock enforcement, server-side re-validation of eligibility.

#### `server/controllers/companyController.js` (666 lines)
- **Responsibility**: Company profile, job CRUD, applicant management, interview scheduling, round results, CSV export.
- **Key Exports**: `getProfile`, `updateProfile`, `uploadCompanyLogo`, `postJob`, `getJobs`, `getJob`, `updateJob`, `toggleJobStatus`, `getApplicants`, `updateApplicationStatus`, `scheduleInterview`, `submitRoundResult`, `getDashboard`, `exportApplicantsCSV`
- **Core Logic**:
  - **postJob**: Requires `isApproved`. Creates Job → queries eligible students → bulk creates Notification documents.
  - **toggleJobStatus**: Close → bulk rejects pending applications, cancels scheduled interviews, notifies students. Open → reopens.
  - **updateApplicationStatus**: Updates status; if `selected`, sets student placement status and creates congratulations notification. If `rejected`, cancels remaining interviews.
  - **submitRoundResult**: If fail → rejects application, cancels remaining rounds.
  - **exportApplicantsCSV**: Builds CSV with proper escaping (commas, quotes, newlines).
- **Dependencies**: Company/Job/Application/Interview/Student/User/Notification models, `upload` middleware

#### `server/controllers/adminController.js` (671 lines)
- **Responsibility**: System-wide management — user CRUD, company approval, academic verification, cascade deletion, report generation, CSV export.
- **Key Exports**: `getDashboard`, `getStudents`, `getStudent`, `updateStudentAcademic`, `verifyStudentAcademic`, `getCompanies`, `getCompany`, `approveCompany`, `updateCompany`, `getJobs`, `updateJob`, `deleteUser`, `toggleUserStatus`, `createAnnouncement`, `generateReport`, `getReports`, `deleteReport`, `exportUnplacedCSV`
- **Core Logic**:
  - **deleteUser**: Full cascade — deletes Student/Company doc → Applications → Interviews → Notifications → Cloudinary assets (resume, profile picture, logo) → User document.
  - **verifyStudentAcademic**: Sets `academicVerified: true`, records who verified and when, notifies student.
  - **generateReport**: Extracts LPA values from string `offeredPackage` field via regex, computes avg/max, branch-wise stats.
  - **createAnnouncement**: Bulk creates notifications for all active users (filterable by role).
- **Security**: Admin-only route guard. Field whitelisting prevents escalation (e.g., cannot set `isApproved` via update endpoint).

#### `server/controllers/publicController.js` (153 lines)
- **Responsibility**: Unauthenticated endpoints for landing page stats, company list, job list, skills enum, public settings, contact form.
- **Key Exports**: `getStats`, `getPublicCompanies`, `getPublicJobs`, `getSkills`, `getPublicSettings`, `submitContactForm`
- **Core Logic**: `submitContactForm` validates inputs → sends Bauhaus-styled admin notification email → sends auto-reply to submitter (best-effort).

#### `server/controllers/settingsController.js` (72 lines)
- **Responsibility**: CRUD for the singleton SystemSettings document.
- **Key Exports**: `getSettings`, `updateSettings`
- **Core Logic**: Whitelists 10 allowed fields. Validates `logoUrl` as valid HTTP/HTTPS URL. Records `lastUpdatedBy`.

#### `server/controllers/notificationController.js` (111 lines)
- **Responsibility**: Notification CRUD — list (paginated), mark read, mark all read, delete, unread count.
- **Key Exports**: `getNotifications`, `markAsRead`, `markAllAsRead`, `deleteNotification`, `getUnreadCount`
- **Security**: All queries scoped to `req.user._id` — users can only access their own notifications.

---

### 3.4 MIDDLEWARE

#### `server/middleware/authMiddleware.js` (86 lines)
- **Responsibility**: JWT verification from httpOnly cookie, RBAC authorization, token generation, cookie setting.
- **Key Exports**: `protect`, `authorize`, `generateToken`, `setTokenCookie`
- **Core Logic**:
  - **protect**: Reads `pms_token` cookie → `jwt.verify()` → loads User from DB → checks `isActive` and `isVerified` → attaches to `req.user`.
  - **authorize(...roles)**: Checks `req.user.role` against allowed roles array.
  - **setTokenCookie**: Sets cookie with `httpOnly: true`, `secure` in production, `sameSite: strict`, 7-day expiry.
- **Security**: Token in httpOnly cookie (not accessible via JS), differentiated error messages for expired vs invalid tokens.

#### `server/middleware/rateLimiter.js` (43 lines)
- **Responsibility**: Three separate rate limiters for different auth operations.
- **Key Exports**: `authLimiter` (20/15min), `otpLimiter` (10/15min), `resendOTPLimiter` (5/hour)
- **Security**: Standard headers enabled, legacy headers disabled. Returns standardised error JSON.

#### `server/middleware/upload.js` (173 lines)
- **Responsibility**: Multer + Cloudinary storage configurations for 3 upload types, plus 2 Cloudinary deletion helpers.
- **Key Exports**: `upload` (alias), `resumeUpload`, `profilePictureUpload`, `companyLogoUpload`, `deleteCloudinaryFile`, `deleteFromCloudinary`
- **Core Logic**:
  - **Resume**: folder `pms-resumes`, PDF only, 5MB limit, `resource_type: raw`.
  - **Profile Picture**: folder `pms-profile-pictures`, JPG/PNG/WEBP, 2MB, `400×400 face-aware crop`, `quality: auto`, `fetch_format: auto`.
  - **Company Logo**: folder `pms-company-logos`, JPG/PNG/WEBP/SVG, 2MB, `300×300 pad with white background`.
  - **deleteCloudinaryFile**: URL-based deletion for resumes (extracts `publicId` from URL path).
  - **deleteFromCloudinary**: `publicId`-based deletion for images.

---

### 3.5 MODELS

#### `server/models/User.js` (102 lines)
- **Fields**: `name`, `email` (unique), `password` (select: false), `role` (enum: student/company/admin), `isVerified`, `isActive`, `profileCompleted`, `profileImageUrl`, `otp`, `otpExpiry`, `otpAttempts`, `otpVerifiedForReset`, `mustChangePassword`
- **Indexes**: `email` (unique, auto), `{ role: 1, isActive: 1 }` (compound)
- **Hooks**: `pre('save')` — hashes password with bcrypt (salt 12) unless `skipHash` flag is set.
- **Methods**: `comparePassword(candidatePassword)` — bcrypt compare.

#### `server/models/Student.js` (157 lines)
- **Fields**: `user` (ref User, unique), `enrollmentNo` (unique, sparse), `branch` (enum 7 values), `phone`, `dob`, `gender`, `address`, `passingYear`, `currentSemester`, `tenthPercentage`, `twelfthPercentage`, `cgpa`, `activeBacklogs`, `skills[]` (validated against SKILLS_LIST), `projects[]`, `certifications[]`, `internshipExperience`, `linkedin`, `github`, `resumeUrl`, `profilePicture` ({url, publicId}), `placementStatus`, `placedIn` (ref Company), `academicVerified`, `academicVerifiedBy`, `academicVerifiedAt`
- **Indexes**: `user` (unique, auto), `{ cgpa: 1, branch: 1, activeBacklogs: 1 }` (eligibility), `{ placementStatus: 1 }`, `{ academicVerified: 1 }`, `{ passingYear: 1 }`

#### `server/models/Company.js` (73 lines)
- **Fields**: `user` (ref User, unique), `name`, `industry`, `location`, `website`, `description`, `tier` (enum: tier1/tier2/mass_recruiter), `hrName`, `hrEmail`, `hrPhone`, `logo` ({url, publicId}), `isApproved`, `isActive`
- **Indexes**: `user` (unique, auto), `{ isApproved: 1 }`, `{ tier: 1 }`

#### `server/models/Job.js` (99 lines)
- **Fields**: `company` (ref Company), `title`, `description`, `requiredSkills[]` (enum SKILLS_LIST), `package`, `jobType` (enum: fulltime/internship), `stipend`, `bondPeriod`, `location`, `minCGPA`, `maxBacklogs`, `eligibleBranches[]`, `openings`, `deadline`, `status` (enum: open/closed/draft)
- **Indexes**: `{ company: 1 }`, `{ status: 1, minCGPA: 1 }`, `{ eligibleBranches: 1 }` (multikey), `{ jobType: 1 }`, `{ createdAt: -1 }`, `{ deadline: 1 }`

#### `server/models/Application.js` (71 lines)
- **Fields**: `student` (ref Student), `job` (ref Job), `company` (ref Company), `resumeUrl`, `status` (enum 6 values), `currentRound`, `remarks`, `offerLetterUrl`, `offeredPackage`, `offerStatus` (enum: pending/accepted/declined/revoked)
- **Indexes**: `{ student: 1, job: 1 }` (unique compound — prevents duplicate applications), `{ job: 1, status: 1 }`, `{ student: 1, status: 1 }`, `{ company: 1 }`

#### `server/models/Interview.js` (85 lines)
- **Fields**: `application` (ref), `student` (ref), `company` (ref), `job` (ref), `roundName`, `roundNumber`, `scheduledAt`, `mode` (online/offline), `venue`, `meetingLink`, `status` (scheduled/completed/cancelled), `result` (pass/fail/pending), `feedback`, `cancelledReason`
- **Indexes**: `{ application: 1 }`, `{ student: 1 }`, `{ company: 1 }`, `{ scheduledAt: 1 }`

#### `server/models/Notification.js` (54 lines)
- **Fields**: `user` (ref User), `title`, `message`, `type` (enum 6 values), `isRead`, `link`
- **Indexes**: `{ user: 1, isRead: 1 }` (unread count), `{ user: 1, createdAt: -1 }` (feed), `{ createdAt: 1 }` (TTL: 90 days auto-delete)

#### `server/models/PlacementReport.js` (43 lines)
- **Fields**: `academicYear`, `branch`, `totalStudents`, `totalPlaced`, `totalApplications`, `avgPackage`, `maxPackage`, `branchWiseStats[]`, `generatedBy` (ref User)
- **No custom indexes** (low-volume collection).

#### `server/models/SystemSettings.js` (110 lines)
- **Fields**: `allowMultipleOffers`, `maxApplicationsPerStudent`, `blockPlacedFromApplying`, `minCGPAOverride`, `placementSeasonActive`, `logoUrl` (validated URL), `companyName`, `contactEmail`, `phone`, `address`, `lastUpdatedBy`
- **Static Method**: `getSettings()` — returns singleton, creates with defaults if not found.
- **Exports**: Model + `DEFAULT_LOGO_URL` constant.

---

### 3.6 ROUTES

#### `server/routes/authRoutes.js` — 12 endpoints under `/api/auth/*`
#### `server/routes/studentRoutes.js` — 11 endpoints under `/api/student/*` (all: `protect + authorize('student')`)
#### `server/routes/companyRoutes.js` — 14 endpoints under `/api/company/*` (all: `protect + authorize('company')`)
#### `server/routes/adminRoutes.js` — 18 endpoints under `/api/admin/*` (all: `protect + authorize('admin')`)
#### `server/routes/publicRoutes.js` — 6 endpoints under `/api/public/*` (no auth)
#### `server/routes/notificationRoutes.js` — 5 endpoints under `/api/notifications/*` (all: `protect`, any role)

---

### 3.7 SERVICES

#### `server/services/emailService.js` (478 lines)
- **Responsibility**: Gmail SMTP transport, Bauhaus-styled HTML email templates.
- **Key Exports**: `sendEmail`, `sendOTPEmail`, `sendInterviewReminderEmail`, `sendTempPasswordEmail`, `buildContactAdminHtml`, `buildContactAutoReplyHtml`
- **Templates**: 6 distinct templates — (1) Registration OTP, (2) Login OTP, (3) Password Reset OTP, (4) Interview Reminder, (5) Contact Admin Notification, (6) Contact Auto-Reply, (7) Temporary Password.
- **Design**: Table-based layout, inline CSS, MSO conditional comments for Outlook compatibility.

#### `server/services/otpService.js` (42 lines)
- **Responsibility**: OTP generation, hashing, and verification.
- **Key Exports**: `generateOTP` (crypto.randomInt 100000-999999), `hashOTP` (bcrypt salt 10), `verifyOTP` (bcrypt.compare), `getOTPExpiry`

#### `server/services/socketService.js` (96 lines)
- **Responsibility**: Socket.IO server init, JWT auth middleware for WebSocket, user room management, targeted emits.
- **Key Exports**: `initSocket`, `emitToUser`, `getIO`, `isUserOnline`
- **Core Logic**: Auth middleware parses JWT from cookie header. Each user joins room `user:{userId}`. Tracks `Map<userId, Set<socketId>>` for multi-device support.

#### `server/services/interviewReminder.js` (108 lines)
- **Responsibility**: Background job that checks for interviews within the next 24 hours and sends reminder notifications + emails.
- **Key Exports**: `checkUpcomingInterviews`, `startInterviewReminders`
- **Core Logic**: Runs on `setInterval` (default 30 min). Queries `Interview.find({ scheduledAt: { $gte: now, $lte: in24Hours }, status: 'scheduled' })`. Uses in-memory `Set` to prevent duplicate reminders. Cleans up when set exceeds 1000 entries.

#### `server/services/notificationHelper.js` (74 lines)
- **Responsibility**: Helper to create notification in DB AND emit via Socket.IO in one call.
- **Key Exports**: `createAndEmitNotification`, `createAndEmitBulkNotifications`

---

### 3.8 UTILS

#### `server/utils/apiResponse.js` (16 lines)
- **Responsibility**: Standardised JSON response envelope.
- **Exports**: `success(res, data, message, statusCode)` → `{ success: true, message, data }`, `error(res, message, statusCode, errors)` → `{ success: false, message, errors }`

#### `server/utils/constants.js` (11 lines)
- **Responsibility**: Shared skills enum (25 skills).
- **Exports**: `SKILLS_LIST` array — JavaScript, Python, Java, C++, C, React, Node.js, Express.js, MongoDB, MySQL, HTML/CSS, Tailwind CSS, TypeScript, PHP, Django, Machine Learning, Data Science, Docker, Git, REST API, GraphQL, AWS, Firebase, Flutter, Android Development.

#### `server/utils/seedAdmin.js` (41 lines)
- **Responsibility**: First-run admin user seeder script (run manually via `node server/utils/seedAdmin.js`).
- **Core Logic**: Connects to DB → checks if `admin@pms.com` exists → creates with password `Admin@123` → exits.
