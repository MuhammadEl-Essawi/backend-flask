# Rently.Management

Backend for the “Management” part of the mobile app (Flutter). It provides JWT authentication, Paymob payments (card iframe and wallet redirect), account management, and core admin dashboards and resources (Users, Cars, Bookings, Requests, Payments).

## Quick Start
- Run locally: `dotnet run --project .\Rently.Management.csproj`
- Swagger: http://localhost:5000/swagger
- Development settings: WebApi/appsettings.Development.json

## Documentation
- Architecture and diagrams: docs/ARCHITECTURE.md (ER diagram, class diagram, endpoint workflows)

## Tech Stack
- .NET 9, ASP.NET Core Web API
- Entity Framework Core (SQL Server)
- JWT Bearer Authentication
- Google SMTP (OTP Verification)
- Swashbuckle/Swagger
- Paymob payment gateway integration

## Project Structure
- Domain/Entities: Core domain models (User, Car, Booking, Payment, etc.)
- Infrastructure: EF Core DbContext, repositories, configurations, migrations
- WebApi/Controllers: API endpoints
- WebApi/Services: PaymobService, PasswordService
- WebApi/appsettings.json/.Development.json: configuration
- docs/: architecture documentation

## Requirements
- .NET SDK 9.0
- SQL Server (LocalDB or any accessible instance)
- Paymob test/development credentials (ApiKey, IntegrationIdCard, IntegrationIdWallet, IframeId, HmacSecret)

## 🔐 Security & Configuration
This project follows professional security standards for handling sensitive data. **Never commit real credentials to the repository.**

### 1. Sensitive Data (User Secrets)
Use `dotnet user-secrets` to store your private keys locally during development:
```bash
# Admin Credentials for Dev Login
dotnet user-secrets set "Admin:Email" "admin@example.com"
dotnet user-secrets set "Admin:Password" "YourStrongPassword123!"

# SMTP Configuration (Gmail recommended)
dotnet user-secrets set "Smtp:Email" "your-app-email@gmail.com"
dotnet user-secrets set "Smtp:Password" "your-16-char-app-password"

# Paymob Integration
dotnet user-secrets set "Paymob:ApiKey" "zx_prd_..."
dotnet user-secrets set "Paymob:HmacSecret" "..."
```

### 2. SMTP Settings (`appsettings.json`)
The infrastructure is ready for Google SMTP. Ensure these settings are in your `appsettings.json`:
```json
"Smtp": {
  "Host": "smtp.gmail.com",
  "Port": 587,
  "EnableSsl": true,
  "Email": "__USE_USER_SECRETS__",
  "Password": "__USE_USER_SECRETS__"
}
```

---

## 📚 API Reference

### 🔐 Authentication (`/api/auth`)
- `POST /login` [Public]
  - **Success**: `200 OK` (Returns JWT token and user profile)
  - **Errors**: `401 Unauthorized` (Invalid credentials), `400 Bad Request`
  - **Description**: Authenticates admin/users and provides a bearer token.

### 👤 Account Management (`/api/account`)
- `POST /change-name` [JWT]
  - **Success**: `204 No Content`
  - **Errors**: `401 Unauthorized`, `404 Not Found`
  - **Description**: Updates the current user's first and last name.
- `POST /change-password` [JWT]
  - **Success**: `204 No Content`
  - **Errors**: `401 Unauthorized`, `400 Bad Request`
  - **Description**: Updates password after verifying the old one.
- `POST /request-reset` [Public]
  - **Success**: `200 OK`
  - **Errors**: `204 No Content` (If email not found)
  - **Description**: Generates and sends a 6-digit OTP to the user's email.
- `POST /reset-password` [Public]
  - **Success**: `204 No Content`
  - **Errors**: `401 Unauthorized` (Invalid/Expired OTP), `404 Not Found`
  - **Description**: Resets password using email, OTP, and new password.
- `POST /request-admin-otp` [Admin (SuperAdmin Only)]
  - **Success**: `200 OK`
  - **Errors**: `403 Forbidden`, `409 Conflict` (Email exists)
  - **Description**: Sends verification OTP to a potential new admin's email.
- `POST /add-admin` [Admin (SuperAdmin Only)]
  - **Success**: `201 Created`
  - **Errors**: `403 Forbidden`, `400 Bad Request` (Invalid OTP), `409 Conflict`
  - **Description**: Finalizes admin creation using verified OTP. (Requires FirstName and LastName)

### 🚗 Car Management (`/api/car`)
- `GET /statistics` [JWT]
  - **Success**: `200 OK` (Car status counts)
- `GET /` [JWT]
  - **Success**: `200 OK` (Paged list of cars)
- `GET /{id}` [JWT]
  - **Success**: `200 OK` (Detailed car info)
  - **Errors**: `404 Not Found`
- `POST /` [JWT]
  - **Success**: `201 Created`
  - **Errors**: `400 Bad Request` (Owner not found)
- `PUT /{id}` [JWT]
  - **Success**: `204 No Content`
  - **Errors**: `404 Not Found`
- `DELETE /{id}` [JWT]
  - **Success**: `204 No Content`
  - **Errors**: `404 Not Found`
- `PATCH /{id}/status` [JWT]
  - **Success**: `204 No Content`
  - **Errors**: `404 Not Found`

### 📅 Booking Management (`/api/booking`)
- `GET /statistics` [JWT]
  - **Success**: `200 OK` (Active trips, pick-ups, etc.)
- `GET /` [JWT]
  - **Success**: `200 OK` (Paged bookings)
- `GET /{id}` [JWT]
  - **Success**: `200 OK` (Detailed booking info)
  - **Errors**: `404 Not Found`
- `PATCH /{id}/status` [JWT]
  - **Success**: `204 No Content`
  - **Errors**: `404 Not Found`
- `POST /refund-all` [JWT]
  - **Success**: `200 OK` (Count of refunded items)

### 💳 Payment & Paymob (`/api/payment`)
- `GET /statistics` [JWT]
  - **Success**: `200 OK` (Revenue and profit stats)
- `POST /paymob/init` [JWT]
  - **Success**: `200 OK` (Returns `{ payment_id, order_id, payment_token, url, method }`)
  - **Errors**: `400 Bad Request` (Invalid Booking/User ID)
- `GET /paymob/checkout` [JWT]
  - **Success**: `200 OK` (Returns Iframe HTML or Redirect)
- `GET /paymob/callback` [Public]
  - **Success**: `200 OK` (Handles HMAC validation and status updates)
- `POST /paymob/webhook` [Public]
  - **Success**: `200 OK` (Server-to-server payment notifications)
- **Security**: All callbacks (`/callback`) and webhooks (`/webhook`) enforce HMAC validation to ensure requests originate from Paymob.

### 📊 Dashboard (`/api/dashboard`)
- `GET /stats` [JWT]
  - **Success**: `200 OK` (General platform totals)
- `GET /weekly-revenue` [JWT]
  - **Success**: `200 OK` (7-day revenue trend)
- `GET /bookings-by-month` [JWT]
  - **Success**: `200 OK` (Monthly performance)

### 📝 Verification Requests (`/api/request`)
- `GET /` [JWT]
  - **Success**: `200 OK` (Pending user/car requests)
- `GET /{id}` [JWT]
  - **Success**: `200 OK` (Details + verification documents)
  - **Errors**: `404 Not Found`
- `PATCH /{id}/status` [JWT]
  - **Success**: `204 No Content`
  - **Errors**: `404 Not Found`

### 👥 User Management (`/api/user`)
- `GET /` [JWT]
  - **Success**: `200 OK` (Paged user list)
- `GET /{id}` [JWT]
  - **Success**: `200 OK` (User profile details)
  - **Errors**: `404 Not Found`
- `POST /` [JWT]
  - **Success**: `201 Created`
  - **Errors**: `400 Bad Request`
- `PUT /{id}` [JWT]
  - **Success**: `204 No Content`
  - **Errors**: `404 Not Found`
- `DELETE /{id}` [JWT]
  - **Success**: `204 No Content`
  - **Errors**: `404 Not Found`

---

## 🛡️ Global Error Handling
The API includes a **Global Exception Middleware** that captures all unhandled errors and returns a consistent, clean JSON structure:
```json
{
  "statusCode": 400,
  "message": "Friendly error message",
  "details": "Stack trace (only visible in Development mode)"
}
```
*Note: This prevents database-level errors (like Foreign Key violations) from crashing the client or exposing sensitive DB info.*

---

## 🛠️ Installation & Run
1. **Clone & Restore**:
   ```bash
   git clone https://github.com/XMahsec/Rently.Management.git
   dotnet restore
   ```
2. **Database**: Update the connection string in `appsettings.json`.
3. **Secrets**: Set your secrets as described in the Security section above.
4. **Run**:
   ```bash
   dotnet run --project WebApi/Rently.Management.csproj
   ```
5. **Swagger**: Access documentation at `http://localhost:5000/swagger`

---

## 🔗 Outgoing Partner Webhooks
The system can notify external services (e.g., a Flask app) about critical events using the `WebhookService`.
- **Supported Events**: `payment.created`, `payment.updated`, `user.created`, `car.updated`.
- **Security**: Each request includes an `X-Rently-Signature` header (HMACSHA256) for verification.

## 🤝 Contributing
- Open issues and PRs on GitHub.
- Keep endpoint contracts and validation consistent; update `docs/ARCHITECTURE.md` if workflows change.
