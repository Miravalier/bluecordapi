# Overview

A simple python script running FastAPI and google recaptcha to implement
a "contact us" form. When a user clicks send on the form, the server sends an email
to the `ADMIN_EMAIL` set in the .env using the SMTP credentials configured. It was
written for bluecordcomputing.com, but it is pretty generic and will probably work
anywhere.

# Running the API

## Copy the file `example.env` to `.env`
```bash
cp example.env .env
```
## Edit the .env file and fill in every parameter
```bash
nano .env
```

## Build and run the docker container
```bash
docker-compose build
docker-compose up -d
```

# See it in action
https://www.bluecordcomputing.com/#contact
