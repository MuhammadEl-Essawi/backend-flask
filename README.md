Car Rental Backend (Flask)

This is the backend service for the Car Rental Platform, built with Flask, SQLAlchemy, and JWT authentication.
It provides APIs for user authentication, car management, bookings, and payments.




 Setup Instructions

1️⃣ Clone the repository

Bash


git clone https://github.com/your-username/car_rental_backend.git
cd car_rental_backend


2️⃣ Create and activate a virtual environment

Bash


python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Linux/Mac:
source venv/bin/activate


3️⃣ Install dependencies

Bash


pip install -r requirements.txt


4️⃣ Initialize the database

Bash


python create_db.py


5️⃣ Run the server

Bash


python manage.py


The server will start on:
👉 http://127.0.0.1:5000

 Environment Variables

Copy .env.template to .env and update values:

Bash


cp .env.template .env


Example .env:

Plain Text


FLASK_ENV=development
SECRET_KEY=change_this_secret
DATABASE_URL=sqlite:///data.db
JWT_SECRET_KEY=change_this_jwt_secret


 Run with Docker

1️⃣ Build the Docker image

Bash


docker build -t car_rental_backend .


2️⃣ Run the container

Bash


docker run -p 5000:5000 --env-file .env car_rental_backend


3️⃣ Or use Docker Compose

Bash


docker-compose up --build


 Push to Docker Hub

1️⃣ Login to Docker Hub

Bash


docker login


2️⃣ Tag the image

Bash


docker tag car_rental_backend your-dockerhub-username/car_rental_backend:latest


3️⃣ Push the image

Bash


docker push your-dockerhub-username/car_rental_backend:latest


4️⃣ Run from Docker Hub (any machine)

Bash


docker pull your-dockerhub-username/car_rental_backend:latest
docker run -p 5000:5000 your-dockerhub-username/car_rental_backend:latest


 Project Structure

Plain Text


car_rental_backend/
│── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── cars.py
│   │   ├── bookings.py
│   │   └── payments.py
│   └── schemas.py
│── requirements.txt
│── manage.py
│── create_db.py
│── Dockerfile
│── docker-compose.yml
│── .dockerignore
│── .env.template
│── README.md


 GitHub Workflow

1️⃣ Initialize Git (first time only)

Bash


git init


2️⃣ Add remote repository

Bash


git remote add origin https://github.com/your-username/car_rental_backend.git


3️⃣ Stage and commit changes

Bash


git add .
git commit -m "Initial commit"


4️⃣ Push to GitHub

Bash


git push -u origin main


 API Documentation (Postman)

 Auth Routes

Register

POST /auth/register

Body (JSON):

JSON


{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "123456",
  "role": "renter"
}


Login

POST /auth/login

Body (JSON):

JSON


{
  "email": "john@example.com",
  "password": "123456"
}


Response:

JSON


{
  "message": "Login successful",
  "access_token": "your_jwt_token",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "renter"
  }
}


 Car Routes

Add Car (Owner only)

POST /cars

Headers:

Plain Text


Authorization: Bearer <your_token>


Body (JSON):

JSON


{
  "brand": "Toyota",
  "model": "Corolla",
  "year": 2022,
  "price_per_day": 500
}


List Cars

GET /cars

 Booking Routes

Create Booking (Renter only)

POST /bookings

Headers:

Plain Text


Authorization: Bearer <your_token>


Body (JSON):

JSON


{
  "car_id": 1,
  "start_date": "2025-09-20",
  "end_date": "2025-09-25"
}


 Payment Routes

Make Payment

POST /payments

Headers:

Plain Text


Authorization: Bearer <your_token>


Body (JSON):

JSON


{
  "booking_id": 1,
  "amount": 2500,
  "method": "credit_card"
}


📎 Notes

•
Do NOT commit .env or data.db to GitHub (already in .gitignore).

•
Use .env.template as a guide for environment variables.

•
Make sure Docker Desktop is running before using Docker commands.

•
Always include the Authorization header for protected routes.




