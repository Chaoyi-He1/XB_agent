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

## HTTPS: use a Personal Access Token (not your password)

GitHub does **not** accept your account password for `git push` over HTTPS. Use a **Personal Access Token** as the password:

1. **Create a token**
   - GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**  
   - Or open: https://github.com/settings/tokens
   - **Generate new token (classic)**. Name it (e.g. `git-push`), choose expiry, tick **repo**
   - Generate, then **copy the token** (you won’t see it again).

2. **Push with the token**
   - Run: `git push -u origin main`
   - When prompted for **Password**, paste the **token** (not your GitHub password).

3. **Save the token so you don’t re-enter it** (optional):
   ```bash
   git config --global credential.helper store
   ```
   Next time you push and enter the token, Git will store it. (Use `osxkeychain` on macOS instead of `store` if you prefer the Keychain.)

**Alternative:** use SSH so you don’t need a token: add your SSH key to GitHub, then use the `git@github.com:...` remote and push (no password prompt).

Done. Your project will be at `https://github.com/YOUR_USERNAME/demo1_xb_agent`.
