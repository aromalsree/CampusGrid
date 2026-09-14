# Git Commit Message Format & "Plan, Change, Test, Commit, Push" Workflow

A standardized approach to Git commit messages and daily development workflows ensures clear project history, seamless code reviews, and easier debugging. thes are not enfoused but following would me really help full in debugging

---

## Part 1: Git Commit Message Format for Features

When introducing new functionality to a repository, use the **Conventional Commits** standard with the `feat` and `fix` prefixs.

### Standard Structure

```text
feat(<scope>): <short summary in imperative mood>

fix(<scope>): <short summary in imperative mood>

[optional body]

[optional footer(s)]
```

### Component Breakdown

* **Type (`feat`):** Indicates a new user-facing feature or significant additions to functionality.
* **Scope (Optional):** The specific module, component, or area of the application affected (e.g., `auth`, `dashboard`, `user-model`).
* **Subject (Short Summary):**
  * Use the imperative, present tense: "add" not "added" or "adds".
  * Do not capitalize the first letter.
  * Do not put a period (`.`) at the end.
  * Limit the subject line to 50 characters.
* **Body (Optional):**
  * Include if the feature requires additional context, rationale, or explanation.
  * Wrap lines around 72 characters.
  * Explain *what* changed and *why*, rather than *how*.
* **Footer (Optional):**
  * Mention issue tracker IDs (e.g., `Closes #123`, `Fixes #45`).

---

### Examples for Feature Commits

#### 1. Quick Feature Additions
```text
feat(auth): add abstract user model with custom fields
```
```text
feat(dashboard): create user and admin template views
```

#### 2. Detailed Feature Additions
```text
feat(rbac): implement role-based access control decorators

Add `@role_required` decorator and custom permissions mixin to restrict 
view execution based on user groups (Admin, Manager, Standard).

Closes #42
```

---

## Part 2: The "Plan, Change, Test, Commit, Push" Formula

The **Plan → Change → Test → Commit → Push** framework is a disciplined, cyclical workflow for developing clean and reliable code.

```text
  [ PLAN ] ──> [ CHANGE ] ──> [ TEST ] ──> [ COMMIT ] ──> [ PUSH ]
     ^                                                       |
     └───────────────── Next Feature / Task ─────────────────┘
```

---

### Step-by-Step Execution

#### 1. Plan
Define the specific scope of your feature before writing any code.

* **Actions:**
  * Review issue descriptions or task requirements.
  * Break down large tasks into atomic sub-tasks.
  * Ensure you are on the correct, updated working branch:
    ```bash
    git checkout main
    git pull origin main
    git checkout -b feat/user-authentication
    ```

#### 2. Change
Implement the minimum necessary code to fulfill the planned task.

* **Actions:**
  * Keep modifications isolated to the planned feature scope.
  * Avoid mixing unrelated tasks (e.g., fixing unrelated bugs while adding a feature).

#### 3. Test
Verify that your changes work as intended and do not introduce regressions.

* **Actions:**
  * Run local automated unit/integration tests:
    ```bash
    python manage.py test
    ```
  * Verify functional requirements manually in the development environment.
  * Ensure code formatting and linting pass standards.

#### 4. Commit
Save your verified changes locally using the feature commit message convention.

* **Actions:**
  * Stage relevant files selectively (avoid `git add .` if unintended files are modified):
    ```bash
    git add path/to/changed/files
    ```
  * Write the commit message:
    ```bash
    git commit -m "feat(auth): implement login and registration views"
    ```

#### 5. Push
Upload local commits to the remote repository for review or deployment.

* **Actions:**
  * Push the branch to the remote origin:
    ```bash
    git push -u origin feat/user-authentication
    ```
  * Open a Pull Request (PR) or Merge Request (MR) if working in a team setup.