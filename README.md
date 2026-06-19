# 🧬 Fingerprint Matching System

A full-stack biometric fingerprint management system with authentication, file storage, and similarity search.

The system allows uploading fingerprint images, storing them in object storage, extracting feature vectors, and performing similarity-based matching using a vector database.

---

# 🚀 Tech Stack

## Frontend
- Angular

## Backend
- FastAPI (Python)

## Database
- PostgreSQL + pgvector

## Storage
- MinIO (S3-compatible object storage)

## Infrastructure
- Docker & Docker Compose

---

# 🧠 System Architecture

```
Angular (Frontend)
        ↓
FastAPI (Backend)
        ↓
PostgreSQL (users + fingerprint vectors)
        ↓
MinIO (image storage)
```

---

# 👥 User Roles

## 🔐 Admin
- Upload fingerprint data
- Add, update, search and delete fingerprint records
- Add, update, search and delete subject records
- Add, update, search and delete user records
- Full access to all endpoints

## 👤 User
- Login required
- Can only view, search and match fingerprint data
- Cannot upload or modify data

---

# 🗄️ Database Schema

## Users Table (Authentication)
- id
- username
- email
- password_hash
- role (admin | user)
- created_at

## Subjects Table (Dataset Identity)
- external_id (from filename grouping)
- name
- age
- address
- city
- country
- created_at

## Fingerprints Table (Biometric Data)
- id
- subject_id (references subjects)
- image_url (MinIO path)
- sex (M | F)
- hand (left | right)
- finger (thumb, index, etc.)
- filename (original image name)
- feature_vector (pgvector)
- created_at
  
---

# 🗄️ Materialzized Views
- mv_gender_stats;
- mv_finger_stats;
- mv_hand_stats;
- mv_country_stats;
- mv_city_stats;
- mv_age_stats;
- mv_age_gender_stats;
- mv_country_gender_stats;
- mv_city_gender_stats;
- mv_user_summary;
- mv_user_roles;
- mv_user_registrations_30d;

## Purpose
Views feed dashboard charts with system data statistics

---

# 🧪 Core Features

## Authentication
- JWT-based login system
- Role-based access control

## Fingerprint System
- Upload fingerprint images
- Store images in MinIO
- Extract feature vectors
- Similarity search using pgvector
- Exact matching through minutiea
- Visualization of matching points

## Storage
- MinIO bucket-based file storage

---

# 🐳 Running the Project

## 1. Clone repository
```bash
git clone https://github.com/Hilms/Fingerprint-Matching-System.git
cd project
```

## 2. Start system
```bash
docker compose up --build
```

---

# 🌐 Access Points

| Service | URL |
|--------|-----|
| Frontend (Angular) | http://localhost:4200 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001 |

---

# 🔐 API Security

- JWT authentication required
- Role-based access control:
    - admin → full access
    - user → view, search, match fingerprint data

---

# 🧬 Fingerprint Matching

The system uses vector similarity search:

- Fingerprints preproccessed and converted into correlation/intesity feature vectors
- Stored using pgvector in PostgreSQL
- Queries return closest matches using distance metrics (prefilter)
- Candidatedets will then matched by extracting fingerprint landmark points (minutiae)

---

# 📦 Storage System

- Images stored in MinIO bucket: `fingerprints`
- Backend stores only object URL in database
- Images are retrieved via MinIO API

---

# 📌 Project Purpose

A secure biometric system where:
- Admins manage systemdata data
- Users can view, search, match fingerprints
- System uses vector-based and minutiae based similarity matching
- Everything runs in a Dockerized microservice architecture
```
```
