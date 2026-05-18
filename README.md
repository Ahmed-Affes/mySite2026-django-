# 🌟 mySite2026: Multi-Application Django Enterprise Platform

Welcome to **mySite2026**, a powerful, multi-app Django workspace that implements enterprise-level solutions for both e-commerce operations (**Magasin**) and critical healthcare logistics (**RedDrop**). 

This platform showcases robust database relations, sophisticated business logic rules, interactive user dashboards, and integrated REST APIs.

---

## 🚀 Quick Navigation
* [⚙️ Tech Stack & Requirements](#-tech-stack--requirements)
* [📦 App 1: Magasin (Smart E-Commerce & Inventory)](#-app-1-magasin-smart-e-commerce--inventory)
* [🩸 App 2: RedDrop (Blood Bank & Donor Management)](#-app-2-reddrop-blood-bank--donor-management)
* [🛠️ Installation & Virtualenv Setup](#%EF%B8%8F-installation--virtualenv-setup)
* [🌱 Database Seeding & Mock Data](#-database-seeding--mock-data)
* [🌐 PythonAnywhere Deployment](#-pythonanywhere-deployment)

---

## ⚙️ Tech Stack & Requirements

The platform is designed to be lightweight, secure, and ready for production staging:

* **Core Framework**: [Django 5.2.11](https://docs.djangoproject.com/en/5.2/) (Robust, secure, and clean MVC)
* **API Integration**: [Django REST Framework 3.17.1](https://www.django-rest-framework.org/) (Custom serializing & endpoints)
* **Backend Runtime**: Python 3.10+ / 3.13
* **Database**: SQLite (Development) / PostgreSQL-ready
* **Assets**: Bootstrap 5, FontAwesome 6, custom high-fidelity stylesheet configurations

---

## 📦 App 1: Magasin (Smart E-Commerce & Inventory)

The **Magasin** application is a comprehensive B2C e-commerce catalog combined with a back-office B2B inventory replenishment system.

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│     Clients     │ ───> │ Product Catalog  │ <─── │    Employees    │
│ (Order & Cart)  │      │ (Stock Tracking) │      │ (Supplier BDCs) │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

### 💎 Key Features
1. **Multi-Supplier Sourcing**: Products are linked to multiple suppliers with varying purchase prices and shipping lead times (`ProduitFournisseur`).
2. **Smart Restocking & Automatic BDCs**:
   * Generates automatic Purchase Orders (**Bon de Commande - BDC**) when product stock dips below the `stock_minimum`.
   * Automatically groups restock items by supplier and picks the **preferred supplier with the best price**.
3. **Role-Based Workflows**:
   * **Clients**: Browse products, manage a session-based shopping cart, track orders, and write reviews.
   * **Employees**: Update stock status, confirm payments, assign tracking details to shipments, and manage BDC approvals.
   * **Administrators**: Complete system configuration, financial KPI dashboards, and CRUD controls.

### 📊 Magasin Schema Overview
* **Produit**: Core catalog model tracking price, current stock, and safety threshold.
* **Categorie**: Organizes products hierarchically.
* **Fournisseur**: Supplier records containing emails, phones, and addresses.
* **ProduitFournisseur**: The bridge table tracking cost pricing, lead time, and favorite selection flags.
* **Commande & CommandeLigne**: Stores client orders, totals, dates, and shipping lifecycle status (`en_attente`, `confirmee`, `expediee`, `livree`).
* **BonDeCommande & BonDeCommandeLigne**: B2B purchase orders issued to suppliers to replenish depleted stocks.

---

## 🩸 App 2: RedDrop (Blood Bank & Donor Management)

**RedDrop** is a healthcare application designed to bridge the gap between volunteers, blood donors, and medical centers. It offers donor portal dashboards, medical center portals, reservation systems, and real-time inventory management.

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   Donor Portal   │ ───> │  RedDrop Core    │ <─── │ Hospital Portal  │
│ (Eligibility/RDV)│      │  (REST API Engine)│     │(Urgent Requests) │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

### 🩸 Core Modules & Business Logic
1. **Smart Eligibility Engine**: Calculates next donation date based on biological gender:
   * **Men** are eligible every **56 days** (8 weeks).
   * **Women** are eligible every **84 days** (12 weeks).
   * Keeps track of active, active-pending, and non-eligible flags dynamically.
2. **Urgent Request Dispatch**: Hospitals can publish urgent blood bank requests (`DemandeUrgente`) that notify matching donors instantly.
3. **Integrated Blood Bank Inventory**:
   * Monitors blood bags by type (`Globules Rouges`, `Plaquettes`, `Plasma`).
   * **Automatic Shelf-Life Expiry Tracker**:
     * Red Blood Cells: Expires in **42 days**.
     * Platelets: Expires in **5 days** (High Alert!).
     * Plasma: Expires in **365 days**.
4. **Stock Transfer Workflow**: Handles stock sharing requests (`TransfertStock`) between hospitals to balance blood bank deficits.

### 🔌 REST API Endpoints Overview
RedDrop features a built-in REST API powered by Django REST Framework (DRF) for integration with mobile apps and local clinics:

| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/reddrop/api/donneur/` | List all blood donors (supports filtering by group, city, active) |
| **POST** | `/reddrop/api/donneur/` | Register a new blood donor |
| **GET** | `/reddrop/api/donneur/<id>/` | Detailed donor record (checks eligibility status) |
| **GET** | `/reddrop/api/hopital/` | List all validated medical facilities |
| **GET** | `/reddrop/api/demande-urgente/` | Active blood bank requests |
| **GET** | `/reddrop/api/stock-sang/` | Monitor hospital blood stocks |

---

## 🛠️ Installation & Virtualenv Setup

To run this project locally on your system, follow these step-by-step instructions.

### 1. Activate the Virtual Environment
Open **PowerShell** or **Command Prompt** at the repository root and activate the preconfigured virtual environment:

```powershell
# Windows PowerShell
.\Scripts\Activate.ps1

# Windows CMD
.\Scripts\activate.bat
```

### 2. Install Project Dependencies
Use `pip` to install all necessary packages specified in `requirements.txt`:
```bash
cd mysite2026
pip install -r requirements.txt
```

### 3. Initialize the Database & Run Migrations
Generate the SQLite database and create schemas for all applications:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🌱 Database Seeding & Mock Data

No one likes an empty application! Run the automated scripts to populate both apps with a rich database of users, products, orders, donors, hospitals, and blood inventories:

### A. Seed the E-Commerce Store (Magasin)
This script populates suppliers, categories, products, client orders, and purchase orders:
```bash
python seed_data.py
```

### B. Seed the Blood Bank (RedDrop)
This script registers urgent requests, donor history, blood stocks, appointments, and notification alerts:
```bash
python seed_reddrop.py
```

### C. Create Superuser (Admin Dashboard)
Create an admin account to access the administrative dashboard at `/admin`:
```bash
python manage.py createsuperuser
```

Once done, launch the development server:
```bash
python manage.py runserver
```
Visit the local server in your browser: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🌐 PythonAnywhere Deployment

Ready to take your platform online? This project is fully prepared for easy deployment to **PythonAnywhere**:

1. **Git Clone**: Clone your GitHub repository inside the PythonAnywhere console.
2. **Virtualenv**: Set up a virtual environment and run `pip install -r requirements.txt`.
3. **WSGI Setup**: Configure the WSGI script pointing to `mysite2026.settings`.
4. **Collectstatic**: Run `python manage.py collectstatic --noinput` to compile static resource files.
5. **Reload**: Reload the web app and watch your portal go live at `https://<your-username>.pythonanywhere.com/`.

---

## 📁 Repository Structure
Here's a layout of the key directories in the repository:

* 📦 **venvDjango** (Root)
  * 📁 **mysite2026** (Django Application)
    * 📁 **magasin** (E-Commerce module)
    * 📁 **reddrop** (Blood Donor & REST API module)
    * 📁 **templates** (Global HTML layout templates)
    * 📄 **requirements.txt** (Dependency specification)
    * 📄 **seed_data.py** (Magasin mock data populate script)
    * 📄 **seed_reddrop.py** (RedDrop mock data populate script)

---
*Developed with dedication by Ahmed-Affes as part of the Django Enterprise Systems suite.*
