# 🌐 PR Website

Professional Website - Modern Web Development Project

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/MrParthRanjan/PR-website.git
cd PR-website
```

### 2. Install Dependencies
```bash
npm install
```

### 3. (Optional) Environment

This is a **static site** — no `.env` is required to run or deploy it. The only
backend is Supabase, and its config (project URL + **public** anon key) lives
client-side in `public/journal.html`. See `.env.example` for reference. Never put
the Supabase `service_role` key or any private secret in client code.

### 4. Run Development Server
```bash
npm run dev
```

Open browser: `http://localhost:8000`

The server will watch `public/` and reload the page automatically when files change.

## 📁 Project Structure

```
PR-website/
├── public/              # Static files (served)
│   ├── index.html      # Main page
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   ├── images/         # Images
│   └── fonts/          # Web fonts
│
├── src/                # Source code
│   ├── components/     # Reusable components
│   ├── pages/          # Page templates
│   ├── styles/         # Additional styles
│   └── utils/          # Utility functions
│
├── tests/              # Test files
├── docs/               # Documentation
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
├── package.json        # Dependencies
├── README.md           # This file
└── SECURITY.md         # Security guidelines
```

## 🛠️ Development

### Edit Files
```bash
# HTML
nano public/index.html

# CSS
nano public/css/style.css

# JavaScript
nano public/js/main.js
```

### Commit Changes
```bash
git add .
git commit -m "Add feature: description"
git push
```

## 📦 Dependencies

- browser-sync (local dev server with live reload; `npm run dev`)
- See package.json for all dependencies

## 🔒 Security

⚠️ **IMPORTANT:** Read SECURITY.md before committing!

- Never commit .env file
- Never hardcode API keys
- Use .env for all secrets
- Rotate tokens regularly

## 🚀 Deployment

Coming soon! Check docs/DEPLOYMENT.md

## 📞 Support

Questions? Create an issue on GitHub!

---

**Happy Coding! 💻**
