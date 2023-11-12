# Train Station API service
This is a restful API built to provide endpoints to manage the workflow of a railroad station.

## Installation:
1. Clone the repository
```bash 
git clone https://github.com/sashabryl/train-station-api-service.git
```
2. Go to the project directory
```bash
cd train-station-api-service
```
3. Create a virtual environment
```bash
python -m venv venv
```
4. Activate the virtual environment
- on Windows:
```bash
.\venv\Scripts\activate
```
- on Linux/MacOS:
```bash
- source venv/bin/activate
 ```
5. Install dependencies
```bash
pip install -r requirements.txt
```

6. Create a copy of the .env.sample file and name it .env.
Update the values as needed.
```bash
cp .env.sample .env
```

## Getting started
1. Build and run the docker container in detached mode.
```bash
docker-compose build
docker-compose up -d
```
2. Find out the id of container containing the app:
```bash
docker ps
```
3. Create an admin user
```bash
docker exec -it <container_id> python manage.py createsuperuser
```
## Usage
- You can visit the admin page at
```bash
http://127.0.0.1:8000/admin/
```
- Or go to the main page at
```bash
http://127.0.0.1:8000/api/train-station/
```
- To learn about all the endpoints, see the documentation
```bash
http://127.0.0.1:8000/api/schema/swagger/
```
## Features
- JWT Authentication
- Managing orders and tickets
- Adding other stations
- Routes management
- Journeys management
- Trains management
- Staff management
- Diverse filtering of routes, stations, crews, journeys

## Testing
- To run the tests, use the following command:
```bash
python manage.py test
```
