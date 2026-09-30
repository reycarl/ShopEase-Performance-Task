# ShopEase Performance Task

A server-rendered e-commerce interface built with Django Templates, Django Forms/ModelForms, server-side validation, responsive CSS, and HTMX.

## Requirements covered
- Django 5.x + SQLite
- Session-based cart; no customer accounts required
- Simulated Cash on Delivery / Pay Later
- Product catalog with search, category, sort, pagination and product detail
- Staff product management
- Cart and checkout
- ProductForm + OrderForm
- Philippine mobile validation
- Price/stock range validation
- Cross-field Express-address validation
- Stock validation on add, update and checkout
- 404 handling and stale-cart handling
- HTMX live search/filter/sort, add-to-cart, cart quantity, remove, product delete, checkout errors, shipping total refresh, pagination and loading indicator
- Reusable templates/partials
- Responsive custom CSS
- Product image upload through MEDIA_ROOT/MEDIA_URL

## HTMX hosting reason
HTMX is loaded from its official CDN in `base.html`. The task explicitly permits either a local static copy or CDN hosting. A CDN keeps the project lightweight and avoids adding a JavaScript build step; the application remains server-driven and does not use React, Vue, or another JS framework.

## Setup - Windows PowerShell

```powershell
cd "PATH\TO\ShopEase_Performance_Task"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open http://127.0.0.1:8000/

If PowerShell blocks activation:
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

## Staff area
Open:
http://127.0.0.1:8000/manage/products/

The demo command creates a staff user:
- username: admin
- password: Admin12345!

This is for classroom/demo use only.

## Product images
Images are optional. Product records include an image field and the development server serves `/media/` from `MEDIA_ROOT`.

## Suggested 3-4 minute demo
1. Catalog: search, category, sort, pagination.
2. Product detail: invalid quantity and successful add-to-cart.
3. Staff management: create/edit/delete product and show validation.
4. Cart: change quantity, remove item, observe total.
5. Checkout: trigger invalid phone and Express-address validation.
6. Submit a valid order and show confirmation plus reduced stock.

## Files for submission
- Project folder / GitHub repository
- `requirements.txt`
- This README
- Part 1 analysis: `docs/Part1_Interface_Data_Entry_Analysis.md`
- Reflection: `docs/Reflection.md`
- Screenshots can be placed in `docs/screenshots/`

The task's final submission asks for a Word document with page snippets and a public GitHub link. Prepare that separately after capturing your own screenshots.
