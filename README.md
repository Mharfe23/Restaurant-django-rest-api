# Restaurant API

This is a RESTful API for a restaurant. It provides endpoints for browsing menu items, managing user carts, placing orders, and administrative tasks. The API supports role-based permissions for customers, managers, and delivery crew.

## Features

-   Browse menu items and categories.
-   User registration and authentication.
-   Customers can add/remove items from their cart.
-   Customers can place orders from their cart.
-   Role-based access control:
    -   **Manager**: Full control over menu items, categories, and all orders. Can assign users to delivery crew and other manager roles.
    -   **Delivery Crew**: Can view and update the status of orders assigned to them.
    -   **Customer**: Can manage their own cart and view their own orders.
-   Filtering, searching, and ordering on menu items and orders.
-   Pagination and rate limiting

## Technologies Used

-   Python
-   Django
-   Django REST Framework
-   Djoser (for user registration and authentication)
-   SQLite (for development)

## Setup and Installation

Follow these steps to get the project up and running on your local machine.

### Prerequisites

-   Python 3.8+
-   pip
-   `venv` (or any other virtual environment tool)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd Restaurant-django-rest-api
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    A `requirements.txt` file is not included. You can create one and install the packages.
    ```bash
    pip install django djangorestframework djoser
    ```

4.  **Apply database migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Create user roles:**
    This project uses three roles: Customer, Manager, and Delivery Crew.
    -   **Customers** are regular authenticated users.
    -   **Manager** and **Delivery Crew** roles are managed using Django's Group system. You'll need to create these groups.

    First, create a superuser to access the admin panel:
    ```bash
    python manage.py createsuperuser
    ```
    Then, run the development server, navigate to the admin panel (`/admin/`), and create two groups named `Manager` and `Delivery-crew`. You can then assign users to these groups.

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/`.

## API Endpoints

All endpoints are prefixed with `/api/`.

### Authentication

Djoser is used for handling user registration and authentication. These endpoints are available under `/auth/`.

| Endpoint                 | Method | Description                      |
| ------------------------ | ------ | -------------------------------- |
| `/auth/users/`             | `POST` | Register a new user.             |
| `/auth/users/me/`          | `GET`  | Get current user details.        |
| `/auth/token/login/`       | `POST` | Get an authentication token.     |
| `/auth/token/logout/`      | `POST` | Invalidate the auth token.       |

### Menu

| Endpoint                 | Method        | Description                                       | Permissions          |
| ------------------------ | ------------- | ------------------------------------------------- | -------------------- |
| `/menu-items/`           | `GET`, `POST` | List or create menu items.                        | `GET`: Public, `POST`: Manager |
| `/menu-items/{id}`       | `GET`, `PUT`, `PATCH`, `DELETE` | Retrieve, update or delete a single menu item. | `GET`: Public, `Others`: Manager |
| `/categories/`           | `GET`, `POST` | List or create categories.                        | `GET`: Public, `POST`: Manager |

### User Management (Managers Only)

| Endpoint                 | Method        | Description                                       |
| ------------------------ | ------------- | ------------------------------------------------- |
| `/groups/manager/users`  | `GET`, `POST` | List or add users to the Manager group.           |
| `/groups/manager/users/{userId}` | `DELETE`      | Remove a user from the Manager group.             |
| `/groups/delivery-crew/users` | `GET`, `POST` | List or add users to the Delivery Crew group.     |
| `/groups/delivery-crew/users/{userId}` | `DELETE`      | Remove a user from the Delivery Crew group.       |

### Cart (Customers Only)

| Endpoint                 | Method          | Description                               |
| ------------------------ | --------------- | ----------------------------------------- |
| `/cart/menu-items/`      | `GET`, `POST`, `DELETE` | List, add, or delete items from the cart. |

### Orders

| Endpoint                 | Method        | Description                                       | Permissions          |
| ------------------------ | ------------- | ------------------------------------------------- | -------------------- |
| `/orders/`               | `GET`, `POST` | List or create orders. `GET` depends on role.     | Customer, Manager, Delivery Crew |
| `/orders/{orderId}/`     | `GET`, `PUT`, `PATCH`, `DELETE` | Retrieve, update or delete a single order. | `GET`: Customer, `PUT`/`PATCH`: Manager/Delivery Crew, `DELETE`: Manager |

### User Roles and Permissions

-   **Anonymous Users**: Can browse menu items and categories.
-   **Authenticated Users (Customers)**:
    -   Can access all `GET` endpoints for menus.
    -   Can manage their own cart.
    -   Can place orders.
    -   Can view their own orders.
-   **Delivery Crew**:
    -   All customer permissions.
    -   Can view orders assigned to them.
    -   Can update the status of their assigned orders.
-   **Managers**:
    -   All permissions.
    -   Can create, update, and delete menu items and categories.
    -   Can view all orders.
    -   Can assign users to Manager and Delivery Crew groups.
    -   Can assign delivery crew to orders.
    -   Can delete any order.
