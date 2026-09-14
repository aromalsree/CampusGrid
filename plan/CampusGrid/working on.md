
# Users  - module
list of all tasks
- Create user modules with AbstractUser
    
- Create login and registration forms and HTMLs
    
- Create user and admin dashboards
    
- Create update, edit, see, and delete views for admin to manage users
    
- Create access control (use groups or role-based)
    
- Create basic views (about, our mission, etc.)

---
# Team Development Task Assignments

This document outlines the project tasks divided among **4 developers**, categorized by task difficulty from **Easy** to **Hard/Advanced**. Each developer is assigned a dedicated package of work with clear descriptions designed for technical implementation. share task and communicate whith eachother also dont forget that the traskes are delegated mean one must work explisitly on that exact task , its jest a quata of what is needed to be build ask each other douts and quests

---

## Aromal S -Developer 1: Core Models, Authentication & Static Views
* **Assigned To:** Developer 1
* **Difficulty Level:** **Easy**
* **Overview:** Build the base user schema and basic public-facing functionality. This task lays the foundation of the project by extending Django's standard user model, configuring authentication forms, and creating baseline static pages.

### Tasks:

- [ ] **Task 1.2:** Implement registration and login forms along with standard authentication views. using django's login logout and
- [ ] **Task 1.3:** Design and implement HTML templates for user registration (`register.html`) and login (`login.html`).
- [ ] **Task 1.4** Setup base.html and form_base html
- [ ] **Task 1.5:** Build basic static pages views and templates (e.g., *About Us*, *Our Mission*).

---

### Gourave Developer 2: Dynamic Dashboards & UI Interfaces
* **Assigned To:** Developer 2
* **Difficulty Level:** **Medium**
* **Overview:** Construct tailored front-end interfaces and dashboard views for different user classes. Ensure logged-in users and site administrators have customized entry points and workflows.
-  **Requarments: ** mast use Re suable dshbord template and exstend capablites
-----

### Tasks:
- [ ] **Task 2.1:** Design and implement the User Dashboard view and HTML template (`user_dashboard.html`).
- [ ] **Task 2.2:** Design and implement the Admin Dashboard view and HTML template (`admin_dashboard.html`).
- [ ] **Task 4.2:** Create administrative User Detail view (`user_detail.html`) to view full user information.
- [ ] **Task 4.3:** Create administrative User Edit view (`user_edit.html`) and user creation workflows for administrators.
- [ ] **Task 2.3:** Integrate conditional dynamic layout elements and navigation links dependent on authentication status and user role.

---

## Aromal P - Developer 3: Role-Based Access Control (RBAC) & Security
* **Assigned To:** Developer 3
* **Difficulty Level:** **Hard**
* **Overview:** Establish robust security layer rules to handle permissions, user groups, and view restrictions across the platform.

### Tasks:
- [ ] **Task 1.1:** Create a custom user model extending `AbstractUser` with required fields (e.g., bio, phone number, profile image).
- [ ] **Task 3.1:** Set up dynamic Role-Based Access Control (RBAC) or standard user groups (e.g., Admin, Manager, Standard User) with granular permission levels.
- [ ] **Task 3.2:** Develop access control decorators or class-based view mixins to restrict routes based on roles.
- [ ] **Task 3.3:** Apply permission checks across all dashboard routes and administration views to block unauthorized access.

---

##  Whoever is free - Developer 4: Full Admin User Management System (CRUD)
* **Assigned To:** Developer 4
* **Difficulty Level:** **mediam**
* **Overview:** Build complete Create, Read, Update, and Delete (CRUD) administrative tools enabling admins to manage user records securely from the custom frontend.
* Tips: create change form 

### Tasks:
- [ ] **Task 4.1:** Develop the administrative User List view featuring search capabilities, filters, and pagination (`user_list.html`).

- [ ] **Task 4.2:** Implement secure User Deletion / Account Deactivation functionality with confirmation prompts.
- [ ] **Task 4.3:** need to set up media and static in debunging
- [ ] fix spelling error in md files 
----
##  Whoever is free - Developer  5 : Media acuarment
* **Assigned To:** Developer 5
* **Difficulty Level:** **mediam**
* **Overview:** ge needed phots , imgs and other media need for the project
* Tips: create change form 

### Tasks:
- [ ] **Task 4.1:** Develop the administrative User List view featuring search capabilities, filters, and pagination (`user_list.html`).

- [ ] **Task 4.4:** Implement secure User Deletion / Account Deactivation functionality with confirmation prompts.
