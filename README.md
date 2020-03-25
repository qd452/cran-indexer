# cran-indexer


## To access the service

http://35.240.177.243:8080/api/v0/

## Quick Start


### Docker


```sh
docker network create backend
docker-compose up -d --build
```

After deploying to GCP, Create a firewall rule to allow traffic to your instance:


```sh
gcloud compute firewall-rules create default-allow-http-8080 \
    --allow tcp:8080 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --description "Allow port 8080 access to http-server"
```

### Native

```sh
export APP_SETTINGS=webapp.config.DevelopmentConfig

# start consumer worker
celery worker -A celery_worker.celery -Q sync_package,process_package --loglevel=info
# start main applications
python manage.py run -h 0.0.0.0 
```

http://localhost:15672/

http://0.0.0.0:5000/api/v0/

## SQL or NoSQL

After some consideration based on the requirement given. I decided to go for NoSQL and chose the MongoDB as the database for the following reasons

1. For the given Package structure, the data is quite "self-contained". So instead of using the SQL to normalize the data into a many-to-many relationship (table `Package` and table `Person`), I use the de-normalized way to store each package as document in a collection `Package`
2. As based on the requirements, this web application should be a read heavy application, and the only query we need perform is query by the `Package Name` and no need to perform any search based on the person. That's why no need to de-normalize the data and use `JOIN` to return the while package information during query, which may create the a bit of overhead.
3. schema flexibility of the NoSQL gives us the freedom to add any new fields in the future.
4. Better support in regex search index