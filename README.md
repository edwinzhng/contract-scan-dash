# Contract Scan Dash

Alerting dashboard for contracts

## Database

Autogenerate migrations
```
docker-compose run api alembic revision --autogenerate -m "Migration name"
```

Apply migrations
```
docker-compose run api alembic upgrade head
```

Accessing the container
```
docker exec -it postgres sh
```

## Deployment

```
docker-compose up --build --d
```
