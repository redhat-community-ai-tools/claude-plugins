# EP Decomposition Guide

This guide provides the methodology for breaking OSAC Enhancement Proposals into actionable Jira work items.

## EP-to-Epic Mapping

When creating a Jira epic from an approved EP, use these standard mappings:

- **Epic name** = EP title (e.g., "OSAC Networking API")
- **Epic summary** = "Implement [EP title] enhancement proposal"
- **Epic body** = Link to EP file in enhancement-proposals repo + tracking ticket link from EP frontmatter
- **Epic label** = "OSAC" (always applied)
- **Epic project** = "MGMT" (always use this project key)

Example:
```bash
jira epic create \
  --project MGMT \
  --name "OSAC Networking API" \
  --summary "Implement OSAC Networking API enhancement proposal" \
  --body "Tracking epic for EP: enhancement-proposals/enhancements/networking/README.md
Tracking ticket: MGMT-22637" \
  --label OSAC \
  --no-input \
  --raw
```

## Task Extraction Strategy

How to identify sub-tasks from an Enhancement Proposal:

### 1. API/Schema Tasks
Each new protobuf message or service becomes one task.

**Pattern:** Read the "API Extensions" or "Proposal" section, identify each new resource type.

**Example task:** "Define VirtualNetwork proto schema"
- **Scope:** Create message definition in proto/public/osac/public/v1/virtual_network_type.proto
- **Acceptance criteria:** Proto compiles with buf lint passing, includes all fields from EP spec

### 2. Controller/Backend Tasks
Each new reconciliation loop or service handler becomes one task.

**Pattern:** Read "Implementation Details" section, identify backend logic components.

**Example task:** "Implement VirtualNetwork CRUD service"
- **Scope:** Add VirtualNetworks service with Create/Get/List/Update/Delete RPCs
- **Acceptance criteria:** Service handlers implement full CRUD, database schema created

### 3. Integration Tasks
Each cross-repo integration point becomes one task.

**Pattern:** From dependency mapping (see "Dependency Mapping Checklist" below), create tasks for each repo affected.

**Example task:** "Update osac-operator to reconcile VirtualNetwork CRs"
- **Scope:** Add controller in osac-operator that watches VirtualNetwork custom resources
- **Acceptance criteria:** Controller creates fulfillment-service API calls when CR created/updated

### 4. Test Tasks
Each test scope becomes one task (unit tests and integration tests are separate tasks).

**Pattern:** Read "Test Plan" section, create tasks for each test category.

**Example tasks:**
- "Add unit tests for VirtualNetwork service handlers"
- "Add integration tests for VirtualNetwork lifecycle"

### 5. Documentation Tasks
Each documentation update becomes one task.

**Pattern:** Check if EP requires CLAUDE.md updates, README changes, API documentation.

**Example task:** "Update fulfillment-service CLAUDE.md with VirtualNetwork patterns"
- **Scope:** Document VirtualNetwork API conventions, example commands
- **Acceptance criteria:** CLAUDE.md includes VirtualNetwork in Quick Reference section

### 6. Infrastructure Tasks
Any new infrastructure needs from the EP's "Infrastructure Needed" section.

**Pattern:** If EP lists prerequisites (new database tables, Kubernetes CRDs, Ansible playbooks).

**Example task:** "Add VirtualNetwork CRD to osac-operator"
- **Scope:** Create config/crd/virtualnetwork.yaml
- **Acceptance criteria:** CRD installable via kustomize, matches proto schema

## Complexity Assessment Framework

Rate each of these dimensions as **LOW** / **MEDIUM** / **HIGH**:

### Dimension 1: Repos Touched
- **LOW:** 1 repository affected
- **MEDIUM:** 2-3 repositories affected
- **HIGH:** 4+ repositories affected

Check: List all repos that need changes based on dependency mapping.

### Dimension 2: API Surface Change
- **LOW:** No API changes (internal implementation only)
- **MEDIUM:** Additive API changes (new resources, backward-compatible fields)
- **HIGH:** Breaking API changes (field removal, type changes, service renames)

Check: Does the EP modify existing proto definitions in breaking ways?

### Dimension 3: Data Migration
- **LOW:** No database schema changes
- **MEDIUM:** Backward-compatible schema changes (new tables, new columns with defaults)
- **HIGH:** Breaking schema changes (column removal, type changes requiring migration)

Check: Does the EP require database schema modifications?

### Dimension 4: Cross-Service Dependency
- **LOW:** Service is independent (no dependencies on other services)
- **MEDIUM:** Service consumes existing APIs (reads from existing endpoints)
- **HIGH:** Service requires coordinated release (breaking changes, bidirectional dependencies)

Check: Can this be deployed independently or does it require simultaneous updates?

### Dimension 5: Testing Complexity
- **LOW:** Unit tests only (pure functions, mocks)
- **MEDIUM:** Integration tests (requires kind cluster, database)
- **HIGH:** End-to-end tests across services (requires full deployment, multiple repos)

Check: What test infrastructure is needed per the EP's Test Plan section?

### Overall Complexity
Overall complexity = **highest individual dimension rating**

If any dimension is HIGH, the overall complexity is HIGH.

### Output Format
Present complexity assessment as a markdown table:

| Dimension | Rating | Rationale |
|-----------|--------|-----------|
| Repos touched | MEDIUM | fulfillment-service (proto + service) + osac-operator (CRD + controller) |
| API surface change | MEDIUM | Additive API (new VirtualNetwork resource, no breaking changes) |
| Data migration | MEDIUM | New tables for virtual_networks, backward-compatible |
| Cross-service dependency | MEDIUM | Operator consumes fulfillment-service API (existing pattern) |
| Testing complexity | MEDIUM | Integration tests require kind + PostgreSQL |
| **Overall** | **MEDIUM** | Highest individual rating is MEDIUM |

## Dependency Mapping Checklist

For each proposed change, execute these checks to identify cross-repo impacts:

### Check 1: Proto File Impact
**Command:** `rg --type proto "<resource_name>" --files-with-matches`

**Purpose:** Find which proto files define or reference the resource.

**Example:** `rg --type proto "VirtualNetwork" --files-with-matches`

### Check 2: Controller/Reconciler Impact
**Command:** `rg "reconcile.*<Resource>" --type go -l`

**Purpose:** Find which Go controllers reconcile this resource type.

**Example:** `rg "reconcile.*VirtualNetwork" --type go -l`

### Check 3: Package Import Impact
**Command:** `rg "import.*<package_name>" --type go -l`

**Purpose:** Find which repos import the affected package (breaks on API changes).

**Example:** `rg "import.*fulfillment.*v1" osac-operator/ --type go -l`

### Check 4: CRD Sample Impact
**Command:** `find osac-operator/config/samples/ -name "*<resource>*" 2>/dev/null`

**Purpose:** Find existing CRD samples that might need updates.

**Example:** `find osac-operator/config/samples/ -name "*virtualnetwork*"`

### Check 5: Shared Type Impact
**Command:** `rg "<TypeName>" fulfillment-service/proto/ --files-with-matches`

**Purpose:** Identify if type changes affect multiple proto files (shared types).

**Example:** `rg "NetworkClass" fulfillment-service/proto/ --files-with-matches`

### Check 6: Breaking Changes Detection
**Manual check:** Does the EP:
- Remove proto fields?
- Change field types (e.g., string to enum)?
- Rename services or RPCs?
- Change required vs optional fields?

If YES to any: flag as breaking change in dependency map.

### Output Format
Present dependency mapping as a markdown table:

| Repo | Impact | Files | Breaking? |
|------|--------|-------|-----------|
| fulfillment-service | High | proto/public/osac/public/v1/virtual_network_type.proto, proto/public/osac/public/v1/virtual_networks_service.proto | No |
| osac-operator | Medium | config/crd/virtualnetwork.yaml, controllers/virtualnetwork_controller.go | No |
| osac-installer | Low | manifests/fulfillment-service-rbac.yaml (may need VirtualNetwork permissions) | No |

## Task Ordering

Apply this ordering to ensure dependencies are satisfied:

1. **Proto/schema tasks first** (foundation)
   - Define new proto messages and services
   - These are the API contract that other tasks depend on

2. **Backend/handler tasks second** (implementation)
   - Implement service handlers (CRUD operations)
   - Database schema and storage logic
   - Business logic and validation

3. **Controller/operator tasks third** (integration)
   - Wire up Kubernetes controllers
   - Connect operator to backend services
   - Cross-repo integration points

4. **Test tasks fourth** (verification)
   - Unit tests
   - Integration tests
   - End-to-end tests

5. **Documentation tasks last** (documentation)
   - Update CLAUDE.md files
   - Update README files
   - API documentation
   - User guides

**Rationale:** This ordering minimizes blocking dependencies. Proto definitions must exist before backend can implement them. Backend must exist before controllers can call it. Tests verify completed implementation. Docs capture the finished product.

## Example: Breaking Down a Full EP

Given the "OSAC Networking API" EP, here's how tasks would be extracted:

**API/Schema tasks (5 tasks):**
1. Define VirtualNetwork proto schema
2. Define Subnet proto schema
3. Define SecurityGroup proto schema
4. Define PublicIPPool proto schema
5. Define PublicIP proto schema

**Controller/Backend tasks (5 tasks):**
6. Implement VirtualNetworks CRUD service
7. Implement Subnets CRUD service
8. Implement SecurityGroups CRUD service
9. Implement PublicIPPools CRUD service
10. Implement PublicIPs CRUD service

**Integration tasks (3 tasks):**
11. Add VirtualNetwork CRD and controller to osac-operator
12. Add Subnet CRD and controller to osac-operator
13. Add SecurityGroup CRD and controller to osac-operator

**Test tasks (2 tasks):**
14. Add unit tests for networking service handlers
15. Add integration tests for VirtualNetwork/Subnet/SecurityGroup lifecycle

**Documentation tasks (2 tasks):**
16. Update fulfillment-service CLAUDE.md with networking API patterns
17. Update osac-operator CLAUDE.md with networking CRD examples

**Total: 17 tasks ordered by dependency**
