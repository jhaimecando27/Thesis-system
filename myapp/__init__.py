from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    from . import routes

    app.register_blueprint(routes.bp)
    app.add_url_rule("/", endpoint="index")
    app.add_url_rule("/DataGathering", endpoint="data_gathering")
    app.add_url_rule("/DataSelection", endpoint="data_selection")
    app.add_url_rule("/Map", endpoint="output_map")

    return app
