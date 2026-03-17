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

## Option B: SSH push flow

Use SSH for Git operations so you never need a token or password prompt.

1. **Create the repo on GitHub**
   - Go to https://github.com/new
   - Repository name: `demo1_xb_agent` (or any name you like)
   - Choose Public or Private
   - Do **not** add a README, .gitignore, or license (this project already has them)
   - Click **Create repository**

2. **Add your SSH key to GitHub**
   - If you already have a key, copy the public key from `~/.ssh/id_ed25519.pub` or `~/.ssh/id_rsa.pub`
   - If you do not have one, create it:
     ```bash
     ssh-keygen -t ed25519 -C "your_email@example.com"
     ```
   - Add the public key in GitHub → **Settings** → **SSH and GPG keys** → **New SSH key**

3. **Push this project**
   ```bash
   cd /Users/chaoyihe/Documents/demo1_xb_agent

   git init
   git add -A
   git commit -m "Initial commit: Memristor Crossbar Design Assistant"

   git remote add origin git@github.com:YOUR_USERNAME/demo1_xb_agent.git
   git branch -M main
   git push -u origin main
   ```

   Replace `YOUR_USERNAME` with your GitHub username. If `origin` already exists, use:
   ```bash
   git remote set-url origin git@github.com:YOUR_USERNAME/demo1_xb_agent.git
   ```

Done. Your project will be at `git@github.com:YOUR_USERNAME/demo1_xb_agent.git`.
