import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        QDRANT_HOST=os.getenv('QDRANT_HOST'),
        QDRANT_PORT=int(os.getenv('QDRANT_PORT')),
        OPENAI_API_KEY=os.getenv('OPENAI_API_KEY'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register API blueprints and initialize services
    from . import answer
    answer.init_app(app)
    app.register_blueprint(answer.bp)

    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'VanTrails API'}

    return app