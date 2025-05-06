# Smart Home Energy Management System

This is a final year Computer Science project that aims to help users monitor, predict and automate their home energy usage

## Project Structure 
- backend/energy - Django server for APIs, data handling, authentication, automation and database management 
- backend/ml-service - Flask app with machine learning models for energy and solar predictions 
- frontend/ - Vue.js app for user interface and data visualisation 
- backup-data/ - Backed-up CSV data
- scripts/ - Scripts for generating solar data and importing saved data 

## Features
- Real time energy consumption and solar power display 
- Machine learning predictions for energy consumption and solar power
- Automation rules based on predictions and user preferences 
- Community page to share automation rules and energy saving strategies 
- Custom user accounts and login/logout

## Backend setup

To run the backend of this project locally follow these steps:

1. Navigate to the backend folder, then create and activate a virtual environment 

    ```console
    cd backend
    python -m venv venv
    venv/Scripts/activate
    ```

2. Install dependencies:

    ```console
    pip install -r requirements.txt
    ```

3. Apply Migrations 

    ```console
    python manage.py makemigrations
    python manage.py migrate
    ```

4. Run the server: 

    ```console
    python manage.py runserver
    ```

## Flask setup

To run the Flask machine learning server of this project locally follow these steps:

1. Open a new terminal and nabvgate to the ml-lservice  folder, then activate the virtual environment 

    ```console
    cd backend
    cd ml-service
    venv/Scripts/activate
    ```

2. Install dependencies:

    ```console
    pip install -r requirements.txt
    ```

3. Run the server: 

    ```console
    python app.py
    ```

## Frontend setup

To run the frontend of this project locally follow these steps:

1. Open a new terminal and navigate to the frontend folder, and activate the virtual environment 

    ```console
    cd frontend
    venv/Scripts/activate
    ```

2. Install dependencies:

    ```console
    npm install 
    ```

3. Start the server: 

    ```console
    npm run serve
    ```

Make sure the Django backend is running on 127.0.0.1:8000 and Flask on 127.0.0.1:5001

## Running the Project

1. Start all 3 servers: Django, Flask, and Vue

2. Visit http://localhost:8080 in your browser

3. Sign up and explore dashboard, predictions, automation, and community features