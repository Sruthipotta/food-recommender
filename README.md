# How to Run This Application

This guide will walk you through the steps to set up and run this Django application on your local machine.

---

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.x
- Git
- Virtualenv (optional but recommended)

---

## Setup Instructions

### 1. Clone the Repository
Clone the repository to your local machine using the following command:
```bash
git clone <repository-url>
```
### 2. Create and Activate a Virtual Environment
Navigate to the project directory and create a virtual environment:
```bash
cd <project-directory>
python -m venv venv
```
Activate the virtual environment:

- On Windows:
	```bash
	venv\Scripts\activate
	```
- On macOS/Linux:
	```bash
	source venv/bin/activate
	```
### 3. Install Dependencies
Install the required Python packages using:

```bash
pip install -r requirements.txt
```
### 4. Set Up the Database

Run the following commands to create and apply database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser

Create a superuser account to access the Django admin panel:
```bash
python manage.py createsuperuser
```

### 6. Populate the Database with Food Items

Run the following script to populate the database with food-related data:
```bash
python populate_food_items.py
```

### 7. Launch the Django REST API Server

Start the development server using:
```bash
python manage.py runserver
```
The server will be available at http://localhost:8000/.


## Accessing the API Documentation

1.  **Log in to Django Admin**:  
    Visit  `http://localhost:8000/admin/`  and log in using your superuser credentials.
    
2.  **View API Documentation**:  
    After logging in, go to  `http://localhost:8000/api/swagger/`  to access the API documentation.


## Notes from the Developer

1.  **Learning AI/ML Skills**:  
    While I didn’t have prior experience with AI/ML, I dedicated time to learn and implement a recommendation system for this project. I watched numerous videos and tutorials to understand the concepts, and despite the challenges, I successfully completed the project within the deadline.
    
2.  **Data Collection**:  
    Since no datasets or APIs were provided, I web-scraped data from the Swiggy website using JavaScript in the browser console. This allowed me to gather the necessary data for the project.
    
3.  **Database Credentials**:  
    For the purpose of this assessment, I hardcoded the database credentials in the configuration. However, in real-world projects, I would use  `.env`  files to securely store sensitive information like credentials.
