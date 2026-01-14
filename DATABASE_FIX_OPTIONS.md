# Database Fix - Choose Your Option

## Problem
The Conference model now has a `classification` field, but the database table doesn't have this column yet, causing a 404 error.

## Solution Options

### Option 1: SAFE MIGRATION (RECOMMENDED)
**Use this if you have existing data you want to keep**

```bash
python migrate_db.py
```

**What it does:**
- Adds only the `classification` column to the existing table
- Preserves all existing conferences, submissions, authors, papers
- Sets the new column to `NULL` for existing records
- Takes ~1 second

**Risks:** Minimal - only adds a column, doesn't modify existing data

**When to use:** 
- You have test data you want to keep
- You've been developing and testing the system
- You want to preserve conference records

---

### Option 2: FULL RESET
**Use this only if you have NO important data**

```bash
python reset_db.py
```

**What it does:**
- Deletes the entire `instance/dev.db` file
- Creates a completely new database with updated schema
- Everything is fresh and clean

**Risks:** HIGH - ALL data is permanently deleted:
- ❌ All conferences deleted
- ❌ All submissions deleted
- ❌ All authors deleted
- ❌ All papers deleted
- ❌ All users deleted
- ❌ All rankings deleted
- ❌ All rankings deleted
- ❌ All conference editions deleted

**When to use:**
- You just started and have no test data
- You're testing with dummy data
- Database is completely corrupted and unfixable

---

## My Recommendation

### ✅ Use `migrate_db.py` (Safe Migration)

This is the safer approach because:

1. **Preserves all data** - Everything you've been testing stays intact
2. **Reversible** - If something goes wrong, you still have your data
3. **Production-like** - Real systems use migrations, not full resets
4. **Faster** - Runs in seconds vs creating new tables
5. **Less risky** - Only adds a single column

---

## Step-by-Step Instructions

### Safe Path (Recommended):
```bash
# 1. Run the safe migration
python migrate_db.py

# 2. Start your app
python app.py

# 3. Try the endpoint
# GET /conferences should now work!
```

### Reset Path (Only if no data matters):
```bash
# 1. Run the reset
python reset_db.py

# 2. Start your app
python app.py

# 3. Try the endpoint
# GET /conferences should work!
```

---

## What to Check Before Deciding

Ask yourself:

1. **Do I have test data I want to keep?**
   - If YES → Use migration
   - If NO → Either option works

2. **Have I been testing submissions?**
   - If YES → Use migration
   - If NO → Either option works

3. **Is this a production database?**
   - If YES → NEVER reset, always migrate
   - If NO → You can choose

4. **How much data is in the database?**
   - If ANY amount you care about → Use migration
   - If empty or dummy data → Can reset

---

## Database File Location
`instance/dev.db` - This is what gets deleted/modified

---

## Recommendation Summary

| Scenario | Use | Command |
|----------|-----|---------|
| Have existing data | Migration | `python migrate_db.py` |
| Empty database | Either | `python migrate_db.py` (safer) |
| Starting fresh | Either | `python reset_db.py` (faster) |
| Testing | Migration | `python migrate_db.py` |
| Production | ONLY Migration | `python migrate_db.py` |

---

**Bottom Line**: Use `python migrate_db.py` unless you're 100% sure there's nothing in the database you care about.
