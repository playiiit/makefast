<div align="center">
  <img height="90" src="https://://raw.githubusercontent.com/playiiit/makefast/refs/heads/main/makefast/app/assets/makefast-logo-white-bg.png">
  <h1 style="margin-top: 0px;">
    MakeFast - FastAPI CLI Manager
  </h1>
</div>

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.4.0-green.svg)](https://pypi.org/project/makefast/)

Welcome to MakeFast, a FastAPI CLI library designed to streamline your development workflow — inspired by Laravel's elegant developer experience. With MakeFast, you can scaffold routes, models, requests, resources, migrations, and more, so you can focus on writing high-quality business logic.

## Table of Contents

- [Installation](#installation)
- [Commands](#commands)
  - [Project Creation](#project-creation)
  - [Controller Generation](#controller-generation)
  - [Model Generation](#model-generation)
  - [Schema Generation](#schema-generation)
  - [Enum Generation](#enum-generation)
  - [Request Generation](#request-generation)
  - [Resource Generation](#resource-generation)
  - [Mail Generation](#mail-generation)
  - [Migration Generation](#migration-generation)
- [Routing & Middleware](#routing--middleware)
  - [Defining Routes](#defining-routes)
  - [Adding Route Middleware](#adding-route-middleware)
- [Form Requests](#form-requests)
  - [Defining Rules](#defining-rules)
  - [Available Rules](#available-rules)
  - [Custom Messages](#custom-messages)
  - [Using in Routes](#using-in-routes)
- [API Resources](#api-resources)
  - [Single Resource](#single-resource)
  - [Resource Collection](#resource-collection)
  - [Pagination with Resources](#pagination-with-resources)
- [Emails (Mailables)](#emails-mailables)
  - [Creating Mailables](#creating-mailables)
  - [Sending Emails](#sending-emails)
- [Database Configuration](#database-configuration)
  - [MySQL](#mysql)
  - [MongoDB](#mongodb)
  - [Database CRUD operations](#database-crud-operations)
    - [Create](#create)
    - [Update](#update)
    - [Find one](#find-one)
    - [Find all](#find-all)
    - [Delete](#delete)
  - [Advanced Query Builder](#advanced-query-builder)
  - [Aggregations](#aggregations)
  - [Bulk Operations](#bulk-operations)
  - [Safe Raw Queries](#safe-raw-queries)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install MakeFast, simply run the following command in your terminal:

```shell
pip install makefast
```

After installation, run this command to generate the project template:

```shell
makefast init
```

Install the project dependencies:

```shell
pip install -r requirements.txt
```

Run the development server:

```shell
uvicorn main:app --port 8000 --reload
```

---

## Commands

#### Project Creation

| Command         | Description               | Options |
| --------------- | ------------------------- | ------- |
| `makefast init` | Initializes a new project |         |

#### Controller Generation

Generates a Laravel-style Controller class and automatically registers its routes in `app/routes/api.py`.

| Command                                      | Description                | Options                                                                                  |
| -------------------------------------------- | -------------------------- | ---------------------------------------------------------------------------------------- |
| `makefast create-controller CONTROLLER_NAME` | Generates a new controller | `--model MODEL_NAME`, `--request-scheme REQUEST_NAME`, `--response-scheme RESPONSE_NAME` |

#### Model Generation

| Command                            | Description           | Options                                              |
| ---------------------------------- | --------------------- | ---------------------------------------------------- |
| `makefast create-model MODEL_NAME` | Generates a new model | `--table TABLE_NAME`, `--collection COLLECTION_NAME` |

#### Schema Generation

| Command                              | Description            | Options |
| ------------------------------------ | ---------------------- | ------- |
| `makefast create-schema SCHEMA_NAME` | Generates a new schema |         |

#### Enum Generation

| Command                          | Description          | Options      |
| -------------------------------- | -------------------- | ------------ |
| `makefast create-enum ENUM_NAME` | Generates a new enum | `--type str` |

#### Request Generation

Generates a Laravel-style `FormRequest` validation class under `app/requests/`.

| Command                                | Description                        | Options |
| -------------------------------------- | ---------------------------------- | ------- |
| `makefast create-request REQUEST_NAME` | Generates a new form request class |         |

```shell
makefast create-request StoreUserRequest
# → app/requests/store_user_request.py
```

#### Resource Generation

Generates a Laravel-style `Resource` or `ResourceCollection` class under `app/resources/`.

| Command                                     | Description                         | Options             |
| ------------------------------------------- | ----------------------------------- | ------------------- |
| `makefast create-resource RESOURCE_NAME`    | Generates a new API resource class  |                     |
| `makefast create-resource RESOURCE_NAME -c` | Also generates a ResourceCollection | `--collection / -c` |

```shell
makefast create-resource User
# → app/resources/user.py

makefast create-resource User --collection
# → app/resources/user.py + app/resources/user_collection.py
```

#### Mail Generation

Generates a Laravel-style `Mailable` class under `app/mail/` and its corresponding HTML template under `resources/views/emails/`.

| Command                          | Description                              |
| -------------------------------- | ---------------------------------------- |
| `makefast create-mail MAIL_NAME` | Generates a new mailable & HTML template |

```shell
makefast create-mail WelcomeEmail
# → app/mail/welcome_email.py
# → resources/views/emails/welcome-email.html
```

#### Migration Generation

| Command                                    | Description                 |
| ------------------------------------------ | --------------------------- |
| `makefast create-migration MIGRATION_NAME` | Generates a new migration   |
| `makefast migrate`                         | Runs all pending migrations |

---

## Routing & Middleware

Since MakeFast adopts a Laravel-style routing architecture, all routes are registered centrally in `app/routes/api.py`.

### Defining Routes

When you generate a controller via `makefast create-controller`, the route is automatically registered for you.

```python
# app/routes/api.py
from fastapi import APIRouter
from app.controllers.user_controller import UserController

router = APIRouter()

router.add_api_route(
    path="/user",
    endpoint=UserController.index,
    methods=["GET"]
)
```

### Adding Route Middleware

In FastAPI, route-specific middleware is handled using the `Depends` dependency injection system. Because the `dependencies` parameter accepts a list, you can chain multiple middlewares to run in an exact sequence before your controller method is executed.

```python
from fastapi import Depends
from app.dependencies.auth import verify_token
from app.dependencies.roles import require_admin

router.add_api_route(
    path="/admin/dashboard",
    endpoint=AdminController.dashboard,
    methods=["GET"],
    dependencies=[
        Depends(verify_token),  # Runs first
        Depends(require_admin)  # Runs second (only if first succeeds)
    ]
)
```

---

## Form Requests

Form Requests provide a clean, reusable way to validate incoming HTTP data — just like Laravel's `FormRequest`.

### Defining Rules

```python
# app/requests/store_user_request.py
from makefast.http import FormRequest
from typing import Any, Dict

class StoreUserRequest(FormRequest):

    def authorize(self) -> bool:
        # Return False to reject unauthorized requests (raises 403)
        return True

    def rules(self) -> Dict[str, Any]:
        return {
            "name":     ["required", "string", "min:2", "max:100"],
            "email":    ["required", "email"],
            "password": ["required", "string", "min:8", "confirmed"],
            "age":      ["nullable", "integer", "min:0"],
            "role":     ["required", "in:admin,user,guest"],
        }
```

### Available Rules

| Rule              | Example           | Description                                           |
| ----------------- | ----------------- | ----------------------------------------------------- |
| `required`        | `"required"`      | Field must be present and non-empty                   |
| `nullable`        | `"nullable"`      | Field may be absent or `None`                         |
| `string`          | `"string"`        | Must be a `str`                                       |
| `integer` / `int` | `"integer"`       | Must be an `int`                                      |
| `numeric`         | `"numeric"`       | Must be `int` or `float`                              |
| `boolean`         | `"boolean"`       | Must be `bool`                                        |
| `email`           | `"email"`         | Must match a valid email pattern                      |
| `min:<n>`         | `"min:3"`         | Min length (strings) or min value (numbers)           |
| `max:<n>`         | `"max:255"`       | Max length (strings) or max value (numbers)           |
| `in:<a,b,c>`      | `"in:admin,user"` | Value must be one of the listed options               |
| `not_in:<a,b,c>`  | `"not_in:banned"` | Value must NOT be one of the listed options           |
| `regex:<pattern>` | `"regex:^[A-Z]"`  | Must match the given regex pattern                    |
| `confirmed`       | `"confirmed"`     | Must equal `{field}_confirmation` in the request body |

### Custom Messages

```python
def messages(self) -> Dict[str, str]:
    return {
        "name.required":  "Please tell us your name.",
        "email.email":    "Please use a valid email address.",
        "password.min":   "Password must be at least 8 characters.",
    }
```

### Using in Routes

Use the request class as a FastAPI dependency via `Depends`:

```python
from fastapi import APIRouter, Depends
from app.requests.store_user_request import StoreUserRequest

router = APIRouter()

@router.post("/users")
async def store(req: StoreUserRequest = Depends(StoreUserRequest.from_request)):
    # req.validated() → only fields that passed validation
    data = req.validated()
    user = await User.create(**data)
    return {"message": "User created", "user": user}
```

If validation fails, a `422 Unprocessable Entity` response is returned automatically with detailed error messages. If `authorize()` returns `False`, a `403 Forbidden` is raised.

---

## API Resources

Resources provide a consistent way to transform your model data before returning it from your routes — like Laravel's API Resources.

### Single Resource

```python
# app/resources/user.py
from makefast.http import Resource
from typing import Any, Dict

class UserResource(Resource):
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id":         self.data["id"],
            "name":       self.data["name"],
            "email":      self.data["email"],
            "created_at": str(self.data.get("created_at", "")),
        }
```

Use in a route:

```python
from app.resources.user import UserResource

@router.get("/users/{id}")
async def show(id: int):
    user = await User.find(id)
    return UserResource(user).response()
    # → {"data": {"id": 1, "name": "Alice", "email": "..."}}
```

**Fluent modifiers:**

```python
# Remove the "data" wrapper
UserResource(user).without_wrapping().response()
# → {"id": 1, "name": "Alice", ...}

# Use a custom wrapper key
UserResource(user).wrap("user").response()
# → {"user": {"id": 1, ...}}

# Attach extra metadata
UserResource(user).with_meta({"token": jwt_token}).response()
# → {"data": {...}, "token": "..."}
```

### Resource Collection

```python
# app/resources/user_collection.py
from makefast.http import ResourceCollection
from app.resources.user import UserResource

class UserCollection(ResourceCollection):
    resource_class = UserResource
```

Use in a route:

```python
from app.resources.user_collection import UserCollection

@router.get("/users")
async def index():
    users = await User.all()
    return UserCollection(users).response()
    # → {"data": [{...}, {...}]}
```

**Inline factory** (no subclassing needed):

```python
from makefast.http import ResourceCollection
from app.resources.user import UserResource

return ResourceCollection.of(UserResource, users).response()
```

### Pagination with Resources

```python
@router.get("/users")
async def index(page: int = 1):
    # Paginate with conditions using QueryBuilder
    result = await User.query().where("active", 1).order_by("name").paginate(page=page, per_page=15)

    return UserCollection(result["data"]).with_pagination(result).response()
```

Response shape:

```json
{
  "data": [...],
  "pagination": {
    "total": 42,
    "per_page": 15,
    "current_page": 1,
    "last_page": 3,
    "from": 1,
    "to": 15
  }
}
```

---

## Emails (Mailables)

MakeFast provides a Laravel-like mailing system using `Mailable` classes and Jinja2 HTML templates.

### Creating Mailables

Generate a Mailable using the CLI:

```shell
makefast create-mail WelcomeEmail
```

This will create `app/mail/welcome_email.py` and an HTML template in `resources/views/emails/welcome-email.html`.

In your `WelcomeEmail` class, define the view, data, and subject:

```python
# app/mail/welcome_email.py
from makefast.mail import Mailable

class WelcomeEmail(Mailable):
    def __init__(self, data: dict = None):
        super().__init__()
        self.mail_data = data or {}

    def build(self):
        return (
            self.view("emails.welcome-email")
                .with_data(**self.mail_data)
                .subject("Welcome to MakeFast!")
        )
```

In your HTML template (`resources/views/emails/welcome-email.html`), you can use Jinja2 syntax to output the passed data:

```html
<!DOCTYPE html>
<html>
  <body>
    <h2>Welcome, {{ name }}!</h2>
    <p>Thank you for joining us.</p>
  </body>
</html>
```

### Sending Emails

Use the `Mail` facade to send emails. MakeFast uses SMTP configurations defined in your `.env` file (e.g., `MAIL_HOST`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM_ADDRESS`, `MAIL_FROM_NAME`).

```python
from makefast.mail import Mail
from app.mail.welcome_email import WelcomeEmail

@router.post("/users")
async def store():
    # User creation logic...

    mailable = WelcomeEmail({"name": "Alice"})
    Mail.to("alice@example.com").send(mailable)

    return {"message": "User created and email sent"}
```

---

## Database Configuration

MakeFast provides the easiest way to configure and use a database. By default, MakeFast supports **MySQL** and **MongoDB**.

### MySQL

Add the following lines to `main.py`:

```python
from fastapi import FastAPI
from makefast.database import MySQLDatabaseInit

app = FastAPI()

MySQLDatabaseInit.init(app)
```

Configure your `.env` file:

```env
DB_CONNECTION=mysql
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=your_database
DB_USERNAME=your_username
DB_PASSWORD=your_password
```

### MongoDB

Add the following lines to `main.py`:

```python
from fastapi import FastAPI
from makefast.database import MongoDBDatabaseInit

app = FastAPI()

MongoDBDatabaseInit.init(app)
```

### Database CRUD operations

MakeFast offers built-in methods for CRUD operations. First, create a model that corresponds to your MySQL table or MongoDB collection.

#### Create

```python
from app.models import User

user = await User.create(**{
    "username": "usertest",
    "email": "test@example.com",
    "password": "test123",
})
```

#### Update

```python
await User.update(45, **{
    "name": "New name"
})
```

#### Find one

```python
await User.find(45)
await User.find_or_fail(45)  # raises 404 if not found
```

#### Find all

```python
await User.all()
```

#### Delete

```python
await User.delete(45)
```

---

## Advanced Query Builder

MakeFast's MySQL integration includes a powerful **QueryBuilder** for building advanced queries with full validation and SQL injection protection.

#### Filtering

```python
# WHERE username = 'john'
users = await User.query().where("username", "john").get()

# WHERE age > 18 AND status = 'active'
users = await User.query().where("age", ">", 18).where("status", "active").get()

# WHERE IN / NOT IN
users = await User.query().where_in("status", ["active", "pending"]).get()

# WHERE IS NULL / IS NOT NULL
users = await User.query().where_null("deleted_at").get()

# WHERE BETWEEN
users = await User.query().where_between("age", 18, 65).get()

# WHERE LIKE
users = await User.query().where_like("email", "%@gmail.com").get()

# OR WHERE
users = await User.query().where("role", "admin").or_where("role", "moderator").get()
```

#### Joins

```python
# INNER JOIN
results = await User.query().join("profiles", "users.id", "profiles.user_id").get()

# LEFT JOIN
results = await User.query().left_join("orders", "users.id", "orders.user_id").get()

# RIGHT JOIN
results = await User.query().right_join("departments", "users.dept_id", "departments.id").get()
```

#### Select Specific Columns

```python
users = await User.query().select("id", "username", "email").get()

# With alias
users = await User.query().select_raw("users.id as user_id", "profiles.bio as profile_bio").get()
```

#### Ordering, Limit & Offset

```python
users = await User.query().order_by("created_at", "DESC").limit(10).offset(20).get()
```

#### Group By

```python
results = await User.query().select("role").group_by("role").get()
```

#### First / First Or Fail

```python
user = await User.query().where("username", "john").first()
user = await User.query().where("username", "john").first_or_fail()  # raises 404
```

#### Pagination (Chained)

Paginate any query, including those with joins, filters, and ordering:

```python
result = await User.query() \
    .where("active", 1) \
    .order_by("created_at", "DESC") \
    .paginate(page=1, per_page=15)

# result = {
#   "data": [...],
#   "total": 42,
#   "per_page": 15,
#   "current_page": 1,
#   "last_page": 3,
#   "from": 1,
#   "to": 15
# }
```

#### Simple Pagination (Class-level)

```python
result = await User.paginate(page=2, per_page=20)
```

#### Exists Check

```python
already_taken = await User.query().where("email", email).exists()
if already_taken:
    raise HTTPException(400, "Email already registered")
```

#### Chained Update & Delete

```python
# Update matching records
rows_updated = await User.query().where("status", "inactive").update(status="archived")

# Delete matching records (WHERE is required for safety)
rows_deleted = await User.query().where("deleted_at", "<", cutoff_date).delete()
```

---

## Aggregations

Built-in aggregation helpers on both the model and the query builder:

```python
total_users = await User.count()
max_age    = await User.max("age")
min_age    = await User.min("age")
avg_age    = await User.avg("age")
total_bal  = await User.sum("balance")

# With conditions
active_count = await User.query().where("active", 1).count()
```

---

## Bulk Operations

#### Bulk Create

```python
users = await User.bulk_create([
    {"username": "alice", "email": "alice@example.com"},
    {"username": "bob",   "email": "bob@example.com"},
])
```

#### Get or Create

```python
user, created = await User.get_or_create(
    username="john",
    defaults={"email": "john@example.com"}
)
```

#### Update or Create

```python
user, created = await User.update_or_create(
    username="john",
    defaults={"email": "newjohn@example.com"}
)
```

---

## Safe Raw Queries

MakeFast allows raw SQL execution with strict validation and safety:

```python
results = await User.safe_raw_query(
    "SELECT id, username FROM users WHERE status = %s",
    params=("active",)
)
```

By default, only **SELECT** queries are allowed unless you explicitly pass `allowed_operations`:

```python
results = await User.safe_raw_query(
    "UPDATE users SET status = %s WHERE id = %s",
    params=("active", 1),
    allowed_operations={"UPDATE"}
)
```

---

## Project Structure

After running `makefast init`, your project will have the following structure:

```
app/
├── controllers/       ← Controller classes
├── dependencies/
│   └── response_handler.py
├── enums/
├── migrations/
├── models/
├── requests/          ← Form Request classes
├── resources/         ← API Resource & Collection classes
├── routes/            ← Route definitions (api.py)
└── schemas/
.makefast/
└── executed_migrations.txt
main.py
.env
requirements.txt
```

---

## Contributing

Contributions are welcome! To contribute to MakeFast, follow these steps:

1. Fork the repository
2. Create a new branch
3. Make changes and commit them
4. Create a pull request

## License

MakeFast is licensed under the MIT License. See [LICENSE](LICENSE) for details.
