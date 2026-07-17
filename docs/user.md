# User Guide

---

## Scanning Items

1. Open **http://localhost:8080** in your browser
2. Point your barcode scanner at an item and pull the trigger
3. The item's details appear instantly

The input field is always auto-focused — you don't need to click anything between scans.

If you don't have a scanner, type the barcode manually and press **Enter**.

---

## When an Item Isn't Found

You'll see a "Not found" message with the scanned barcode. This means:

- The item hasn't been added to the database yet
- The barcode was misread — try scanning again
- The wrong side of the item was scanned

Ask your inventory maintainer to add the item via the Admin panel.

---

## Admin Panel

Go to **http://localhost:8080/admin**

### Search

Type any part of a name, barcode, description, or location into the search bar. Results filter as you submit. Click **Clear** to reset.

### Add an Item

Fill in the row at the bottom of the page and click **Add**. Only **Barcode** and **Name** are required.

### Edit an Item

Click **Edit** on any row, update the fields, and click **Save**.

### Delete an Item

Click **Delete** on any row. A confirmation dialog will appear — click **Delete** again to confirm, or **Cancel** to go back.

---

## Tips

- Barcodes are exact matches — a trailing space or extra digit will return "not found"
- Quantity and Location are free-form fields; use whatever convention your team agrees on
- The scanner page and admin panel work on any device on the same network
