# Google Workspace Plugin

Google Workspace integration for Claude Code via the [`gws`](https://github.com/googleworkspace/cli) CLI.

**Services:** Gmail, Google Docs, Google Slides, Google Sheets, Google Calendar, Google Drive

## Setup

### Prerequisites

- **Node.js 18+**
- A Google account with Workspace access (e.g. `@redhat.com`)

### Step 1: Install gws

```bash
# Using npm
npm install -g @googleworkspace/cli

# Or with brew (macOS/Linux)
brew install googleworkspace-cli
```

### Step 2: Create a GCP Project

You need your **own** GCP project for OAuth credentials. Do **not** use a shared org project.

1. Go to https://console.cloud.google.com/projectcreate
2. Name it whatever you want (e.g. `username-gws`)
3. For **Parent resource**, select `Default Projects`
4. Click **Create**
5. Note your **Project ID** (the text slug like `jefferyb-gws`, not the numeric Project Number)

### Step 3: Configure OAuth Consent Screen

1. Go to: `https://console.cloud.google.com/apis/credentials/consent?project=YOUR_PROJECT_ID`
2. Select **External** for User Type (this is the "Audience" setting)
3. Set **App name** to anything (e.g. `gws CLI`)
4. Set **Support email** to your Google email
5. Click through and **Save** all steps
6. Go to the **Test users** tab
7. Click **Add users** and add your email

### Step 4: Create OAuth Desktop Credentials

1. Go to: `https://console.cloud.google.com/apis/credentials?project=YOUR_PROJECT_ID`
2. Click **Create Credentials** > **OAuth client ID**
3. Application type: **Desktop app** (this is different from the "External" user type in Step 3)
4. Click **Create**
5. Download the JSON file (`client_secret_*.json`)
6. Save it:

```bash
mkdir -p ~/.config/gws
mv ~/Downloads/client_secret_*.json ~/.config/gws/client_secret.json
```

### Step 5: Enable APIs

Enable each Google API you plan to use. Replace `YOUR_PROJECT_ID` in the URLs below:

| Service | Enable URL |
|---------|-----------|
| Drive | `https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project=YOUR_PROJECT_ID` |
| Docs | `https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=YOUR_PROJECT_ID` |
| Sheets | `https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=YOUR_PROJECT_ID` |
| Gmail | `https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=YOUR_PROJECT_ID` |
| Calendar | `https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview?project=YOUR_PROJECT_ID` |

Click **Enable** on each one. If you skip this, `gws` will return a `403 accessNotConfigured` error with a direct link to enable the missing API.

### Step 6: Login

Do **not** run `gws auth setup` — it tries to automate via gcloud and tends to fail. Use `gws auth login` directly with only the scopes you need:

```bash
# Just Drive
gws auth login -s drive

# Drive + Docs + Sheets
gws auth login -s drive,docs,sheets

# All common services
gws auth login -s drive,docs,sheets,gmail,calendar
```

Keep it under ~25 scopes — Google rejects consent for unverified apps with too many.

When the browser opens:

1. If you see "Google hasn't verified this app" — click **Advanced** > **Go to \<app name\> (unsafe)**. This is expected for testing-mode apps.
2. Select/approve the requested scopes
3. You should see a success message

### Step 7: Verify

```bash
gws drive files list --params '{"pageSize": 5}'
```

You should see your recent Drive files.

## Adding More Scopes Later

If you need to add more services after initial setup:

```bash
gws auth logout
gws auth login -s drive,docs,sheets,gmail,calendar
```

You'll go through the consent flow again with the expanded scope set.

## Common Gotchas

| Error | Cause | Fix |
|-------|-------|-----|
| `Failed to set project` / `validationError` | Using `gws auth setup` | Skip it. Use `gws auth login -s drive` instead |
| Too many scopes / consent rejected | Selected too many scopes | Use `-s` flag to limit: `gws auth login -s drive,docs` |
| `Access blocked` / 403 on login | Not added as test user | Add your email under OAuth consent > Test users |
| `User type: External` not visible | Wrong project (shared org project) | Create your **own** project at console.cloud.google.com/projectcreate |
| `403 accessNotConfigured` | API not enabled | Click the `enable_url` from the error, click Enable, wait 30s |
| Confused by "External" vs "Desktop app" | Two different screens | External = OAuth consent audience. Desktop app = credential type |

## Using with Claude Code

```bash
# Install the plugin
claude plugin install google
```

## Skills

| Skill | Description |
|-------|-------------|
| `gws-gmail` | Send, read, and manage email |
| `gws-gmail-send` | Send an email |
| `gws-gmail-read` | Read a message body by ID |
| `gws-gmail-triage` | Unread inbox summary |
| `gws-gmail-reply` | Reply to a message |
| `gws-gmail-reply-all` | Reply-all to a message |
| `gws-gmail-forward` | Forward a message |
| `gws-gmail-watch` | Watch for new emails (NDJSON stream) |
| `gws-docs` | Read and write Google Docs |
| `gws-docs-write` | Append text to a document |
| `gws-slides` | Read and write presentations |
| `gws-sheets` | Read and write spreadsheets |
| `gws-sheets-read` | Read values from a spreadsheet |
| `gws-sheets-append` | Append rows to a spreadsheet |
| `gws-calendar` | Manage calendars and events |
| `gws-calendar-agenda` | Show upcoming events |
| `gws-calendar-insert` | Create a new event |
| `gws-drive` | Manage files, folders, shared drives |
| `gws-drive-upload` | Upload a file |
