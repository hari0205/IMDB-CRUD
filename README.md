## Description
IMDB like movie database application using Python and Flask

## Prerequisites
This project requires SQLite and Redis. Connect to an instance running on your local machine or use docker.
- Docker: [Install Docker](https://docs.docker.com/get-docker/)


## Installation

1. Clone this repository. 
2. Navigate to the project directory.
3. Create a `.env` file and place all variables required (Refer sample.env)
4. Create `.flaskenv` file and place all variables required (Refer flaskenv-sample)


### Method 1: Run locally
- To run locally, follow these steps
1. Run `pip install -r requirements.txt` to install dependencies
2. Run  `flask run` to start the application.
- Note: When running the application for the first time, you may need to run migrations. Run the following(no setup necessary)
-  `flask db init` Initialize migrations
- `flask db migrate` Apply migrations
- `flask db upgrade` Run migrations
- or just run `migrate.sh` script with a message. eg. `./migrate.sh "First run"`

### Method 2: Run using Containers
- To run containerised application
1. From the project directory, Run `docker compose up --build`
2. This will automatically install all the requirements and DB.

### Load sample data
- To load sample dataset: Hit `/load` endpoint.
- To clear all data: Hit `/clear` endpoint. 


## Documentation
- To access documentation for the api, access `/docs/v1/swagger-ui` endpoint.
