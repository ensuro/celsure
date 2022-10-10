# Celsure

This repository manages the collection of data and the workflow for cel phone insurance. 
It's developed using Django and Postgresql as a database.

## Requirements

Docker and Docker compose.

## Development

The development environment is prepared for running inside a docker container defined in the Dockerfile.

Launching docker-compose:

```bash
if [ ! -f .env.dev ]; then
    cp .env.sample .env.dev
    $EDITOR .env.dev
fi # env-file required by docker-compose.override.dev.yml
docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml up --build
```

Also you can launch the docker environment using [invoke tasks](http://www.pyinvoke.org/), but before you need to run `pip install inv-py-docker-k8s-tasks` to install a package with common tasks for coding inside docker. Then with `inv start-dev` you should be able to launch the docker environment. Then you can run specific tasks:

- `inv django`: starts the Django development server inside Docker
- `inv shell`: enters into the container

The Postgresql database will be stored inside the folder `data`.

To initialize your local database (inside `inv shell`):

```bash
./manage.py migrate
./manage.py createsuperuser
```

Then you can start the development server (`inv django`) and browse to the Django Admin: http://localhost:38000/admin/

## Contributing

Thank you for your interest in Ensuro! Head over to our [Contributing Guidelines](CONTRIBUTING.md) for instructions on how to sign our Contributors Agreement and get started with
Ensuro!

Please note we have a [Code of Conduct](CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.

## Authors

- _Guillermo M. Narvaja_
