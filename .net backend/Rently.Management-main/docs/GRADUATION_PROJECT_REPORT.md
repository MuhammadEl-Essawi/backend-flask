# Graduation Project Report: Rently Management System

## 1. Introduction
The **Rently Management System** is the core backend engine responsible for the operations of an integrated car rental platform. The system aims to provide a secure, stable, and scalable environment for managing users, vehicles, bookings, and payments. It serves as the central hub connecting the mobile application (Flutter), partner systems (Flask), and electronic payment gateways.

### Technology Choice Rationale
Modern Microsoft technologies were chosen to build this system based on several strategic factors:
- **.NET 9**: The latest version of the .NET ecosystem, providing high performance and full support for distributed systems.
- **C#**: A powerful, strongly-typed language that supports object-oriented programming and modern patterns, reducing runtime errors.
- **Entity Framework Core**: A professional ORM tool that allows database interaction through code objects, facilitating maintenance and a "Code-First" development approach.
- **SQL Server**: A robust relational database ensuring data integrity and the capability to handle large volumes of transactions.
- **Google OAuth 2.0 & SMTP**: Integrated for secure external authentication and automated email communication (e.g., OTP delivery).

---

## 2. Architecture & Design Patterns

### Clean Architecture
The project follows the Clean Architecture pattern to ensure a strict separation of concerns:
1. **Domain Layer**: Contains core entities, business logic, and repository interfaces.
2. **Infrastructure Layer**: Handles technical details such as database access and repository implementations.
3. **WebApi Layer**: The interface for external communication, containing Controllers and DTOs (Data Transfer Objects).

### Design Patterns
- **Repository Pattern**: Used to decouple data access logic from the business logic in Controllers.
- **Dependency Injection (DI)**: Manages object lifecycles and reduces direct dependencies between components, enhancing testability.
- **Middleware Pattern**: Handles cross-cutting concerns, such as Global Error Handling and Authentication.

#### Controller-Service Communication
The Controller acts as an orchestrator; it receives an HTTP request, validates it using DTOs, and then invokes the appropriate Repository or Service to execute the business logic. Finally, it returns a standard HTTP response to the client.

---

## 3. Database & Data Management

### Entity-Relationship Diagram (ERD)
The database is designed to be fully relational (Normalized) to ensure data consistency:
```mermaid
erDiagram
    USER ||--o{ CAR : owns
    USER ||--o{ BOOKING : rents
    USER ||--o{ PAYMENT : pays
    USER ||--o{ REVIEW : writes
    USER ||--o{ NOTIFICATION : receives
    USER ||--o{ FAVORITE : marks
    USER ||--o{ MESSAGE : sends
    USER ||--o{ MESSAGE : receives
    USER ||--o{ OTP : has

    CAR ||--o{ BOOKING : has
    CAR ||--o{ REVIEW : gets
    CAR ||--o{ CARIMAGE : has
    CAR ||--o{ CARUNAVAILABLEDATE : blocks
    CAR ||--o{ FAVORITE : featuredIn

    BOOKING ||--o{ PAYMENT : generates

    USER {
      int Id PK
      string FirstName
      string LastName
      string Email UNIQUE
      string Phone UNIQUE
      string Role "Owner, Renter, Admin"
      bool IsSuperAdmin
      string ApprovalStatus "Pending, Approved, Rejected"
      string Nationality
      string PreferredLanguage
      string LicenseNumber
      string PayoutMethod
      string PayoutDetails
      string BillingCountry
      string ZipCode
      string PasswordHash
      string PasswordSalt
      string PasswordResetToken
      datetime PasswordResetTokenExpires
      string IdImage
      string LicenseImage
      string PassportImage
      string SelfieImage
      string ResidenceProofImage
      string JobProofImage
      datetime CreatedAt
      datetime UpdatedAt
    }
    CAR {
      int Id PK
      int OwnerId FK
      string Brand
      string Model
      int Year
      decimal PricePerDay
      string Status "Available, Rented, Maintenance"
      string Transmission "Manual, Automatic"
      string Color
      string LocationCity
      decimal AverageRating
      string Features
      string Description
      string LicensePlate
      string CarLicenseImage
      datetime CreatedAt
      datetime UpdatedAt
    }
    BOOKING {
      int Id PK
      int CarId FK
      int RenterId FK
      datetime StartDate
      datetime EndDate
      string Status "Pending, Confirmed, Completed, Cancelled"
      string TransactionId
      decimal TotalPrice
      decimal PaidAmount
      datetime PaymentConfirmedAt
      datetime CreatedAt
      datetime UpdatedAt
    }
    PAYMENT {
      int Id PK
      int BookingId FK
      int UserId FK
      decimal Amount
      string Currency "SAR, EGP"
      string Status "Pending, Succeeded, Failed, Refunded"
      string Provider "Paymob, Stripe"
      string ProviderPaymentId
      string ProviderReceiptUrl
      string FailureCode
      string FailureMessage
      datetime CreatedAt
      datetime UpdatedAt
    }
    REVIEW {
      int Id PK
      int RenterId FK
      int CarId FK
      int Rating "1-5"
      string Comment
      datetime CreatedAt
      datetime UpdatedAt
    }
    NOTIFICATION {
      int Id PK
      int UserId FK
      string Title
      string Message
      string Type "info, booking, payment"
      bool IsRead
    }
    MESSAGE {
      int Id PK
      int SenderId FK
      int ReceiverId FK
      string Content
      bool IsRead
    }
    OTP {
      int Id PK
      int UserId FK
      string OtpHash
    }
    CARIMAGE {
      int Id PK
      int CarId FK
      string ImagePath
    }
    CARUNAVAILABLEDATE {
      int Id PK
      int CarId FK
      datetime StartDate
      datetime EndDate
      string Reason
    }
```
*(Note: The schema has been updated to include FirstName, LastName, and IsSuperAdmin for enhanced security and identity management).*

### Class Diagram (Detailed)
The following diagram illustrates the relationship between the core system components and their attributes:
```mermaid
classDiagram
    class AuditableEntity {
      +DateTime CreatedAt
      +DateTime? UpdatedAt
    }
    class User {
      +int Id
      +string FirstName
      +string LastName
      +string Email
      +string Phone
      +string Role
      +bool IsSuperAdmin
      +string ApprovalStatus
      +string Nationality
      +string PreferredLanguage
      +string LicenseNumber
      +string PayoutMethod
      +string PayoutDetails
      +string BillingCountry
      +string ZipCode
      +string PasswordHash
      +string PasswordSalt
      +string PasswordResetToken
      +DateTime? PasswordResetTokenExpires
      +string IdImage
      +string LicenseImage
      +string PassportImage
      +string SelfieImage
      +string ResidenceProofImage
      +string JobProofImage
      +List~Car~ OwnedCars
      +List~Booking~ BookingsAsRenter
      +List~Review~ Reviews
      +List~Notification~ Notifications
      +List~Favorite~ Favorites
      +List~Message~ SentMessages
      +List~Message~ ReceivedMessages
      +List~Otp~ Otps
      +List~Payment~ Payments
    }
    class Car {
      +int Id
      +int OwnerId
      +string Brand
      +string Model
      +int Year
      +decimal PricePerDay
      +string Status
      +string Transmission
      +string Color
      +string LocationCity
      +decimal AverageRating
      +string Features
      +string Description
      +string LicensePlate
      +string CarLicenseImage
      +User Owner
      +List~Booking~ Bookings
      +List~Review~ Reviews
      +List~CarImage~ Images
      +List~CarUnavailableDate~ UnavailableDates
      +List~Favorite~ Favorites
    }
    class Booking {
      +int Id
      +int CarId
      +int RenterId
      +DateTime StartDate
      +DateTime EndDate
      +string Status
      +string TransactionId
      +decimal TotalPrice
      +decimal PaidAmount
      +DateTime? PaymentConfirmedAt
      +Car Car
      +User Renter
      +List~Payment~ Payments
    }
    class Payment {
      +int Id
      +int BookingId
      +int? UserId
      +decimal Amount
      +string Currency
      +string Status
      +string Provider
      +string ProviderPaymentId
      +string ProviderReceiptUrl
      +string FailureCode
      +string FailureMessage
      +Booking Booking
      +User User
    }
    
    AuditableEntity <|-- User
    AuditableEntity <|-- Car
    AuditableEntity <|-- Booking
    AuditableEntity <|-- Payment
    AuditableEntity <|-- Review
    
    User "1" --> "many" Car : owns
    User "1" --> "many" Booking : rents
    User "1" --> "many" Payment : pays
    User "1" --> "many" Notification : receives
    User "1" --> "many" Favorite : marks
    User "1" --> "many" Message : sends/receives
    User "1" --> "many" Otp : has
    
    Car "1" --> "many" Booking : has
    Car "1" --> "many" Review : gets
    Car "1" --> "many" CarImage : has
    Car "1" --> "many" CarUnavailableDate : blocks
    Car "1" --> "many" Favorite : featuredIn
    
    Booking "1" --> "many" Payment : generates
```

---

## 4. System Workflows (Logic Flow)

This section details the critical operational flows within the Rently Management system.

### 4.1. Authentication & Security
#### Login Workflow
```mermaid
graph TD
    A[Client sends POST /api/auth/login] --> B{Verify Credentials}
    B -- Valid --> C[Generate JWT Token]
    B -- Invalid --> D[Return 401 Unauthorized]
    C --> E[Return 200 OK + Token]
```

#### Password Reset (OTP Flow)
```mermaid
graph TD
    A[POST /api/account/request-reset] --> B{User Exists?}
    B -- Yes --> C[Generate 6-digit OTP]
    C --> D[Send OTP via Google SMTP]
    D --> E[Store OTP in DB with 10m Expiry]
    E --> F[Return 200 OK]
    B -- No --> G[Return 204 No Content]
    
    H[POST /api/account/reset-password] --> I{Verify OTP & Email}
    I -- Valid --> J[Hash New Password]
    J --> K[Update DB & Clear OTP]
    K --> L[Return 204 No Content]
    I -- Invalid/Expired --> M[Return 401 Unauthorized]
```

#### Add Admin (OTP Flow)
```mermaid
graph TD
    A[SuperAdmin requests OTP for new admin] --> B{Is SuperAdmin?}
    B -- Yes --> C[Generate OTP & Send to New Admin]
    C --> D[SuperAdmin sends POST /add-admin + OTP]
    D --> E{Verify OTP}
    E -- Valid --> F[Create Admin User]
    F --> G[Return 201 Created]
    E -- Invalid --> H[Return 400 Bad Request]
    B -- No --> I[Return 403 Forbidden]
```

### 4.2. User Onboarding & Verification
```mermaid
graph TD
    A[User Registers] --> B[Upload ID/License/Selfie]
    B --> C[Status: Pending]
    C --> D[Admin Reviews Documents]
    D --> E{Approve?}
    E -- Yes --> F[Status: Approved]
    E -- No --> G[Status: Rejected]
```

### 4.3. Car Management
```mermaid
graph TD
    A[Owner creates Car Listing] --> B[Upload Car Images/License]
    B --> C[Status: Pending]
    C --> D[Admin Reviews Listing]
    D --> E{Approve?}
    E -- Yes --> F[Status: Available]
    E -- No --> G[Status: Rejected]
```

### 4.4. Booking Process
```mermaid
graph TD
    A[Renter selects Car & Dates] --> B[POST /api/booking]
    B --> C[Status: Pending]
    C --> D[Payment Initiation]
    D --> E{Payment Success?}
    E -- Yes --> F[Status: Confirmed]
    E -- No --> G[Status: Cancelled/Pending]
```

### 4.5. Payment Integration (Paymob)
```mermaid
graph TD
    A[POST /paymob/init] --> B[Auth with Paymob API]
    B --> C[Create Paymob Order]
    C --> D[Generate Payment Token]
    D --> E[Return Token + Iframe URL]
    E --> F[Client Completes Payment]
    F --> G[Paymob sends Webhook/Callback]
    G --> H{Verify HMAC Signature}
    H -- Valid --> I[Update Payment & Booking Status]
    I --> J[Notify Partner via Webhook]
```

### 4.6. Refund Process
```mermaid
graph TD
    A[Admin initiates Refund] --> B{Payment exists & Succeeded?}
    B -- Yes --> C[Create new Refund record]
    C --> D[Update original Payment to 'Refunding']
    D --> E[Notify Partner via Webhook]
    E --> F[Return 200 OK]
    B -- No --> G[Return 404/400 Error]
```

### 4.7. Partner Integration (Flask Webhooks)
```mermaid
graph TD
    A[.NET Event Triggered] --> B[WebhookService.PublishAsync]
    B --> C{Webhooks Enabled?}
    C -- Yes --> D[Construct JSON Envelope]
    D --> E[Compute HMAC Signature]
    E --> F[Send POST to Flask URL]
    F --> G[Flask App receives Request]
    G --> H{Verify Signature Header}
    H -- Valid --> I[Flask App processes Data]
    H -- Invalid --> J[Flask App rejects Request]
    C -- No --> K[Exit]
```

### 4.8. Dashboard & Statistics
```mermaid
graph TD
    A[GET /api/dashboard/stats] --> B[Calculate Total Revenue]
    B --> C[Count Active Users/Cars/Bookings]
    C --> D[Generate Charts Data]
    D --> E[Return Comprehensive JSON]
```

### 4.9. Global Error Handling
```mermaid
graph TD
    A[Any Exception Occurs] --> B[ExceptionMiddleware catches it]
    B --> C[Log error details]
    C --> D{Is Development?}
    D -- Yes --> E[Return JSON with Stack Trace]
    D -- No --> F[Return Friendly JSON Message]
```

---

## 5. RESTful APIs & Integration

The system is built with an **API-First** philosophy, enabling multiple platforms to consume the same data.

### Endpoint Structure
Routes follow standard REST principles:
- `GET /api/resource`: Fetch data.
- `POST /api/resource`: Create a new record.
- `PUT /api/resource/{id}`: Full update.
- `PATCH /api/resource/{id}`: Partial update (e.g., account status).
- `DELETE /api/resource/{id}`: Soft or hard deletion.

### Flask Integration (Partner Webhooks)
The system utilizes **Webhooks** to communicate with the Flask partner application. When a specific event occurs (e.g., a successful payment), the backend sends a JSON payload to the Flask URL with an **HMAC Signature** to ensure the data is authentic and originates from a trusted source.

### Frontend Integration
Communication is handled via HTTP requests, with a **JWT (JSON Web Token)** passed in the header for authorized requests. Data is exchanged exclusively in JSON format using **Snake Case** naming conventions to match mobile app standards.

---

## 6. Security & Authentication
A multi-layered security system has been implemented to protect user data and financial transactions:

### 1. JWT & Google OAuth 2.0 Authentication
The system supports two main authentication methods:
- **JWT Authentication**: Upon standard login, an encrypted token is generated containing user identification and claims (roles). This token has a specific expiration time and is verified programmatically for every request.
- **Google OAuth 2.0**: For seamless onboarding, users can authenticate using their Google accounts. The backend verifies the Google ID Token and maps the user to the system's identity schema.

### 2. Super Admin Protection
A dedicated `IsSuperAdmin` field exists in the database. This field is protected and cannot be modified via any public API. It is set manually or through secure system configurations. Only a Super Admin has the authority to add new administrative accounts.

### 3. Password Hashing
Passwords are never stored as plain text. We utilize industry-standard hashing algorithms with a unique **Salt** for each user to prevent Rainbow Table attacks.

### 4. HMAC Verification
For payment gateway (Paymob) and Flask integrations, we use **HMAC (Hash-based Message Authentication Code)** to ensure data has not been tampered with during transit.

---
**Prepared by:** [Mahmoud Samir Mohamed Mohamed]

**Supervised by:** [Dr.Shimaa Abo Elgob]

**Academic Year:** 2025/2026
