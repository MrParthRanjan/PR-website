# 🛡️ Security Guidelines

## Critical Rules

### 1. Never Commit .env
```bash
# ❌ WRONG
git add .env

# ✅ CORRECT
# Commit .env.example only
git add .env.example
```

### 2. Environment Variables
```bash
# Create .env from template
cp .env.example .env

# Add your real API keys
API_KEY=your_actual_key
```

### 3. API Keys & Tokens
- 🔑 Store private secrets (e.g. Supabase `service_role` key) in .env only
- 🚫 Never hardcode or commit private secrets
- 🔄 Rotate regularly
- 🗑️ Revoke old tokens

> **Note on Supabase keys:** The Supabase **anon** key in `public/journal.html`
> is *public by design* — it is meant to ship in the browser and is safe to
> commit, **as long as Row Level Security (RLS) is enabled on every table**.
> This is different from the `service_role` key, which grants full access and
> must never appear in client code or the repository.

### 4. Before Each Commit
```bash
# Check for secrets
git diff --cached | grep -i "password\|token\|key"

# If found, remove them!
git reset HEAD filename
# Edit file and remove secrets
git add filename
git commit
```

## File Permissions

```
.gitignore      → Protects secrets ✅
.env            → NEVER commit ✅
.env.example    → Safe to commit ✅
node_modules/   → Auto ignored ✅
```

## Security Checklist

- ✅ .env created from .env.example
- ✅ Real values in .env only
- ✅ No hardcoded credentials
- ✅ .gitignore updated
- ✅ Checked before commit

## If You Leak a Secret

1. Revoke the token/key immediately
2. Create a new one
3. Update .env
4. Force push: `git push -f origin main`

---

Remember: One leaked key = entire account compromised!
