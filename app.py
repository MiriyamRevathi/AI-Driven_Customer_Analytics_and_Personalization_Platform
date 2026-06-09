from flask import Flask, jsonify, render_template

from config.settings import Config, ensure_project_directories
from routes.dashboard_routes import dashboard_bp
from routes.export_routes import export_bp
from routes.upload_routes import upload_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    ensure_project_directories()

    app.register_blueprint(upload_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(export_bp)

    @app.route("/")
    def index():
        return render_template("upload.html")

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            {
                "success": False,
                "message": "Resource not found",
                "data": None,
                "errors": [str(error)],
            }
        ), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify(
            {
                "success": False,
                "message": "Internal server error",
                "data": None,
                "errors": [str(error)],
            }
        ), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
