# Backward Compatibility Scenarios: Building Shared Libraries for Multiple Consumers

Real-world stories demonstrating backward compatibility patterns when building libraries consumed by many teams/products.

---

## 🎭 Scenario 1: Runtime Warnings - The Platform Update

**Pattern:** Runtime deprecation with console warnings

### The Story

**Characters:**
- **Platform Team:** You maintain an authentication SDK used by 5,000+ companies
- **Enterprise Corp:** Large client with 200 microservices using your SDK
- **Startup Inc:** New company just integrated your SDK last month

**Situation:**

Your team discovers that Node.js 18 has reached end-of-life and contains security vulnerabilities. You need to drop support, but:
- Enterprise Corp has services still running on Node.js 16 and 18
- Startup Inc just deployed to production using Node.js 18 last week
- 30% of your users are still on Node.js 18 according to telemetry

**The Problem:**

If you immediately require Node.js 20+:
- ❌ Enterprise Corp can't upgrade (too many services, bureaucratic approval needed)
- ❌ Startup Inc's production breaks (they just raised Series A, can't afford downtime)
- ❌ Your GitHub Issues explode with angry users

**Your Solution:**

```typescript
// Version 2.78.0 - Start warning period (3 months before)
function shouldShowDeprecationWarning(): boolean {
  if (typeof process === 'undefined') return false
  
  const version = process.version.match(/^v(\d+)\./)?.[1]
  const majorVersion = parseInt(version || '0', 10)
  
  return majorVersion <= 18
}

if (shouldShowDeprecationWarning()) {
  console.warn(
    `⚠️  DEPRECATION WARNING: Node.js ${process.version} is deprecated.\n` +
    `   Support will be removed in version 2.79.0 (releasing April 2025)\n` +
    `   Please upgrade to Node.js 20+ before then.\n` +
    `   Migration guide: https://docs.yourcompany.com/migration/node20\n` +
    `   Current version still works, but won't receive security updates.`
  )
}
```

**Timeline:**
- **January 2025 (v2.78.0):** Warning added, code still works
- **February-March:** Enterprise Corp schedules upgrade sprints
- **March:** Startup Inc upgrades during maintenance window
- **April 2025 (v2.79.0):** Node.js 18 support removed as a *minor* version bump

**Outcome:**
- ✅ Enterprise Corp had 3 months to plan migration
- ✅ Startup Inc upgraded without emergency
- ✅ Only 5% of users complained (the ones who ignore warnings)
- ✅ Your support tickets decreased after removal (fewer edge cases)

---

## 🎭 Scenario 2: JSDoc @deprecated Tags - The API Rename

**Pattern:** Parameter renaming with dual support

### The Story

**Characters:**
- **Data Team:** You maintain a query builder used by 50+ internal teams
- **Analytics Team:** Built 300+ dashboards using your library
- **Mobile Team:** 3 iOS and Android apps with complex queries
- **External Partners:** 20 companies using your public API

**Situation:**

Your original API used `foreignTable` parameter:
```typescript
query.order('created_at', { foreignTable: 'users' })
```

But you realize:
- The term "foreign table" is confusing (it's about *referenced* tables in JOINs)
- SQL standards use "referenced table"
- New developers keep asking "what's a foreign table?"
- Your documentation is inconsistent

**The Problem:**

If you rename immediately:
- ❌ Analytics Team: 300 dashboards break in production
- ❌ Mobile Team: Need to update 3 apps, submit to app stores, wait for approval
- ❌ External Partners: Some are on annual release cycles
- ❌ Breaking change = major version bump = fragmentation

**Your Solution:**

```typescript
// Support BOTH parameters with deprecation guidance
interface OrderOptions {
  ascending?: boolean
  nullsFirst?: boolean
  /** @deprecated Use `referencedTable` instead. Will be removed in v4.0 */
  foreignTable?: string
  /** Preferred: Specify the referenced table for ordering joined data */
  referencedTable?: string
}

order(column: string, options: OrderOptions = {}): this {
  const {
    ascending = true,
    nullsFirst,
    foreignTable,
    referencedTable = foreignTable, // Fallback to old name
  } = options
  
  // Emit runtime warning in development
  if (foreignTable && process.env.NODE_ENV === 'development') {
    console.warn(
      `⚠️  'foreignTable' is deprecated. Use 'referencedTable' instead.\n` +
      `   File: ${new Error().stack?.split('\n')[2]}`
    )
  }
  
  const table = referencedTable
  // ... implementation
}
```

**Migration Journey:**

**Week 1:** Release v2.5.0 with dual support
```typescript
// Old code still works (no changes needed)
query.order('created_at', { foreignTable: 'users' })

// New code recommended
query.order('created_at', { referencedTable: 'users' })
```

**Month 1-6:** Teams migrate at their own pace
- Analytics Team: Updates dashboards one-by-one during maintenance
- Mobile Team: Updates in next app release cycle (2 months)
- External Partners: Some migrate, others don't (both work!)

**Month 12:** Plan v4.0.0 major release
- Announce: `foreignTable` will be removed in v4.0.0
- Usage telemetry shows: 95% migrated, 5% still using old parameter
- You extend timeline another 6 months for the remaining 5%

**Outcome:**
- ✅ Zero breaking changes for 18 months
- ✅ Teams migrated without pressure
- ✅ TypeScript users saw strikethrough in IDE
- ✅ New developers use correct term from day one
- ✅ Clean removal in v4.0.0 major version

---

## 🎭 Scenario 3: Type-Level Versioning - The Server Upgrade

**Pattern:** API version compatibility through types

### The Story

**Characters:**
- **Platform Team:** You maintain SDK for your company's database service
- **SaaS Customers:** 10,000+ customers on different server versions
- **Enterprise Clients:** Large companies on self-hosted v12 servers
- **Cloud Users:** Newer customers on managed v14 servers

**Situation:**

Your database server has two versions in production:
- **v12:** Used by 60% of customers (stable, released 2 years ago)
- **v14:** Used by 40% of customers (new features, released 6 months ago)

**Key Difference:**
```sql
-- v12: Returns single object for aggregates
SELECT COUNT(*) FROM users;  -- Returns: { count: 100 }

-- v14: Returns array for consistency
SELECT COUNT(*) FROM users;  -- Returns: [{ count: 100 }]
```

**The Problem:**

If you update SDK for v14:
- ❌ Enterprise Clients on v12 servers get wrong types
- ❌ Their TypeScript code breaks: `data.count` vs `data[0].count`
- ❌ Runtime errors in production when types don't match reality

If you keep SDK for v12:
- ❌ Cloud Users can't use new v14 features
- ❌ They get type errors even though their code is correct

**Your Solution:**

```typescript
// User specifies server version in their database types
type DatabaseV12 = {
  __InternalSupabase: {
    PostgrestVersion: '12'
  }
  public: {
    Tables: {
      users: { /* ... */ }
    }
  }
}

type DatabaseV14 = {
  __InternalSupabase: {
    PostgrestVersion: '14'
  }
  public: {
    Tables: {
      users: { /* ... */ }
    }
  }
}

// SDK adapts behavior based on version
export class SupabaseClient<
  Database = any,
  ClientOptions extends { PostgrestVersion: string } = 
    Database extends { __InternalSupabase: { PostgrestVersion: infer V } }
      ? { PostgrestVersion: V }
      : { PostgrestVersion: '12' } // Safe default
> {
  // Type inference changes based on version
  rpc<FnName extends string>(fn: FnName, args: any): 
    ClientOptions['PostgrestVersion'] extends '14'
      ? Promise<Array<Result>>  // v14 returns arrays
      : Promise<Result>          // v12 returns single object
}
```

**Real-World Usage:**

**Enterprise Client (v12 server):**
```typescript
// Their generated types (auto-detected from server)
type Database = {
  __InternalSupabase: { PostgrestVersion: '12' }
  public: { /* schema */ }
}

const supabase = createClient<Database>(url, key)

// Type-safe: v12 behavior
const { data } = await supabase.rpc('get_user_count')
console.log(data.count) // ✅ Correct for v12
```

**Cloud User (v14 server):**
```typescript
// Their generated types
type Database = {
  __InternalSupabase: { PostgrestVersion: '14' }
  public: { /* schema */ }
}

const supabase = createClient<Database>(url, key)

// Type-safe: v14 behavior
const { data } = await supabase.rpc('get_user_count')
console.log(data[0].count) // ✅ Correct for v14
```

**Outcome:**
- ✅ Single SDK supports both server versions
- ✅ Types match actual server behavior
- ✅ Compile-time safety for both versions
- ✅ No runtime version checks needed
- ✅ Users migrate at their own pace
- ✅ Zero breaking changes during transition period

---

## 🎭 Scenario 4: Legacy Package Mirror - The Rebrand

**Pattern:** Publishing under multiple package names

### The Story

**Characters:**
- **Platform Team:** You're rebranding from "AuthCore" to "SecureAuth"
- **Mobile Apps:** 500+ published apps using `@company/authcore`
- **Web Apps:** 2,000+ deployed websites
- **CI/CD Pipelines:** 10,000+ automated builds referencing old package
- **Documentation:** 1,000+ tutorials and blog posts with old install commands

**Situation:**

Your company is rebranding:
- Old: `@company/authcore`
- New: `@company/secureauth`

**The Problem:**

If you stop publishing `@company/authcore`:
- ❌ Mobile apps need updates and App Store approvals (weeks)
- ❌ `npm install` breaks for everyone following old tutorials
- ❌ CI/CD pipelines fail across thousands of projects
- ❌ Junior developers get confused by error messages
- ❌ Stack Overflow answers become outdated

**Your Solution:**

```typescript
// publish-legacy-mirror.ts
async function publishLegacyPackage() {
  const newPackagePath = './packages/secureauth'
  const newPackage = require(`${newPackagePath}/package.json`)
  
  // Create temporary package.json for old name
  const legacyPackage = {
    ...newPackage,
    name: '@company/authcore', // Old name!
    description: newPackage.description + 
      ' (Legacy package name. Use @company/secureauth instead)',
    deprecated: 'This package has been renamed to @company/secureauth. ' +
      'Please update your dependencies. Both packages will be maintained ' +
      'until Dec 2026.',
    repository: {
      ...newPackage.repository,
      directory: 'packages/secureauth'
    }
  }
  
  // Publish identical code under old name
  await publishToNpm(legacyPackage, newPackagePath)
  
  console.log('✅ Published @company/authcore@' + newPackage.version)
  console.log('   (mirror of @company/secureauth)')
}
```

**Migration Timeline:**

**Month 0 (Jan 2025):** Initial Release
```bash
# Both work identically
npm install @company/authcore     # Old name (deprecated)
npm install @company/secureauth   # New name (preferred)
```

**Month 1-12:** Gradual Migration
- New projects: Use `@company/secureauth`
- Existing projects: Can upgrade at their own pace
- npm shows deprecation warning but installs successfully
- Both packages receive updates (automated mirror)

**Migration Experience:**

**Developer sees this:**
```bash
$ npm install @company/authcore

npm WARN deprecated @company/authcore@2.5.0: 
This package has been renamed to @company/secureauth.
Please update your dependencies. Both packages will be 
maintained until Dec 2026.

+ @company/authcore@2.5.0
added 1 package in 2.3s
```

**Easy migration:**
```bash
# Just update package.json
- "@company/authcore": "^2.5.0"
+ "@company/secureauth": "^2.5.0"

# Code stays identical (no imports need changing!)
import { AuthClient } from '@company/secureauth' // was authcore
```

**Month 24 (Dec 2026):** End of Legacy Support
- Final notice: "Last version supporting @company/authcore"
- Analytics show: 98% migrated
- You stop publishing legacy mirror
- Old package remains on npm (immutable) but won't get updates

**Outcome:**
- ✅ Zero downtime during rebrand
- ✅ Developers migrated at their own pace
- ✅ No emergency fixes needed
- ✅ Clear communication timeline
- ✅ 2-year migration window (generous!)

---

## 🎭 Scenario 5: Method Overloading - The Async Callback Problem

**Pattern:** Soft deprecation through type signatures

### The Story

**Characters:**
- **Auth Team:** You maintain authentication SDK
- **E-commerce Platform:** Using your SDK for 2M daily users
- **Banking App:** Highly regulated, security-critical
- **Gaming Studio:** Real-time multiplayer with auth state sync

**Situation:**

Your SDK has this callback system:
```typescript
auth.onAuthStateChange(async (event, session) => {
  // Users started doing database calls here
  await db.logAuthEvent(event)
  await analytics.track(event)
  
  // This can take seconds!
  if (event === 'SIGNED_IN') {
    await loadUserProfile(session.user.id)
    await fetchUserPreferences(session.user.id)
    await syncToThirdParty(session.user.id)
  }
})
```

**The Problem You Discovered:**

The callback runs inside an exclusive lock. Async operations cause **deadlocks**:

```typescript
// Banking App's real incident:
auth.onAuthStateChange(async (event, session) => {
  if (event === 'TOKEN_REFRESHED') {
    // This tries to call getSession() internally...
    await saveSessionToSecureStorage(session)
  }
})

// Meanwhile, auto-refresh tries to acquire the same lock
// DEADLOCK! App freezes for 30 seconds until timeout
```

**Impact:**
- E-commerce: Checkout flows freeze
- Banking: Compliance violations (timeout logs)
- Gaming: Players disconnected mid-game

**But You Can't Break Everyone's Code:**
- All three teams have async callbacks in production
- Removing async support = breaking change
- They need time to refactor

**Your Solution:**

```typescript
/**
 * ⚠️ IMPORTANT: Avoid async callbacks
 * 
 * Async functions can cause deadlocks when they call other auth methods.
 * Use synchronous callbacks and defer async work.
 * 
 * @deprecated Async callbacks will be removed in v3.0. 
 * Use synchronous callbacks instead.
 */
onAuthStateChange(
  callback: (event: AuthChangeEvent, session: Session | null) => Promise<void>
): { data: { subscription: Subscription } }

/**
 * Receive notifications when auth state changes.
 * 
 * ✅ RECOMMENDED: Use synchronous callback
 * 
 * @example
 * ```typescript
 * auth.onAuthStateChange((event, session) => {
 *   // Synchronous updates
 *   updateUI(event, session)
 *   
 *   // Defer async work
 *   queueMicrotask(async () => {
 *     await logToAnalytics(event)
 *   })
 * })
 * ```
 */
onAuthStateChange(
  callback: (event: AuthChangeEvent, session: Session | null) => void
): { data: { subscription: Subscription } }

// Implementation
onAuthStateChange(
  callback: (event: AuthChangeEvent, session: Session | null) => void | Promise<void>
): { data: { subscription: Subscription } } {
  // Runtime detection
  const callbackStr = callback.toString()
  if (callbackStr.includes('async ') || callbackStr.includes('=> Promise')) {
    console.warn(
      '⚠️  DEPRECATION: Async onAuthStateChange callbacks can cause deadlocks.\n' +
      '   Migrate to synchronous callbacks. See: https://docs.example.com/migration/sync-callbacks\n' +
      '   This callback: ' + callback.name || 'anonymous'
    )
  }
  
  // Still works, but warned
  return this._addCallback(callback)
}
```

**Migration Guide Provided:**

```typescript
// ❌ OLD WAY (can deadlock)
auth.onAuthStateChange(async (event, session) => {
  await db.logAuthEvent(event)
  await analytics.track(event)
  await loadUserProfile(session.user.id)
})

// ✅ NEW WAY (safe)
auth.onAuthStateChange((event, session) => {
  // Immediate, synchronous work
  updateAuthUI(event, session)
  
  // Defer async work (non-blocking)
  queueMicrotask(async () => {
    try {
      await db.logAuthEvent(event)
      await analytics.track(event)
      await loadUserProfile(session?.user.id)
    } catch (err) {
      console.error('Background auth task failed:', err)
    }
  })
})

// OR use event queue
auth.onAuthStateChange((event, session) => {
  authEventQueue.push({ event, session })
})

// Process queue separately
async function processAuthEvents() {
  while (true) {
    const item = await authEventQueue.pop()
    await handleAuthEvent(item)
  }
}
```

**Migration Journey:**

**Week 1:** Release v2.8.0 with warnings
- E-commerce: Sees warnings in dev, adds to sprint backlog
- Banking: Triggers compliance review (async in production!)
- Gaming: Notices but deprioritizes (no issues yet)

**Month 2:** Banking hits deadlock in production
- They check logs, see your warning
- Use migration guide to fix in 2 hours
- Crisis averted

**Month 3:** Gaming experiences deadlock during tournament
- 10,000 players affected
- They quickly apply fix using your guide
- Thankful warning existed

**Month 6:** E-commerce finally migrates
- Planned refactor during slow season
- Zero production issues

**Month 12:** Announce v3.0 (1 year away)
- Async support will be removed
- Most teams already migrated
- The few remaining have 12 months

**Year 2:** Release v3.0.0
- Remove async overload
- TypeScript won't allow async callbacks
- 99% of users already compliant

**Outcome:**
- ✅ You prevented countless deadlocks
- ✅ Teams had 2+ years to migrate
- ✅ Clear documentation and examples
- ✅ Major version boundary for removal
- ✅ Ecosystem healthier and more reliable

---

## 🎭 Scenario 6: Optional Field Deprecation - The Metadata Cleanup

**Pattern:** Deprecating fields while keeping them in types

### The Story

**Characters:**
- **Storage Team:** You maintain file storage SDK
- **Photo App:** 50M photos with metadata
- **Document Platform:** 10M business documents
- **Video Service:** Petabytes of video files
- **Security Auditors:** Reviewing your system

**Situation:**

Your file metadata includes `last_accessed_at`:
```typescript
interface FileObject {
  id: string
  name: string
  created_at: string
  updated_at: string
  last_accessed_at: string  // Problem field!
  size: number
  metadata: Record<string, any>
}
```

**The Problem You Discovered:**

`last_accessed_at` causes severe issues:
1. **Performance:** Updating on every file access creates massive DB writes
2. **Privacy:** GDPR lawyers say it's tracking data (needs consent!)
3. **Storage Cost:** Billions of unnecessary timestamp updates
4. **Race Conditions:** Concurrent access causes conflicts

**Server Team's Plan:**
- Stop tracking `last_accessed_at` in new files
- Keep existing data for backward compatibility
- Eventually remove from database (cost savings!)

**Your SDK Challenge:**

Remove from types immediately?
- ❌ Photo App: `file.last_accessed_at` in 500+ components breaks
- ❌ Document Platform: Sorting by "recently viewed" breaks
- ❌ Video Service: Analytics dashboard goes blank

Keep in types forever?
- ❌ New developers use deprecated field
- ❌ Security auditors flag as privacy risk
- ❌ Technical debt accumulates

**Your Solution:**

```typescript
// Phase 1: Mark as deprecated (v2.10.0)
interface FileObject {
  id: string
  name: string
  created_at: string
  updated_at: string
  
  /**
   * @deprecated This field is no longer maintained by the server.
   * For existing files, it may contain the last access time before
   * deprecation (2025-01-15). For new files, it will be null.
   * 
   * Alternative: Implement your own tracking if needed:
   * ```typescript
   * // Track in your own database
   * await db.fileAccess.upsert({
   *   fileId: file.id,
   *   accessedAt: new Date(),
   *   userId: currentUser.id
   * })
   * ```
   * 
   * This field will be removed from types in v4.0.0 (2026).
   */
  last_accessed_at: string | null
  
  size: number
  metadata: Record<string, any>
}

// Add runtime helper
export function isFieldDeprecated(field: string): boolean {
  return field === 'last_accessed_at'
}
```

**Migration Journey:**

**Month 1 (Jan 2025):** Server stops updating field
```typescript
// Photo App's existing code still works
const file = await storage.getFile('avatar.jpg')

// Old code doesn't break
if (file.last_accessed_at) {
  console.log('Last accessed:', file.last_accessed_at)
  // Shows old date (before Jan 2025) or null for new files
}
```

**Month 2:** Teams notice deprecation in IDE

Photo App's developer sees:
```typescript
const file = await storage.getFile('avatar.jpg')
file.last_accessed_at // ⚠️ strikethrough in VS Code
// Hover shows: "@deprecated This field is no longer maintained..."
```

**Month 3-6:** Teams migrate gradually

**Photo App Solution:**
```typescript
// OLD: Relied on last_accessed_at
const recentFiles = files.sort((a, b) => 
  new Date(b.last_accessed_at) - new Date(a.last_accessed_at)
)

// NEW: Implemented own tracking
async function trackFileAccess(fileId: string) {
  await db.fileActivity.create({
    fileId,
    userId: currentUser.id,
    accessedAt: new Date()
  })
}

const recentFiles = await db.fileActivity
  .findMany({ userId: currentUser.id })
  .orderBy('accessedAt', 'desc')
```

**Document Platform Solution:**
```typescript
// They actually didn't need it!
// Switched to using 'updated_at' instead
const recentDocs = docs.sort((a, b) => 
  new Date(b.updated_at) - new Date(a.updated_at)
)
```

**Video Service Solution:**
```typescript
// Implemented sophisticated analytics
class ViewTracker {
  private redis: Redis
  
  async trackView(videoId: string, userId: string) {
    // Real-time tracking with Redis
    await this.redis.zadd(
      `user:${userId}:views`,
      Date.now(),
      videoId
    )
  }
  
  async getRecentlyViewed(userId: string) {
    return await this.redis.zrevrange(
      `user:${userId}:views`,
      0,
      20
    )
  }
}
```

**Year 2 (Jan 2026):** Announce v4.0.0
- Field will be removed from types
- Most teams already migrated
- Server will stop returning field entirely

**Year 3 (Jan 2027):** Release v4.0.0
```typescript
// Field completely removed
interface FileObject {
  id: string
  name: string
  created_at: string
  updated_at: string
  // last_accessed_at removed!
  size: number
  metadata: Record<string, any>
}
```

**Outcome:**
- ✅ Performance improved: 80% reduction in DB writes
- ✅ Privacy compliance: GDPR compliant
- ✅ Cost savings: $100k/month in database costs
- ✅ Teams migrated smoothly over 2 years
- ✅ Better solutions emerged (custom tracking)
- ✅ Zero emergency migrations needed

---

## 🎭 Scenario 7: Monorepo Migration - The Infrastructure Revolution

**Pattern:** Massive internal restructure, zero user impact

### The Story

**Characters:**
- **Platform Team:** 8 developers maintaining 6 separate repos
- **Users:** 50,000 developers across 10,000 companies
- **CI/CD:** Hundreds of pipelines in different repos
- **Release Manager:** Coordinating releases across 6 repos manually

**Situation:**

Your SDK is split across 6 repositories:
```
github.com/company/main-sdk
github.com/company/auth-sdk
github.com/company/database-sdk
github.com/company/storage-sdk
github.com/company/functions-sdk
github.com/company/realtime-sdk
```

**The Pain Points:**

**Platform Team's Weekly Nightmare:**
```bash
# Monday: Need to update shared types
cd ~/auth-sdk
git checkout -b update-types
# Make changes, PR, wait for review...

cd ~/database-sdk
git checkout -b update-types
# Copy-paste same changes, PR, wait...

cd ~/storage-sdk
# Repeat 4 more times... 😭
```

**Version Hell:**
```json
// User's package.json
{
  "dependencies": {
    "@company/main-sdk": "^2.5.0",
    "@company/auth-sdk": "^1.8.2",  // Compatible?
    "@company/database-sdk": "^3.1.0", // Who knows!
    "@company/storage-sdk": "^2.0.5"   // Good luck!
  }
}
```

**Release Coordination Disaster:**
```
Week 1: auth-sdk v1.8.0 released
Week 2: database-sdk v3.1.0 (needs auth-sdk ^1.8.0)
Week 3: main-sdk v2.5.0 (needs both above)
Week 4: Breaking change in auth-sdk v1.9.0
Week 5: database-sdk broken! Emergency fix needed!
Week 6: Users confused, issues pile up
```

**The Problem:**

You want to merge into monorepo, but:
- ❌ Can't break 50,000 developers' workflows
- ❌ Can't change npm package names (too disruptive)
- ❌ Can't force everyone to update install commands
- ❌ Can't break existing CI/CD pipelines
- ❌ Can't invalidate Stack Overflow answers

**Your Solution: The Invisible Migration**

**Step 1: Create Monorepo (Internal Only)**
```bash
# New structure (contributors only see this)
github.com/company/sdk-monorepo/
├── packages/
│   ├── main-sdk/
│   ├── auth-sdk/
│   ├── database-sdk/
│   ├── storage-sdk/
│   ├── functions-sdk/
│   └── realtime-sdk/
├── nx.json
└── package.json
```

**Step 2: Redirect Old Repos**
```markdown
# github.com/company/auth-sdk README.md

⚠️ **This repository has moved!**

`auth-sdk` is now developed in the main monorepo:
👉 https://github.com/company/sdk-monorepo/tree/main/packages/auth-sdk

**For Contributors:**
- Submit PRs to the monorepo
- Issues will be auto-transferred

**For Users:**
- ✅ No action needed!
- `npm install @company/auth-sdk` still works
- Package names unchanged
- Your code works exactly the same
```

**Step 3: Publish from Monorepo**
```typescript
// .github/workflows/publish.yml
name: Publish Packages

on:
  push:
    branches: [main]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Determine which packages changed
      - name: Detect changes
        run: npx nx affected:libs
        
      # Publish each package independently
      - name: Publish auth-sdk
        working-directory: packages/auth-sdk
        run: npm publish
        # Still publishes as @company/auth-sdk!
        
      - name: Publish database-sdk
        working-directory: packages/database-sdk
        run: npm publish
        # Still publishes as @company/database-sdk!
```

**What Users Experience: NOTHING**

**Before Migration:**
```bash
npm install @company/auth-sdk@1.8.0
```

**After Migration:**
```bash
npm install @company/auth-sdk@1.8.1
# Same command!
# Same package name!
# Just better internally!
```

**User's package.json (unchanged):**
```json
{
  "dependencies": {
    "@company/auth-sdk": "^1.8.0"
  }
}
```

**User's imports (unchanged):**
```typescript
import { AuthClient } from '@company/auth-sdk'
// Exactly the same!
```

**Platform Team's New Workflow:**

**Before (6 separate repos):**
```bash
# Update shared type (1 hour of work)
cd auth-sdk && update types && PR
cd database-sdk && update types && PR
cd storage-sdk && update types && PR
cd functions-sdk && update types && PR
cd realtime-sdk && update types && PR
cd main-sdk && update types && PR

# Wait for 6 PRs to be reviewed...
# Merge in specific order to avoid breaking deps...
# Coordinate 6 releases...
```

**After (monorepo):**
```bash
# Update shared type (5 minutes)
cd sdk-monorepo
npx nx run-many --target=build
# All packages use updated types immediately!

git commit -m "Update shared types"
# Single PR, single review, automatic release!
```

**Coordinated Releases (Now Easy):**
```bash
# One command releases all affected packages
npx nx affected --target=publish

# Output:
# ✅ @company/auth-sdk@1.9.0 published
# ✅ @company/database-sdk@3.2.0 published
# ✅ @company/main-sdk@2.6.0 published
# ⏭️  storage-sdk unchanged, skipped
```

**Version Synchronization (Now Possible):**
```json
// All packages share root version
{
  "name": "@company/sdk-monorepo",
  "version": "2.10.0",
  "workspaces": [
    "packages/*"
  ]
}

// Each package inherits or uses compatible version
// packages/auth-sdk/package.json
{
  "name": "@company/auth-sdk",
  "version": "2.10.0", // Now synchronized!
  "dependencies": {
    "@company/shared-types": "2.10.0" // Always compatible!
  }
}
```

**The Outcome (6 Months Later):**

**Platform Team:**
- ✅ Development speed: 3x faster
- ✅ Shared code: Easy to maintain
- ✅ Testing: All packages tested together
- ✅ Release coordination: Automated
- ✅ Breaking changes: Detected automatically
- ✅ Fewer bugs: Integration tests catch issues
- ✅ Happier developers: Less repetitive work

**Users:**
- ✅ Noticed nothing! (Perfect!)
- ✅ Same commands, same imports
- ✅ Better quality (fewer bugs)
- ✅ Faster releases (better DX)
- ✅ Compatible versions (less confusion)

**Metrics:**
- PRs merged: 50% faster
- Release coordination time: 90% reduction
- Version conflicts: 0 (was 5-10/month)
- Cross-package bugs: 80% reduction
- Developer satisfaction: ⭐⭐⭐⭐⭐

---

## 🎭 Scenario 8: Version Synchronization - The Dependency Chaos Solution

**Pattern:** Unified versioning across packages

### The Story

**Characters:**
- **Support Team:** Handling 500 tickets/week about version conflicts
- **Fortune 500 Company:** Using your SDK in 1,000+ services
- **Startup:** Just trying to get started
- **DevOps Engineer:** Managing dependency updates

**The Horror Story (Before):**

**Startup's Onboarding Experience:**
```bash
$ npm install @company/main-sdk

✅ Installed @company/main-sdk@2.5.0

$ npm install @company/database-sdk

❌ ERROR: peer dependency conflict
   @company/main-sdk@2.5.0 requires @company/auth-sdk ^1.7.0
   but @company/database-sdk@3.1.0 requires @company/auth-sdk ^1.9.0
```

**Startup Developer:** "I just want to query a database! 😭"

**Fortune 500's Dependency Update:**
```bash
# Monday: Security patch for auth-sdk
npm update @company/auth-sdk
# ✅ Updated to 1.9.1

# Tuesday: Tests fail!
# database-sdk@3.0.5 incompatible with auth-sdk@1.9.1

# Wednesday: Update database-sdk
npm update @company/database-sdk
# ✅ Updated to 3.1.2

# Thursday: More tests fail!
# main-sdk@2.4.0 incompatible with database-sdk@3.1.2

# Friday: Give up, rollback everything
# Stay on vulnerable version 😰
```

**Support Team's Top 10 Tickets:**
1. "Version X doesn't work with Version Y"
2. "Which versions are compatible?"
3. "npm install fails with peer dependency error"
4. "Can I use auth-sdk 1.8 with database-sdk 3.0?"
5. "What's the migration path from X to Y?"
6. "My tests pass locally but fail in CI"
7. "Which version should I install?"
8. "The docs show version X but npm has Y"
9. "Can't upgrade because of dependency conflicts"
10. "Please provide a compatibility matrix"

**Your Solution: Unified Versioning**

**The Announcement:**
```markdown
## 🎉 Introducing Unified Versioning (v3.0.0)

Starting with v3.0.0, **all packages will share the same version number**.

**Before:**
- @company/main-sdk: 2.5.0
- @company/auth-sdk: 1.9.0
- @company/database-sdk: 3.1.0
- @company/storage-sdk: 2.0.0

**After:**
- @company/main-sdk: 3.0.0
- @company/auth-sdk: 3.0.0
- @company/database-sdk: 3.0.0
- @company/storage-sdk: 3.0.0

### Benefits:
✅ No version conflicts
✅ Easy to know what's compatible
✅ Simpler dependency management
✅ All packages tested together
```

**Startup's New Experience:**
```bash
$ npm install @company/main-sdk@3.0.0
$ npm install @company/database-sdk@3.0.0
$ npm install @company/auth-sdk@3.0.0

# All packages installed successfully! ✅
# All guaranteed compatible! ✅
# Developer happiness! ✅
```

**Fortune 500's New Update Process:**
```bash
# Update all packages at once
npm install @company/main-sdk@3.2.0 \
            @company/auth-sdk@3.2.0 \
            @company/database-sdk@3.2.0

# ✅ All compatible automatically
# ✅ Tests pass
# ✅ Deploy to production
# ✅ No conflicts
```

**Your Release Process:**
```bash
# Monorepo makes this possible
$ npx nx version --releaseAs=minor

✅ Bumped all packages to 3.1.0:
   - @company/main-sdk: 3.0.0 → 3.1.0
   - @company/auth-sdk: 3.0.0 → 3.1.0
   - @company/database-sdk: 3.0.0 → 3.1.0
   - @company/storage-sdk: 3.0.0 → 3.1.0
   - @company/functions-sdk: 3.0.0 → 3.1.0

$ npx nx run-many --target=publish

✅ Published all packages to npm
```

**Migration Strategy:**

**Phase 1: Announce (3 months before)**
```markdown
## Notice: Moving to Unified Versioning

In v3.0.0 (releasing April 2025), all packages will share the same version.

### What You Need to Do:
1. Update all @company packages to 3.x at the same time
2. Don't mix 2.x and 3.x versions

### Migration:
```bash
# ❌ Don't do this
npm install @company/main-sdk@3.0.0 @company/auth-sdk@1.9.0

# ✅ Do this
npm install @company/main-sdk@3.0.0 @company/auth-sdk@3.0.0
```
```

**Phase 2: Provide Migration Tool**
```typescript
// packages/migration-tool/src/check-versions.ts
#!/usr/bin/env node

const packageJson = require('./package.json')
const deps = { ...packageJson.dependencies, ...packageJson.devDependencies }

const companyPackages = Object.entries(deps)
  .filter(([name]) => name.startsWith('@company/'))

const versions = [...new Set(companyPackages.map(([_, version]) => version))]

if (versions.length > 1) {
  console.error('❌ Mixed versions detected:')
  companyPackages.forEach(([name, version]) => {
    console.log(`   ${name}: ${version}`)
  })
  console.log('\n✅ Fix with:')
  console.log('   npm install ' + companyPackages
    .map(([name]) => `${name}@3.0.0`)
    .join(' '))
  process.exit(1)
}

console.log('✅ All @company packages use same version:', versions[0])
```

**Phase 3: Clear Documentation**
```markdown
## Installation Guide

### ✅ Correct Installation
```bash
# Install all packages with same version
npm install @company/main-sdk@3.2.0 \
            @company/auth-sdk@3.2.0 \
            @company/database-sdk@3.2.0
```

### ❌ Common Mistakes
```bash
# DON'T mix versions
npm install @company/main-sdk@3.2.0 \
            @company/auth-sdk@3.0.0  # ❌ Different version
```

### 🔍 Check Your Versions
```bash
npx @company/check-versions
```
```

**The Results (After 6 Months):**

**Support Tickets:**
- Version conflicts: 90% reduction (50/week → 5/week)
- Installation errors: 85% reduction
- "Which version?" questions: 95% reduction
- Overall ticket volume: 60% reduction

**Developer Experience:**
```typescript
// Startup Developer's Twitter:
"Just tried @company's SDK. Install was painless,
versions just work. Why isn't everyone doing unified
versioning? 🤯"

// Fortune 500 DevOps:
"Dependency updates used to take 3 days across our
microservices. Now it's 3 hours. Unified versioning
is a game-changer."

// Frustrated Developer (who upgraded):
"I complained loudly about forced version bumps.
But honestly? Haven't had a single conflict since.
I was wrong. This is better."
```

**Outcome:**
- ✅ Zero version conflicts
- ✅ Easier to support
- ✅ Faster onboarding
- ✅ Simpler documentation
- ✅ Happier developers
- ✅ More predictable releases
- ✅ Reduced support burden

---

## 📚 Key Takeaways

### Principles Applied Across All Scenarios:

1. **Communicate Early and Often**
   - Warnings before breaking changes
   - Clear timelines (6-24 months)
   - Migration guides ready day one

2. **Provide Graceful Transitions**
   - Dual support during migration period
   - Fallback mechanisms
   - Runtime warnings in development

3. **Use Type System as Teaching Tool**
   - `@deprecated` tags for IDE hints
   - Type errors guide to correct API
   - Inference helps detect problems

4. **Respect Different Migration Speeds**
   - Enterprises need time (bureaucracy)
   - Startups need stability (limited resources)
   - Agencies need flexibility (many clients)

5. **Make Breaking Changes in Major Versions**
   - Deprecate in minor/patch versions
   - Remove in next major version
   - Long deprecation windows

6. **Measure Success by User Experience**
   - Zero downtime migrations
   - Clear error messages
   - Reduced support tickets
   - Positive community feedback

### When to Use Each Pattern:

| Pattern | Use When | Timeline |
|---------|----------|----------|
| **Runtime Warnings** | Deprecating runtime behavior | 3-12 months |
| **@deprecated Tags** | Renaming/replacing APIs | 12-24 months |
| **Type Versioning** | Multiple server versions | Indefinite |
| **Legacy Package** | Renaming/rebranding | 12-36 months |
| **Method Overloading** | Dangerous patterns | 12-24 months |
| **Optional Fields** | Removing properties | 12-24 months |
| **Monorepo Migration** | Internal restructure | Invisible |
| **Version Sync** | Multiple related packages | Ongoing |

---

## 🎯 The Golden Rule

**"Breaking changes break trust. Give users time, tools, and guidance."**

Every scenario above shows teams that prioritized **developer experience over short-term convenience**, resulting in:
- Stronger ecosystems
- Loyal users
- Fewer emergencies
- Better software

Your library's success depends on the trust of your users. Backward compatibility is how you earn and keep that trust.

---

# Apollo GraphQL Shared Library – Backward Compatibility Playbook

This section adapts the above patterns specifically for a shared Apollo GraphQL library that exports queries, mutations, fragments, and TypeScript types used by multiple apps/teams.

## ✅ What to Export from the Library

- Queries: `queries/*.ts` exporting `gql` documents with deprecation tags
- Mutations: `mutations/*.ts` with input/output normalization helpers
- Fragments: `fragments/*.ts` with version-aware composition
- Types: `types/schema-vX.ts` with `__InternalGraphQL.SchemaVersion`
- Client wrapper: `client/createClient.ts` that injects deprecation/runtime notices

## 🔧 Version-Aware Types

```ts
// types/schema-v1.ts
export type SchemaV1 = {
  __InternalGraphQL: { SchemaVersion: '1' }
  Query: {
    user: { id: string; name: string }
    posts: Array<{ id: string; title: string }>
  }
  Mutation: {
    createUser: { id: string; name: string }
  }
}

// types/schema-v2.ts
export type SchemaV2 = {
  __InternalGraphQL: { SchemaVersion: '2' }
  Query: {
    user: { id: string; name: string; email: string }
    posts: Array<{
      id: string
      title: string
      author: { id: string; name: string }
    }>
  }
  Mutation: {
    createUser: { id: string; name: string; email: string }
  }
}
```

## 🧩 Deprecating Queries and Fragments (Dual Support)

```ts
// queries/user.queries.ts
import { gql } from '@apollo/client'

/**
 * @deprecated Use `getUserProfile`. Removal: 2026-06-30.
 */
export const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) { id name }
  }
`

export const GET_USER_PROFILE = gql`
  query GetUserProfile($userId: ID!) {
    userProfile(userId: $userId) {
      id
      name
      email
      avatar
      preferences { theme language }
    }
  }
`

export const queries = {
  /** @deprecated */ getUser: GET_USER,
  getUserProfile: GET_USER_PROFILE,
}
```

## 🧱 Fragment Composition (Version-Aware)

```ts
// fragments/user.fragments.ts
import { gql } from '@apollo/client'

export const UserFragmentV1 = gql`
  fragment UserInfo on User { id name email }
`

export const UserFragmentV2 = gql`
  fragment UserInfoV2 on User { id name email avatar createdAt }
`

export function resolveUserFragment(schemaVersion: '1' | '2') {
  return schemaVersion === '2' ? UserFragmentV2 : UserFragmentV1
}
```

## 🧭 Client Wrapper with Runtime Deprecation Notices

```ts
// client/createClient.ts
import { ApolloClient, InMemoryCache } from '@apollo/client'

const DEPRECATED = new Map<string, { reason: string; alternative: string; removeDate: string }>([
  ['GetUser', {
    reason: 'Use GetUserProfile for extended fields and stability.',
    alternative: 'GetUserProfile',
    removeDate: '2026-06-30',
  }],
])

export function createClient(uri: string) {
  const client = new ApolloClient({ uri, cache: new InMemoryCache() })

  return {
    raw: client,
    async query(opts: { query: any; variables?: Record<string, any> }) {
      const opName = opts.query?.definitions?.[0]?.name?.value
      if (DEPRECATED.has(opName)) {
        const d = DEPRECATED.get(opName)!
        console.warn(
          `⚠️  Deprecated GraphQL query "${opName}". ` +
          `Reason: ${d.reason}. Use "${d.alternative}". Removal: ${d.removeDate}.`
        )
      }
      return client.query(opts)
    },
    async mutate(opts: { mutation: any; variables?: Record<string, any> }) {
      return client.mutate(opts)
    },
  }
}
```

## 🔄 Mutation Return Normalization (Backward-Compatible)

```ts
// mutations/user.mutations.ts
import { gql } from '@apollo/client'

export const CREATE_USER_V1 = gql`
  mutation CreateUser($input: CreateUserInput!) { createUser(input: $input) }
`

export const CREATE_USER_V2 = gql`
  mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) { id name email }
  }
`

export async function createUser(client: ReturnType<typeof import('./client/createClient').createClient>, input: any) {
  const res = await client.mutate({ mutation: CREATE_USER_V2, variables: { input } })
  const value = (res.data?.createUser ?? null)
  return typeof value === 'boolean' ? { success: value } : value
}
```

## 📦 Unified Versioning Across GraphQL Packages

- `@company/graphql-queries@X.Y.Z`
- `@company/graphql-mutations@X.Y.Z`
- `@company/graphql-fragments@X.Y.Z`
- `@company/graphql-types@X.Y.Z`

All published with the same version to prevent fragmentation and ensure compatibility.

## 🧰 Migration Guidance (Devs See This)

```md
### Deprecation Policy
- Queries/Mutations: 12–24 months dual support
- Fragments/Fields: GraphQL `@deprecated` + TS JSDoc
- Runtime warnings in dev only
- Major releases remove deprecated APIs after window

### Example Migration
// Old
await client.query({ query: queries.getUser, variables: { id: '123' } })

// New
await client.query({ query: queries.getUserProfile, variables: { userId: '123' } })
```

## 🧪 What to Test

- Deprecated queries still function and warn in dev
- New queries/mutations/fragments are compatible across packages
- Normalizers return consistent shapes (boolean vs object)
- Version-aware fragments resolve correctly for V1/V2
- Unified versioning prevents peer dependency conflicts

---

By exporting queries, mutations, fragments, and types with clear deprecation windows, version-aware behavior, and runtime guidance, a shared Apollo GraphQL library can safely evolve without breaking multiple consumers.
