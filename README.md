<div style="display: flex; justify-content: center; margin-top: 20px;">
  <img width="200" src="https://raw.githubusercontent.com/playiiit/makefast/main/makefast/app/assets/makefast-logo.png">
</div>
<h2 style="text-align: center; margin-top: 0px;">
  MakeFast - FastAPI CLI Manager
</h2>

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
- [Contributing](#contributing)
- [License](#license)

## Installation

To install MakeFast, simply run the following command in your terminal:
```shell
pip install assets
```
After the run this command to make the project template:
```shell
assets init
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
To create a new record, use the Model.create method, passing in the desired attributes. This method is asynchronous and returns a response that typically contains information about the newly created record.
```py
from app.models import User

create_response = await User.create(**{
    "username": "usertest",
    "email": "test@example.com",
    "password": "test123",
})
```
#### Update
To update an existing record, specify the ID and the fields to modify using Model.update. This example updates the name field of the user with ID 45.
```py
from app.models import User

await User.update(45, **{
    "name": "New name"
})
```
#### Find one
To retrieve a single record, use Model.find. This function typically returns the first record matching the criteria or, if no criteria are specified, an arbitrary record.
```py
from app.models import User

await User.find(45)
```
#### Find all
To retrieve all the records, use the Model.all method, which returns a collection of records.
```py
from app.models import User

await User.all()
```
#### Delete
To delete a record by their ID, use the Model.delete method. Here, we remove the user with an ID of 45.
```py
from app.models import User

await User.delete(45)
```

## Contributing

Contributions are welcome! To contribute to MakeFast, follow these steps:

1. Fork the repository
2. Create a new branch
3. Make changes and commit them
4. Create a pull request

## License

MakeFast is licensed under the MIT License. See [LICENSE](LICENSE) for details.