class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = (
        "mysql+mysqlconnector://root:rootpoot666@localhost/mechanic_shop"
    )
    DEBUG = True


class TestingConfig:
    pass


class ProductionConfig:
    pass
