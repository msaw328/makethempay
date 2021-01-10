## Initialization
Set up virtual environment:

```
python3 -m venv venv                # creates venv directory
. venv/bin/activate                 # changes prompt
pip install wheel                   # sometimes next step does not work without wheel
pip install -r requirements.txt     # installs requirements in the venv directory
```

After running ```venv/bin/activate``` one can execute ```deactivate``` to revert to original environment.

## Running
In order to run this app you have to start postgres instance on default port on localhost.

Use ```run_uwsgi``` if you have uwsgi installed. It runs the app in development environment by default, can change to production if given "prod" as an argument.

App listens on localhost on default port of 5000.

## DB model
The database description can be found in ```doc/makethempay.dbm```. It can be opened in pgModeler.
Recreate database by running ```init_db.sh``` which runs ```sql/init_db.sql``` through psql.
