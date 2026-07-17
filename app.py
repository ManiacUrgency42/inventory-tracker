from pathlib import Path

import markdown
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import database

app = FastAPI(docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory="templates")

database.init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/scan")
def scan(barcode: str = Form(...)):
    return RedirectResponse(f"/item/{barcode.strip()}", status_code=302)


@app.get("/item/{barcode}", response_class=HTMLResponse)
def get_item(request: Request, barcode: str):
    conn = database.get_connection()
    cur = database.get_cursor(conn)
    cur.execute("SELECT * FROM items WHERE barcode = %s", (barcode,))
    item = cur.fetchone()
    cur.close()
    conn.close()
    return templates.TemplateResponse(
        request=request, name="item.html", context={"item": item, "barcode": barcode}
    )


# ── Admin ──────────────────────────────────────────────────────────────────────

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, q: str = ""):
    conn = database.get_connection()
    cur = database.get_cursor(conn)
    if q:
        like = f"%{q}%"
        cur.execute(
            """SELECT * FROM items
               WHERE barcode ILIKE %s OR name ILIKE %s OR description ILIKE %s OR location ILIKE %s
               ORDER BY name""",
            (like, like, like, like),
        )
    else:
        cur.execute("SELECT * FROM items ORDER BY name")
    items = cur.fetchall()
    cur.close()
    conn.close()
    return templates.TemplateResponse(
        request=request, name="admin.html", context={"items": items, "q": q}
    )


@app.post("/admin/add")
def admin_add(
    barcode: str = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    quantity: int = Form(0),
    location: str = Form(""),
):
    conn = database.get_connection()
    cur = database.get_cursor(conn)
    cur.execute(
        "INSERT INTO items (barcode, name, description, quantity, location) VALUES (%s, %s, %s, %s, %s)",
        (barcode.strip(), name.strip(), description.strip(), quantity, location.strip()),
    )
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/admin", status_code=302)


@app.get("/admin/edit/{item_id}", response_class=HTMLResponse)
def admin_edit(request: Request, item_id: int):
    conn = database.get_connection()
    cur = database.get_cursor(conn)
    cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
    item = cur.fetchone()
    cur.close()
    conn.close()
    return templates.TemplateResponse(
        request=request, name="admin_edit.html", context={"item": item}
    )


@app.post("/admin/edit/{item_id}")
def admin_update(
    item_id: int,
    barcode: str = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    quantity: int = Form(0),
    location: str = Form(""),
):
    conn = database.get_connection()
    cur = database.get_cursor(conn)
    cur.execute(
        """UPDATE items
           SET barcode=%s, name=%s, description=%s, quantity=%s, location=%s
           WHERE id=%s""",
        (barcode.strip(), name.strip(), description.strip(), quantity, location.strip(), item_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/admin", status_code=302)


@app.post("/admin/delete/{item_id}")
def admin_delete(item_id: int):
    conn = database.get_connection()
    cur = database.get_cursor(conn)
    cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
    conn.commit()
    cur.close()
    conn.close()
    return RedirectResponse("/admin", status_code=302)


# ── Docs ───────────────────────────────────────────────────────────────────────

@app.get("/docs", response_class=HTMLResponse)
def docs_index(request: Request):
    return templates.TemplateResponse(request=request, name="docs_index.html")


_DOC_TITLES = {"user": "User Guide", "dev": "Developer Guide", "data": "Data Reference"}

@app.get("/docs/{section}", response_class=HTMLResponse)
def docs_section(request: Request, section: str):
    if section not in _DOC_TITLES:
        return HTMLResponse("Not found", status_code=404)
    content = Path(f"docs/{section}.md").read_text()
    body = markdown.markdown(content, extensions=["tables", "fenced_code"])
    return templates.TemplateResponse(
        request=request, name="docs_page.html",
        context={"body": body, "section": section, "title": _DOC_TITLES[section]},
    )
