# Service Management and Booking System

**Final Project for the Software Engineering Laboratory Course**
**Shahid Chamran University of Ahvaz**

## Overview

The **Service Management and Booking System** is a comprehensive web-based platform designed to manage services, reservations, payments, reviews, notifications, and reports.

The system supports three user roles:

- **Admin:** Manages users, services, bookings, and statistical reports
- **Provider:** Creates services and available time slots and manages customer bookings
- **Customer:** Searches for services, makes reservations, completes payments, and submits reviews

## Main Features

### Admin

- Manage users and providers
- Manage services and categories
- View and manage all bookings
- Access statistical dashboards
- Generate administrative PDF reports
- Delete inappropriate reviews

### Provider

- Create, edit, activate, or deactivate services
- Define available booking time slots
- View and manage customer bookings
- Access provider dashboard statistics
- Generate booking reports in PDF format

### Customer

- Search and filter available services
- Reserve available time slots
- Complete simulated payments
- View booking history
- Cancel eligible bookings
- Submit and edit service reviews
- Download invoices and booking reports

## Technologies and Libraries

- **Django 5+**: Main web framework
- **Django Channels**: Real-time WebSocket communication
- **Daphne**: ASGI server
- **ReportLab**: PDF report and invoice generation
- **Pillow**: Image processing and management
- **Bootstrap 5 RTL**: Responsive right-to-left user interface
- **Chart.js**: Dashboard charts and statistical visualizations

## Project Structure

```text
accounts/           Authentication, user profiles, and user management
services/           Services, categories, and available time slots
bookings/           Booking creation, management, and cancellation
payments/           Simulated payment gateway
reviews/            Customer reviews and ratings
notifications_app/  Notifications and WebSocket functionality
reports/            PDF reports and invoice generation
dashboard/          Admin and Provider dashboards
```

## Installation and Setup

### 1. Create a Virtual Environment

```bash
python3 -m venv venv
```

### 2. Activate the Virtual Environment

On Linux or macOS:

```bash
source venv/bin/activate
```

On Windows CMD:

```bash
venv\Scripts\activate
```

On Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install the Required Packages

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Create Sample Data

```bash
python manage.py seed_data
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

## Running the WebSocket Server

To enable real-time notifications through WebSocket, run the project using Daphne:

```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

The application will then be available at:

```text
http://127.0.0.1:8000/
```

## Sample Accounts

| Role     | Username    | Password |
| -------- | ----------- | -------- |
| Admin    | `admin`     | `123456` |
| Provider | `provider1` | `123456` |
| Customer | `customer1` | `123456` |

> These accounts are intended for development and testing purposes only. Change the default passwords before deploying the system.

## Business Rules

- All newly created bookings initially have a **Pending** status.
- When a Provider account is deactivated, all services belonging to that Provider automatically become **Inactive**.
- Existing bookings preserve a snapshot of the service price and duration at the time of reservation.
- Customers can cancel a booking only up to **2 hours before** its scheduled start time.
- Customers can edit their reviews for up to **24 hours** after submission.
- Reviews can only be deleted by an Admin.
- Service search requests use a **300-millisecond debounce** to reduce unnecessary server requests.

## Running Tests

Run all project tests using:

```bash
python manage.py test
```

## PDF Reports

The system can generate the following PDF documents:

- Payment invoice with an `INV-xxxx` invoice number
- Customer booking report
- Provider booking report
- Admin statistical report with the report generation date

## Development Notes

- The payment gateway is simulated and does not process real financial transactions.
- WebSocket functionality requires the application to run through an ASGI server such as Daphne.
- Sample data can be generated using the `seed_data` management command.
- Default credentials must not be used in a production environment.

## License

This project was developed for educational purposes as the final project of the Software Engineering Laboratory course at Shahid Chamran University of Ahvaz.
