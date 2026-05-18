# 📦 Magasin Application: Enterprise E-Commerce & Inventory Management

The **Magasin** application is a fully integrated B2C e-commerce platform and a B2B back-office stock fulfillment system. It manages the entire product lifecycle from buyer cart checkout to vendor replenishment.

---

## 🎯 System Roles & Permissions
The application implements strict role-based access control (RBAC) to distinguish customer features from administrative tasks:

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│     Client       │    │     Employé      │    │  Administrateur  │
│                  │    │                  │    │                  │
│ • Catalog view   │    │ • Stock Tracking │    │ • All Employee   │
│ • Shopping Cart  │    │ • Manage Orders  │    │ • Delete Access  │
│ • Order History  │    │ • View BDC lists │    │ • System Settings│
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

* **Access Protection**: Secured via custom role-checking decorators (`@login_required`, `@employe_required`, `@admin_required`) and Class-Based View mixins (`EmployeRequiredMixin`, `AdminRequiredMixin`).
* **Dynamic Menus**: Template rendering uses context indicators (`is_admin_user`, `is_employe_user`) to display personalized navbar elements.

---

## 📊 Core Data Models
The data structure is built on relational integrity and tracks both internal stock levels and supplier relationships:

```python
# Product & Sourcing
Produit ──┬── Categorie (Many-to-One)
          └── Fournisseur (Many-to-Many via ProduitFournisseur)

# Order Processing
Commande ──┬── Client (User model, Many-to-One)
           └── CommandeLigne (One-to-Many lines)

# Supplier Replenishment (BDC)
BonDeCommande ──┬── Fournisseur (Many-to-One)
                 └── BonDeCommandeLigne (One-to-Many)
```

1. **Produit**: Stores catalog details, public retail price, current stock, and safety margins (`stock_minimum`).
2. **Categorie**: Standardizes categorization.
3. **Fournisseur**: Details supplier email, phone numbers, and warehousing locations.
4. **ProduitFournisseur**: Bridges products to suppliers, establishing wholesale buy prices and average delivery days.
5. **Commande & CommandeLigne**: Stores client orders, dynamic totals, and order shipping status.
6. **BonDeCommande & BonDeCommandeLigne**: Tracks internal procurement orders created for restock purposes.

---

## 🔄 Core Business Workflows

### 🛒 Client Checkout Lifecycle
1. **Cart Storage**: Session-based cart allows clients to add and update quantities before committing.
2. **Stock Verification**: Checkout validates quantity against live store inventory.
3. **Status Transitions**:
   `en_attente` (Pending Review) ➔ `confirmee` (Stock Reserved) ➔ `en_preparation` (Packaging) ➔ `expediee` (In Transit) ➔ `livree` (Completed)

---

### 🧠 Smart Procurement & Automatic BDCs
When a customer confirms a purchase that drops a product's stock below `stock_minimum`, the system automatically triggers the replenishment engine:

```
[Low Stock Event] ➔ [Fetch Sourcing List] ➔ [Pick Cheapest Preferred Supplier] ➔ [Generate BDC Draft]
```

1. Checks all suppliers registered under `ProduitFournisseur` for that item.
2. Selects the supplier offering the **lowest purchase price** (`prix_achat`) and marked as preferred.
3. Automatically groups all pending items for that specific supplier into a new **Bon de Commande (BDC)** draft.
4. Updates inventories automatically upon employee acceptance and receipt of supplier packages.

---

## 🛠️ View & Directory Architecture
The application uses a hybrid of **Function-Based Views (FBVs)** for stateful flows (cart, registration) and **Class-Based Views (CBVs)** for standard administration tables:

* 📁 **magasin**
  * 📁 [models.py](file:///c:/Users/ASUS%20PC/OneDrive/Documents/facult%C3%A9/DSI23/django/venvDjango/mysite2026/magasin/models.py): Holds databases schemas.
  * 📁 [views.py](file:///c:/Users/ASUS%20PC/OneDrive/Documents/facult%C3%A9/DSI23/django/venvDjango/mysite2026/magasin/views.py): Implements cart actions, supplier lists, and replenishment dashboards.
  * 📁 [urls.py](file:///c:/Users/ASUS%20PC/OneDrive/Documents/facult%C3%A9/DSI23/django/venvDjango/mysite2026/magasin/urls.py): Endpoints map.
  * 📁 [templates/magasin/](file:///c:/Users/ASUS%20PC/OneDrive/Documents/facult%C3%A9/DSI23/django/venvDjango/mysite2026/magasin/templates/magasin/): Form layouts, catalog, checkout success, and printer-friendly purchase orders.

---
*Created by Ahmed-Affes for the mySite2026 Systems Portfolio.*
