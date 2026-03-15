# Push this project to a new GitHub repo

Run these in your terminal **from the project root** (`/Users/chaoyihe/Documents/demo1_xb_agent`).

If you see an Xcode license error, run `sudo xcodebuild -license` once and accept, then retry.

## Option A: GitHub CLI (if you have `gh` installed)

**First time:** log in so `gh` can create repos and push:

```bash
gh auth login
```

Follow the prompts (browser or token). Then:

```bash
cd /Users/chaoyihe/Documents/demo1_xb_agent

git init
git add -A
git commit -m "Initial commit: Memristor Crossbar Design Assistant"

gh repo create demo1_xb_agent --private --source=. --remote=origin --push
```

To create a **public** repo instead, use `--public` in place of `--private`.

If the repo name is taken, pick another: `gh repo create my-memristor-agent --private --source=. --remote=origin --push`

## Option B: Create repo on GitHub, then push

1. **Create the repo on GitHub**
   - Go to https://github.com/new
   - Repository name: `demo1_xb_agent` (or any name you like)
   - Choose Public or Private
   - Do **not** add a README, .gitignore, or license (this project already has them)
   - Click **Create repository**

2. **Push this project** (replace `YOUR_USERNAME` with your GitHub username):

   ```bash
   cd /Users/chaoyihe/Documents/demo1_xb_agent

   git init
   git add -A
   git commit -m "Initial commit: Memristor Crossbar Design Assistant"

   git remote add origin https://github.com/YOUR_USERNAME/demo1_xb_agent.git
   git branch -M main
   git push -u origin main
   ```

   If you use SSH:
   ```bash
   git remote add origin git@github.com:YOUR_USERNAME/demo1_xb_agent.git
   git branch -M main
   git push -u origin main
   ```

Done. Your project will be at `https://github.com/YOUR_USERNAME/demo1_xb_agent`.
