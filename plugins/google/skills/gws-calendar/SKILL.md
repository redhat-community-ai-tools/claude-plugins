---
name: gws-calendar
description: "Google Calendar: Manage calendars and events."
metadata:
  version: 0.22.0
  openclaw:
    category: "productivity"
    requires:
      bins:
        - gws
    cliHelp: "gws calendar --help"
---

# calendar (v3)

> **PREREQUISITE:** Read `../gws-shared/SKILL.md` for auth, global flags, and security rules. If missing, run `gws generate-skills` to create it.

```bash
gws calendar <resource> <method> [flags]
```

## Helper Commands

| Command | Description |
|---------|-------------|
| [`+insert`](../gws-calendar-insert/SKILL.md) | create a new event |
| [`+agenda`](../gws-calendar-agenda/SKILL.md) | Show upcoming events across all calendars |

## API Resources

### acl

  - `delete` — Deletes an access control rule.
  - `get` — Returns an access control rule.
  - `insert` — Creates an access control rule.
  - `list` — Returns the rules in the access control list for the calendar.
  - `patch` — Updates an access control rule. This method supports patch semantics.
  - `update` — Updates an access control rule.
  - `watch` — Watch for changes to ACL resources.

### calendarList

  - `delete` — Removes a calendar from the user's calendar list.
  - `get` — Returns a calendar from the user's calendar list.
  - `insert` — Inserts an existing calendar into the user's calendar list.
  - `list` — Returns the calendars on the user's calendar list.
  - `patch` — Updates an existing calendar on the user's calendar list. This method supports patch semantics.
  - `update` — Updates an existing calendar on the user's calendar list.
  - `watch` — Watch for changes to CalendarList resources.

### calendars

  - `clear` — Clears a primary calendar. This operation deletes all events associated with the primary calendar of an account.
  - `delete` — Deletes a secondary calendar. Use calendars.clear for clearing all events on primary calendars.
  - `get` — Returns metadata for a calendar.
  - `insert` — Creates a secondary calendar.
  - `patch` — Updates metadata for a calendar. This method supports patch semantics.
  - `update` — Updates metadata for a calendar.

### channels

  - `stop` — Stop watching resources through this channel

### colors

  - `get` — Returns the color definitions for calendars and events.

### events

  - `delete` — Deletes an event.
  - `get` — Returns an event based on its Google Calendar ID.
  - `import` — Imports an event. This operation is used to add a private copy of an existing event to a calendar.
  - `insert` — Creates an event.
  - `instances` — Returns instances of the specified recurring event.
  - `list` — Returns events on the specified calendar.
  - `move` — Moves an event to another calendar, i.e. changes an event's organizer.
  - `patch` — Updates an event. This method supports patch semantics.
  - `quickAdd` — Creates an event based on a simple text string.
  - `update` — Updates an event.
  - `watch` — Watch for changes to Events resources.

### freebusy

  - `query` — Returns free/busy information for a set of calendars.

### settings

  - `get` — Returns a single user setting.
  - `list` — Returns all user settings for the authenticated user.
  - `watch` — Watch for changes to Settings resources.

## Discovering Commands

Before calling any API method, inspect it:

```bash
# Browse resources and methods
gws calendar --help

# Inspect a method's required params, types, and defaults
gws schema calendar.<resource>.<method>
```

Use `gws schema` output to build your `--params` and `--json` flags.
