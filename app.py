import os
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

    from blueprints.convert import bp as convert_bp
    app.register_blueprint(convert_bp, url_prefix="/convert")

    from blueprints.merge import bp as merge_bp
    app.register_blueprint(merge_bp, url_prefix="/merge")

    from blueprints.remove import bp as remove_bp
    app.register_blueprint(remove_bp, url_prefix="/remove")
    @app.route("/")
    def home():
        return render_template("home.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8000, debug=True)
