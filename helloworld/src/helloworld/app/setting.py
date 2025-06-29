import os
from pathlib import Path
from platformdirs import user_log_dir, user_data_dir


app_name = "xplay"
app_author = "JerryZhen"

default_host = "0.0.0.0"
default_port = "9090"

host = os.getenv('HOST',default_host)
port_str = os.getenv("PORT", default_port)
port = int(port_str)

######  log file #######
default_log_path = user_log_dir(app_name, app_author)
log_path = os.getenv("LOG_PATH", default_log_path)
Path(log_path).mkdir(parents=True, exist_ok=True)

log_level = os.getenv("LOG_LEVEL", "info")
logfile = Path(log_path).joinpath("app.log")
print("log_path=",log_path)


######  Data file #######
default_data_path = Path(user_data_dir(app_name, app_author)).joinpath("Data")
data_path = os.getenv("DATA_PATH", default_data_path)
Path(data_path).mkdir(parents=True, exist_ok=True)

db_name = os.getenv("DBNAME", "app.db")
print(data_path, db_name)

sched_path = Path(data_path).joinpath("sched.db")
print(f"sched_path={sched_path}")

iotdb_path = Path(data_path).joinpath("iot.db")
print(f"iotdb_path={iotdb_path}")

app_db_path = Path(data_path).joinpath("app.db")
print(f"app_db_path={app_db_path}")

cache_path = Path(data_path).joinpath("cache.db")
print(f"cache_path={cache_path}")


######  Frontpage file #######
app_path = Path(__file__).resolve().parent.parent
defualt_front_path = app_path.joinpath("resources", "dist")
frontpath =Path(os.getenv("DIST_PATH", defualt_front_path)) 
print(f"frontpath={frontpath}")
