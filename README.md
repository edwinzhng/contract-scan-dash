# FTM Contract Dash

Alerting dashboard for FTM contracts

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
