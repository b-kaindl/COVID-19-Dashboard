import dash
from flask_caching import Cache

# get bootstrap stylesheet
external_stylesheets = [
"https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css"
]

# create app instance
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# set cache config
config = {
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DIR": "cache"
}

# initialize cache for underlying flask app
cache = Cache(app.server, config=config)
