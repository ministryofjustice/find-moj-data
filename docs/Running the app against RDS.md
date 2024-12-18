# Running the app against the RDS database(s)

The database settings in the application are such that for local development an sqlite db will be created.
However if there is a usecase to target one of the RDS environments then you will need to carry out the following steps.
It is important to note that to access the rds environment you will need to create a loopback connection which means opening a local free
port on your machine for the postgres connection, the loopback connection then forwards matching traffic to a dedicated port forward pod, which inturn forwards
to the specified rds environment. Please pay particular attention to the port numbers that have been specified in the examples. We have used port 1234 for
the local port.

1.  Create a loop back pod for the given namespace. Note all ports are standard postgres port 5432 for this command.
    ```
    kubectl -n data-platform-find-moj-data-dev \
    run port-forward-pod \
    --image=ministryofjustice/port-forward \
    --port=5432 \
    --env="REMOTE_HOST=cloud-platform-2d5acdf1ab5379e3.cdwm328dlye6.eu-west-2.rds.amazonaws.com" \
    --env="LOCAL_PORT=5432" \
    --env="REMOTE_PORT=5432"
    ```
2.  Forward traffic from your local host to the remote pod and keep the connection open. Note the use of local port of 1234.

    ```
    kubectl -n data-platform-find-moj-data-dev port-forward port-forward-pod 1234:5432
    ```

3.  You can test connectivity as follows using postgres utility psql.Note the use of localhost and local port 1234.

    ```
    psql postgres://< Database Username >:< Database Password >@localhost:1234/< Database Name >
    ```

    ```
    psql (14.11 (Homebrew), server 16.3)
    WARNING: psql major version 14, server major version 16.
            Some psql features might not work.
    SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
    Type "help" for help.

    db2d5acdf1ab5379e3=>
    ```

4.  Via Netcat. Note the use of localhost and local port 1234.

    ```
    nc -z localhost 1234
    ```

    ```
    Connection to localhost port 1234 [tcp/search-agent] succeeded!
    ```

5.  Optionally populate the .env file if you dont already have one. Add additional environment variables required for RDS.
    Note the value of `RDS_INSTANCE_ADDRESS` as `docker.for.mac.host.internal`. This is a special requirment for accessing local connections through docker containers on MAC OS.

        ```
        op inject --in-file .env.tpl --out-file .env
        ```

        ```
        RDS_INSTANCE_ADDRESS=docker.for.mac.host.internal
        DATABASE_NAME=< 1pass >
        DATABASE_USERNAME=< 1pass >
        DATABASE_PASSWORD=< 1pass >
        ```

6.  In order for the application to utilise the loopback connection you have created in the steps above, you will need to change the postgres port number in the Django settings file `settings.py` and addionally in the startup script ```./scripts/app-entrypoint.sh` if you are running as a docker image, to match the local port value used for the loopback connection i.e. `1234` in our examples.

    ```
    "default": {
        "ENGINE": (
            "django.db.backends.postgresql"
            if os.environ.get("RDS_INSTANCE_ADDRESS")
            else "django.db.backends.sqlite3"
        ),
        "NAME": os.environ.get("DATABASE_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("DATABASE_USERNAME", ""),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD", ""),
        "HOST": os.environ.get("RDS_INSTANCE_ADDRESS", ""),
        "PORT": "1234",
    }
    ```

    If running the app on the development server rather than as a docker image, ignore changing the startup script value as below.

    ```
    if [ -n "$RDS_INSTANCE_ADDRESS" ]; then
      echo "Waiting for postgres..."

      while ! nc -z $RDS_INSTANCE_ADDRESS 1234; do
        sleep 0.1
      done

      echo "PostgreSQL started"
    fi
    ```

7.  Building and running as a Docker image.

    ```
    docker build -t find-moj-data:latest . && docker run --env-file .env -it -p 8000:8000 find-moj-data:latest
    ```

8.  Alternatively run the development server

    ```
    poetry run python manage.py collectstatic --noinput
    poetry run python manage.py migrate
    poetry run python manage.py waffle_switch search-sort-radio-buttons off --create
    poetry run python manage.py runserver
    ```

9.  The app should be running at http://localhost:8000

10. Delete the port forward pod

    `kubectl delete pod port-forward-pod -n data-platform-find-moj-data-dev`

## Contributing

Run `pre-commit install` from inside the poetry environment to set up pre commit hooks.

- Linting and formatting handled by `black`, `flake8`, `pre-commit`, and `isort`
  - `isort` is configured in `pyproject.toml`
- `detect-secrets` is used to prevent leakage of secrets
- `sync_with_poetry` ensures the versions of the modules in the pre-commit specification
  are kept in line with those in the `pyproject.toml` config.

## Testing

- All tests `make test`
- Unit tests: `make unit`
- Integration tests: `make integration`

Selenium makes use of chromedriver to run a headless browser.
As either the chrome browser or chromedriver are updated,
the local version of chromedriver and chrome may drift apart.
If so, update both to the latest version: update your local chrome
and run `npm install -g chromedriver chromedriver@latest` to install the latest chromedriver.

## Frontend styling

If making changes to the scss, to ensure your changes are reflected in local deployments, run:
`make build` to update the css files.
