# 🩸 RedDrop Application: Advanced Blood Bank & Donor Coordination System

**RedDrop** is a Django-based digital hub designed to optimize blood donation schedules, urgent blood product distribution, and clinical inventory audits. It integrates donor portals, hospital dispatch interfaces, and a fully featured REST API.

---

## 💡 Key Clinical Features

### 1. Dynamic Eligibility Engine
To ensure donor safety and conform to global medical standards, eligibility dates are calculated automatically using biological gender rules:
* **Men (Homme)**: Eligible to donate every **56 days** (8 weeks).
* **Women (Femme)**: Eligible to donate every **84 days** (12 weeks).
* The model exposes `prochain_don()` and `est_eligible()` methods which compute eligibility dynamically relative to their latest registered donation record.

---

### 2. Blood Stock Expiry & Preservation Tracker
Blood products are highly perishable. RedDrop monitors inventory shelf-life to minimize clinical waste:
* **Red Blood Cells (Globules Rouges - GR)**: Expire in **42 days** from collection.
* **Platelets (Plaquettes - PL)**: Expire in **5 days** (requires immediate dispatch warning).
* **Plasma (Plasma - PS)**: Expire in **365 days** (long-term frozen storage).
* Shelf-life calculations are completed during save operations and flagged on medical dashboards.

---

### 3. Emergency Dispatch & Inter-Hospital Stock Transfer
* **Urgent Requests**: Hospitals can broadcast emergency blood shortage alerts (`DemandeUrgente`). Matching donors in the area are notified and can pledge responses.
* **Stock Transfers**: If Hospital A has an acute shortage of O- blood, it can initiate a transfer request (`TransfertStock`) to Hospital B to share available stock.

---

## 📊 Database Models & Flow
```python
# Donors & Centers
Donneur ─── OneToOne ─── User (Auth System)
Hopital ─── OneToOne ─── User (Auth System)

# Donation Operations
Don ──┬── Donneur (Many-to-One)
      └── Hopital (Many-to-One)

# Inventory & Appointment Scheduling
StockSang  ─── OneToOne ─── Don
RendezVous ──┬── Donneur (Many-to-One)
             └── Hopital (Many-to-One)
```

1. **Donneur**: Volunteers tracking blood types (`A+`, `A-`, `B+`, `B-`, `O+`, `O-`, `AB+`, `AB-`) and active status.
2. **Hopital**: Registered medical centers validated by administrators.
3. **DemandeUrgente**: Urgent blood request details (volume required, deadline, description).
4. **Don**: Records details (place, volume, date) of completed donations.
5. **StockSang**: Blood bag records detailing blood groups, statuses (`En test`, `En stock`, `Utilisé`, `Expiré`), and collection dates.
6. **RendezVous**: Donation bookings mapped to centers or campaigns.

---

## 🔌 REST API Developer Documentation

RedDrop comes preconfigured with a Django REST Framework API engine. Developers can integrate mobile applications and clinics using these key endpoints:

### Endpoints Table
| Endpoint | Method | Filters Supported | Description |
| :--- | :--- | :--- | :--- |
| `/reddrop/api/donneur/` | `GET`, `POST` | `groupe_sanguin`, `ville`, `actif` | Lists donors or registers a new volunteer. |
| `/reddrop/api/donneur/<id>/` | `GET`, `PUT` | — | Retrieves donor profiles and eligibility status. |
| `/reddrop/api/hopital/` | `GET` | `ville`, `valide` | Validated medical facilities. |
| `/reddrop/api/demande-urgente/`| `GET`, `POST` | `active`, `groupe_sanguin` | Broadcasts new blood needs. |
| `/reddrop/api/stock-sang/` | `GET` | `groupe_sanguin`, `statut` | Tracks active bag counts. |

---

## 🛠️ Folder Architecture
* 📁 **reddrop**
  * 📄 [models.py](file:///c:/Users/ASUS%20PC/OneDrive/Documents/facult%C3%A9/DSI23/django/venvDjango/mysite2026/reddrop/models.py): Declares eligibility metrics and blood preservation timeframes.
  * 📄 [serializers.py](file:///c:/Users/ASUS%20PC/OneDrive/Documents/facult%C3%A9/DSI23/django/venvDjango/mysite2026/reddrop/serializers.py): DRF class mappings for JSON serialization.
  * 📄 [views.py](file:///c:/Users/ASUS%20PC/OneDrive/Documents/facult%C3%A9/DSI23/django/venvDjango/mysite2026/reddrop/views.py): Handles REST API viewsets, filtering, and donor appointment schedulers.
  * 📄 [forms.py](file:///c:/Users/ASUS%20PC/OneDrive/Documents/facult%C3%A9/DSI23/django/venvDjango/mysite2026/reddrop/forms.py): Form validation.

---
*Created by Ahmed-Affes for the mySite2026 Systems Portfolio.*
