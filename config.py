import os
from configparser import ConfigParser
from pathlib import Path


path = Path(__file__)
dir_path = path.parent.absolute()


class Config(object):
    def __init__(self):
        self.FLASK_ENV = os.environ.get("FLASK_ENV")
        self.auth_user = os.environ.get("auth_user")
        self.auth_key = os.environ.get("auth_key")
        self.FLASK_ENV = 'dev'
        env_config = self.getConfig(self.FLASK_ENV)
        self.APP_ID = env_config.get("APP_ID")
        self.TENANT_ID = env_config.get("TANANET_ID")
        self.BASE_URL = env_config.get("BASE_URL")
        self.GROUP_ID = env_config.get("GROUP_ID")

        self.REPORT_ID_ORDER = env_config.get("REPORT_ID_ORDER")
        self.REPORT_ID_SALESMAN = env_config.get("REPORT_ID_SALESMAN")
        self.CLIENT_ID = env_config.get("CLIENT_ID")
        self.CLIENT_SECRET = env_config.get("CLIENT_SECRET")
        self.AUTHORITY_URL = env_config.get("AUTHORITY_URL")
        self.SCOPE = env_config.get("SCOPE")
        self.USERNAME = env_config.get("USERNAME")
        self.PASSWORD = env_config.get("PASSWORD")
        self.EMBED_TOKEN_ENDPOINT = env_config.get("EMBED_TOKEN_ENDPOINT")

        self.driver = env_config.get("driver")
        self.server_name = env_config.get("server_name")
        self.database_name = env_config.get("database_name")
        self.logid = env_config.get("logid")
        self.logpass = env_config.get("logpass")
        self.TCON = env_config.get("TCON")

        self.SMTP_SERVER = env_config.get("SMTP_SERVER")
        self.SMTP_PORT = env_config.get("SMTP_PORT")
        self.SENDER_EMAIL = env_config.get("SENDER_EMAIL")
        self.SENDER_PASSWORD = env_config.get("SENDER_PASSWORD")

    def getConfig(self, env: str):
        config_parser= ConfigParser()
        config_parser.read(os.path.join(dir_path, f"{env}.ini"))
        return config_parser["config"]
