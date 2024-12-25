class Config:
    DEBUG = False
    TESTING = False



class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI ='sqlite:///development.db'  
    SECRET_KEY = "iamsecretkey"
    SECURITY_PASSWORD_SALT = "iamsalt" 
    # SECURITY_PASSWORD_HASH = 'bcrypt' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    SMTP_SERVER = "localhost"
    SMTP_PORT = 1025
    SENDER_EMAIL = "kaushalprajapati@study.iitm.ac.in"
    SENDER_PASSWORD = ""
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = "redis://localhost:6379/0"
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_DEFAULT_TIMEOUT = 30
    CACHE_KEY_PREFIX = "caching"
    broker_connection_retry_on_startup = True
    worker_cancel_long_running_tasks_on_connection_loss = True
    broker_url = 'redis://localhost:6379/0'  
    result_backend = 'redis://localhost:6379/1' 

