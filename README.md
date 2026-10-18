# E-Commerce API (Flask)

A REST API for an online store backend, built with Flask and SQLAlchemy. It covers user registration and login, a product catalogue, shopping carts, wishlists and order placement, with JWT authentication and per-user authorization.

I built this while learning backend development. I started with plain CRUD routes, then reworked the data model, security and tests until it behaved like a real store backend. The "Design decisions" and "Known limitations" sections below explain the choices I made and what I'd improve next.

## Tech stack

- **Python 3 / Flask**: routing, blueprints, error handlers
- **SQLAlchemy** (Flask-SQLAlchemy): ORM and relational models
- **Flask-JWT-Extended**: token-based authentication
- **Marshmallow**: input validation and serialization (currently on products)
- **SQLite** for development and tests
- **pytest**: 19 automated tests

## Getting started

```bash
git clone https://github.com/Liu-Yagami/ecommerce-api-flask.git
cd ecommerce-api-flask

python -m venv venv
# Windows:      .\venv\Scripts\Activate.ps1
# macOS/Linux:  source venv/bin/activate

pip install -r requirements.txt
```

Create your environment file by copying `.env.example` to `.env`, then set a real secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the output as `JWT_SECRET_KEY` in `.env`. The app refuses to start without it.

Run the API:

```bash
python app.py
```

It runs at `http://127.0.0.1:5000` and creates the SQLite database on first start.

## Running the tests

```bash
pip install -r requirements-dev.txt
python -m pytest -v
```

The tests use a fresh in-memory database for every test, so they never touch your development data.

## Quick walkthrough

**1. Register and log in**

```http
POST /users
{ "first_name": "Ada", "last_name": "Lovelace", "username": "ada",
  "email": "ada@example.com", "password": "a-strong-password" }

POST /login
{ "username": "ada", "password": "a-strong-password" }
→ { "access_token": "eyJ..." }
```

Send the token on later requests as `Authorization: Bearer <token>`.

**2. Place an order**

```http
POST /orders
{ "items": [ { "product_id": 1, "quantity": 3 },
             { "product_id": 2, "quantity": 1 } ] }
→ 201 { "message": "Order created successfully", "order_id": 1 }

GET /orders/1
→ { "id": 1, "status": "pending", "total_price": "105.47",
    "items": [ { "product_id": 1, "quantity": 3, "price_at_purchase": "19.99" }, ... ] }
```

The request never includes a user ID. The server identifies the user from the token.

## Endpoints

| Method | Route | Access | Description |
|---|---|---|---|
| POST | `/users` | Public | Register |
| POST | `/login` | Public | Log in, returns a JWT |
| GET / PUT / DELETE | `/users/<id>` | Own account only | Read, update or delete a profile |
| GET / POST | `/users/<id>/wishlist` | Own account only | List or add wishlist items |
| DELETE | `/users/<id>/wishlist/<product_id>` | Own account only | Remove a wishlist item |
| GET | `/products`, `/products/<id>` | Public | Browse products |
| POST / PUT / DELETE | `/products`, `/products/<id>` | Logged in (see limitations) | Manage products |
| GET / POST / DELETE | `/carts` | Logged in | View, add to, or clear your cart |
| GET / PUT / DELETE | `/carts/<id>` | Own items only | Read, change quantity of, or remove a cart item |
| GET / POST | `/orders` | Logged in | List your orders or place one |
| GET | `/orders/<id>` | Own orders only | Read an order |
| POST | `/orders/<id>/cancel` | Own orders only | Cancel a pending order |

## Design decisions

- **Orders and order items are separate tables.** An order is one checkout containing many products. Each `OrderItem` row holds a product and quantity, so a basket of several different products is a single order.
- **Prices are snapshotted.** Each order item stores `price_at_purchase`, so changing a product's price later doesn't rewrite order history.
- **The server calculates totals.** Clients never send prices or totals, so they can't be tampered with.
- **Money uses `Decimal`, not `float`.** Float arithmetic can't represent decimal currency exactly. Prices are stored as `Numeric(10, 2)` and returned as strings (for example `"19.99"`) so JSON parsers don't turn them back into floats.
- **Identity comes from the token, not the request body.** Carts and orders use the user ID inside the verified JWT. A `user_id` in the body is ignored, which stops one user acting as another.
- **Other users' data returns `404`, not `403`.** For carts and orders, someone else's record looks the same as one that doesn't exist, so IDs can't be probed.
- **Order creation is all-or-nothing.** Items are validated and the order is built before a single commit, so an invalid item never leaves a partial order behind. This is covered by a test.
- **Consistent error responses.** Global handlers return JSON errors in one shape, hide internal exception text from clients, and map database constraint violations to `409`, validation failures to `400` (with field-level details), and wrong HTTP methods to `405`.
- **Passwords are hashed** with Werkzeug before storage and are never returned by the API.
- **Secrets live in environment variables.** `.env` is git-ignored, and `.env.example` documents what is needed.

## Project structure

```
├── app.py            # App setup, blueprint registration, error handlers
├── auth.py           # Helpers: current user from token, ownership check
├── extensions.py     # Shared db / jwt / marshmallow instances
├── models.py         # User, Product, Cart, Order, OrderItem, Wishlist
├── schemas.py        # Marshmallow schemas
├── routes/           # One blueprint per resource
└── tests/            # pytest suite
```

## Known limitations and roadmap

I'd rather be upfront about what this doesn't do yet:

- **No admin role.** Any logged-in user can create, edit or delete products. An `is_admin` flag with an admin-only decorator is the next security step.
- **Validation is uneven.** Marshmallow schemas cover products. Other routes use hand-written checks, and I plan to move them all onto schemas.
- **SQLite only for now.** I plan to run it on PostgreSQL, where `Numeric` is exact, and add Alembic migrations (the schema is currently created with `db.create_all()`).
- **No pagination, search or filtering** on list endpoints.
- **No stock tracking, payments or email notifications.**
- **No token refresh or rate limiting** on login.

## Author

Emmanuel · eakinbode11@gmail.com
