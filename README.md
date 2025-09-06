<div align="center">
  <img height="90" src="https://://raw.githubusercontent.com/playiiit/makefast/refs/heads/main/makefast/app/assets/makefast-logo-white-bg.png">
  <h1 style="margin-top: 0px;">
    MakeFast - FastAPI CLI Manager
  </h1>
</div>

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Welcome to MakeFast, a FastAPI CLI library designed to streamline your development workflow. With MakeFast, you can efficiently manage your projects, and focus on writing high-quality code.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Commands](#commands)
  - [Project Creation](#project-creation)
  - [Route Generation](#route-generation)
  - [Model Generation](#model-generation)
  - [Schema Generation](#schema-generation)
  - [Enum Generation](#enum-generation)
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
- [Contributing](#contributing)
- [License](#license)

## Installation

To install MakeFast, simply run the following command in your terminal:
```shell
pip install makefast
```
After the run this command to make the project template:
```shell
makefast init
```
Finally, run the:
```shell
pip install -r requirements.txt
```
To run the project, you can run the uvicorn command:
```shell
uvicorn main:app --port 8000 --reload
```

## Commands

#### Project Creation
| Command | Description | Options |
| --- | --- | --- |
| `makefast init` | Initializes a new project |  |

#### Route Generation
| Command | Description | Options |
| --- | --- | --- |
| `makefast create-route ROUTE_NAME` | Generates a new route | `--model MODEL_NAME`, `--request_scheme REQUEST_NAME`, `--response_scheme RESPONSE_NAME` |

#### Model Generation
| Command | Description | Options |
| --- | --- | --- |
| `makefast create-model MODEL_NAME` | Generates a new model | `--table TABLE_NAME`, `--collection COLLECTION_NAME` |

#### Schema Generation
| Command | Description | Options |
| --- | --- | --- |
| `makefast create-schema SCHEMA_NAME` | Generates a new schema |  |

#### Enum Generation
| Command | Description | Options |
| --- | --- | --- |
| `makefast create-enum ENUM_NAME` | Generates a new enum | `--type str` |

## Database Configuration
Makefast provide the easiest way to configure the database and using them. By default makefast has 2 databases which is MySql and MongoDB.

### MySQL

To initiate MySQL, add below lines on `main.py` file as necessary.
```py
from fastapi import FastAPI
from makefast.database import MySQLDatabaseInit

app = FastAPI()

MySQLDatabaseInit.init(app)
```

### MongoDB

To initiate MongoDB, add below lines on `main.py` file as necessary.
```py
from fastapi import FastAPI
from makefast.database import MongoDBDatabaseInit

app = FastAPI()

MongoDBDatabaseInit.init(app)
```

### Database CRUD operations

Makefast offers default functions for CRUD operations. Before using these, you need to create a model that corresponds to the MySQL table or MongoDB collection.

#### Create
```py
from app.models import User

create_response = await User.create(**{
    "username": "usertest",
    "email": "test@example.com",
    "password": "test123",
})
```

#### Update
```py
await User.update(45, **{
    "name": "New name"
})
```

#### Find one
```py
await User.find(45)
```

#### Find all
```py
await User.all()
```

#### Delete
```py
await User.delete(45)
```

---

## Advanced Query Builder

MakeFast’s MySQL integration includes a powerful **QueryBuilder** for advanced queries with validation and safety.

#### Filtering
```py
# WHERE username = 'john'
users = await User.query().where("username", "john").get()

# WHERE age > 18 AND status = 'active'
users = await User.query().where("age", ">", 18).where("status", "active").get()
```

#### Joins
```py
# INNER JOIN
results = await User.query().join("profiles", "users.id", "profiles.user_id").get()

# LEFT JOIN
results = await User.query().left_join("orders", "users.id", "orders.user_id").get()
```

#### Select Specific Columns
```py
users = await User.query().select("id", "username", "email").get()

# With alias
users = await User.query().select_raw("users.id as user_id", "profiles.bio as profile_bio").get()
```

#### Ordering, Limit & Offset
```py
users = await User.query().order_by("created_at", "DESC").limit(10).offset(20).get()
```

#### First / First Or Fail
```py
user = await User.query().where("username", "john").first()
user = await User.query().where("username", "john").first_or_fail()
```

#### Pagination
```py
users_page = await User.paginate(page=2, per_page=20)
```

---

## Aggregations

Built-in aggregation helpers:
```py
total_users = await User.count()
max_age = await User.max("age")
min_age = await User.min("age")
avg_age = await User.avg("age")
total_balance = await User.sum("balance")
```

---

## Bulk Operations

#### Bulk Create
```py
users = await User.bulk_create([
    {"username": "alice", "email": "alice@example.com"},
    {"username": "bob", "email": "bob@example.com"}
])
```

#### Get or Create
```py
user, created = await User.get_or_create(username="john", defaults={"email": "john@example.com"})
```

#### Update or Create
```py
user, created = await User.update_or_create(username="john", defaults={"email": "newjohn@example.com"})
```

---

## Safe Raw Queries

MakeFast allows raw SQL execution with strict validation and safety:
```py
results = await User.safe_raw_query("SELECT id, username FROM users WHERE status = %s", params=("active",))
```

By default, only **SELECT** queries are allowed unless you explicitly allow other operations.

---

## Contributing

Contributions are welcome! To contribute to MakeFast, follow these steps:

1. Fork the repository
2. Create a new branch
3. Make changes and commit them
4. Create a pull request

## License

MakeFast is licensed under the MIT License. See [LICENSE](LICENSE) for details.
