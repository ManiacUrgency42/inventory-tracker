---
layout: default
title: Data Reference
---

# Data Reference

---

## Database

| Property | Value                        |
|----------|------------------------------|
| Engine   | SQLite 3                     |
| File     | `inventory.db` (project root)|
| Tables   | 1 (`items`)                  |

The entire database is a single file. No server process is required.

---

## Table: `items`

| Column        | Type    | Required | Default | Max Length |
|---------------|---------|----------|---------|------------|
| `id`          | INTEGER | —        | auto    | —          |
| `barcode`     | TEXT    | yes      | —       | no limit*  |
| `name`        | TEXT    | yes      | —       | no limit*  |
| `description` | TEXT    | no       | NULL    | no limit*  |
| `quantity`    | INTEGER | no       | 0       | —          |
| `location`    | TEXT    | no       | NULL    | no limit*  |

*SQLite imposes no column-level length limit. Practical limits are noted per field below.

---

## Field Reference

### `id`
- **Type:** INTEGER
- **Behavior:** Auto-incremented primary key. Set by the database. Never set manually.

---

### `barcode`
- **Type:** TEXT
- **Constraint:** UNIQUE, NOT NULL
- **Description:** The barcode string exactly as read by the scanner or typed by the user. Lookup is a case-sensitive exact match (`WHERE barcode = ?`).
- **Recommended max:** 255 characters

Common barcode formats and their lengths:

| Format   | Example          | Length    |
|----------|------------------|-----------|
| EAN-13   | `5901234123457`  | 13 digits |
| EAN-8    | `96385074`       | 8 digits  |
| UPC-A    | `012345678905`   | 12 digits |
| Code 128 | `ABC-1234`       | 1–80 chars|
| QR Code  | any string       | up to 4296 chars |

Barcodes must be stored exactly as scanned. Do not strip leading zeros — `0123` and `123` are different barcodes.

---

### `name`
- **Type:** TEXT
- **Constraint:** NOT NULL
- **Description:** Human-readable item name. Displayed as the page heading on the item view.
- **Recommended max:** 200 characters

---

### `description`
- **Type:** TEXT
- **Constraint:** nullable
- **Description:** Optional free-text description of the item. Displayed below the name on the item view. Renders as plain text.
- **Recommended max:** 1000 characters

---

### `quantity`
- **Type:** INTEGER
- **Default:** `0`
- **Constraint:** nullable (treated as 0 if NULL)
- **Description:** Current stock count. The application does not decrement this automatically on scan — it must be updated manually via the admin panel.
- **Valid range:** 0 and above (no upper limit enforced by the database)

---

### `location`
- **Type:** TEXT
- **Constraint:** nullable
- **Description:** Physical storage location of the item (e.g. `"Shelf 4"`, `"Bin A3"`, `"Lab Cabinet 2"`). Free-form string — no validation or standardization is enforced.
- **Recommended max:** 100 characters

---

## Example Records

```sql
INSERT INTO items (barcode, name, description, quantity, location)
VALUES
  ('5901234123457', 'Widget A',       'Small blue widget, 10mm diameter', 17, 'Shelf 4'),
  ('9780131101630', 'The C Book',     'Kernighan & Ritchie, 2nd ed',       2, 'Bookshelf 1'),
  ('ABC-2024-001',  'Custom Part X',  NULL,                                 5, 'Bin A3');
```

---

## Constraints Summary

| Rule                                  | Enforced by   |
|---------------------------------------|---------------|
| `barcode` must be unique              | SQLite UNIQUE |
| `barcode` and `name` cannot be empty | SQLite NOT NULL + form `required` |
| `quantity` defaults to 0             | SQLite DEFAULT |
| Barcode lookup is case-sensitive      | SQLite default collation |
| No duplicate barcodes                 | SQLite UNIQUE (INSERT fails) |
