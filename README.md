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

## Deployment

```
docker-compose up --build --d
```
