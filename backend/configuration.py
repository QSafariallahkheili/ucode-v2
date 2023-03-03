from os import getenv

dbConfig = {
    "host": getenv("DB_HOST", "localhost"),
    "port": getenv("DB_PORT", 5432),
    "dbname": getenv("DB_NAME", "ucode"),
    "user": getenv("DB_USER", "postgres"),
    "password": getenv("DB_PASSWORD", "postgres"),
}

appConfig = {"apiKey": getenv("API_KEY", "XXX_API_KEY_XXX")}
