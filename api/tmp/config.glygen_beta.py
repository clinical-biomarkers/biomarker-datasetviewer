DEBUG = False
TESTING = False

SERVER = "beta"
DB_HOST = "mongodb://10.10.0.6:27017"

DB_NAME = "glydb_beta"
DB_USERNAME = "glydb_betaadmin"
DB_PASSWORD = "glydb_betapass"
DATA_PATH = "/data/shared/glygen"


SECRET_KEY = "9012b212ce1d1184eb764492727ba34ec30e2c98f64406e1ef6a967816011e85"
JWT_SECRET_KEY = "9012b212ce1d1184eb764492727ba34ec30e2c98f64406e1ef6a967816011e85"
SESSION_COOKIE_SECURE = True
JWT_TOKEN_LOCATION = ['cookies']
JWT_COOKIE_SECURE = False
JWT_ACCESS_COOKIE_PATH = '/'
JWT_REFRESH_COOKIE_PATH = '/'
JWT_COOKIE_CSRF_PROTECT = True
JWT_CSRF_IN_COOKIES = False

    



