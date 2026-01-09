import os
import sys
import json
import threading
from logging import Logger

import waitress
from flask import Flask, Response, jsonify, make_response, render_template, request

from icloudpd.status import Status, StatusExchange


def serve_app(logger: Logger, _status_exchange: StatusExchange) -> None:
    app = Flask(__name__)
    app.logger = logger
    # for running in pyinstaller
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir is not None:
        app.template_folder = os.path.join(bundle_dir, "templates")
        app.static_folder = os.path.join(bundle_dir, "static")

    @app.route("/")
    def index() -> Response | str:
        return render_template("index.html")

    @app.route("/status", methods=["GET"])
    def get_status() -> Response | str:
        _status = _status_exchange.get_status()
        _global_config = _status_exchange.get_global_config()
        _user_configs = _status_exchange.get_user_configs()
        _current_user = _status_exchange.get_current_user()
        _progress = _status_exchange.get_progress()
        _error = _status_exchange.get_error()

        if _status == Status.NO_INPUT_NEEDED:
            return render_template(
                "no_input.html",
                status=_status,
                error=_error,
                progress=_progress,
                global_config=vars(_global_config) if _global_config else None,
                user_configs=[vars(uc) for uc in _user_configs] if _user_configs else [],
                current_user=_current_user,
            )
        if _status == Status.NEED_MFA:
            return render_template("code.html", error=_error, current_user=_current_user)
        if _status == Status.NEED_PASSWORD:
            return render_template("password.html", error=_error, current_user=_current_user)
        return render_template("status.html", status=_status)

    @app.route("/code", methods=["POST"])
    def set_code() -> Response | str:
        _current_user = _status_exchange.get_current_user()
        code = request.form.get("code")
        if code is not None:
            if _status_exchange.set_payload(code):
                return render_template("code_submitted.html", current_user=_current_user)
        else:
            logger.error(f"cannot find code in request {request.form}")
        return make_response(
            render_template(
                "auth_error.html",
                type="Two-Factor Code",
                current_user=_current_user,
            ),
            400,
        )  # incorrect code

    @app.route("/password", methods=["POST"])
    def set_password() -> Response | str:
        _current_user = _status_exchange.get_current_user()
        password = request.form.get("password")
        if password is not None:
            if _status_exchange.set_payload(password):
                return render_template("password_submitted.html", current_user=_current_user)
        else:
            logger.error(f"cannot find password in request {request.form}")
        return make_response(
            render_template("auth_error.html", type="password", current_user=_current_user),
            400,
        )  # incorrect code

    @app.route("/resume", methods=["POST"])
    def resume() -> Response | str:
        _status_exchange.get_progress().resume = True
        return make_response("Ok", 200)

    @app.route("/cancel", methods=["POST"])
    def cancel() -> Response | str:
        _status_exchange.get_progress().cancel = True
        return make_response("Ok", 200)

    @app.route("/browser")
    def browser() -> Response | str:
        """Folder browser UI page"""
        return render_template("browser.html")

    @app.route("/api/folders", methods=["GET"])
    def list_folders() -> Response:
        """API endpoint to list available folders"""
        try:
            icloud_service = _status_exchange.get_icloud_service()
            if not icloud_service:
                return jsonify({"error": "Not authenticated"}), 401

            library_name = request.args.get("library", "PrimarySync")
            if library_name in icloud_service.photos.private_libraries:
                library = icloud_service.photos.private_libraries[library_name]
            elif library_name in icloud_service.photos.shared_libraries:
                library = icloud_service.photos.shared_libraries[library_name]
            else:
                library = icloud_service.photos

            folders = library.folders
            folder_list = [{"name": name, "count": len(album)} for name, album in folders.items()]
            return jsonify({"folders": folder_list})
        except Exception as e:
            logger.error(f"Error listing folders: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/albums", methods=["GET"])
    def list_albums() -> Response:
        """API endpoint to list available albums"""
        try:
            icloud_service = _status_exchange.get_icloud_service()
            if not icloud_service:
                return jsonify({"error": "Not authenticated"}), 401

            library_name = request.args.get("library", "PrimarySync")
            if library_name in icloud_service.photos.private_libraries:
                library = icloud_service.photos.private_libraries[library_name]
            elif library_name in icloud_service.photos.shared_libraries:
                library = icloud_service.photos.shared_libraries[library_name]
            else:
                library = icloud_service.photos

            albums = library.albums
            album_list = [{"name": name, "count": len(album)} for name, album in albums.items()]
            return jsonify({"albums": album_list})
        except Exception as e:
            logger.error(f"Error listing albums: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/libraries", methods=["GET"])
    def list_libraries() -> Response:
        """API endpoint to list available libraries"""
        try:
            icloud_service = _status_exchange.get_icloud_service()
            if not icloud_service:
                return jsonify({"error": "Not authenticated"}), 401

            private_libs = list(icloud_service.photos.private_libraries.keys())
            shared_libs = list(icloud_service.photos.shared_libraries.keys())
            return jsonify({"private": private_libs, "shared": shared_libs})
        except Exception as e:
            logger.error(f"Error listing libraries: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/download", methods=["POST"])
    def start_download() -> Response:
        """API endpoint to start a download"""
        try:
            data = request.get_json()
            folders = data.get("folders", [])
            albums = data.get("albums", [])
            directory = data.get("directory")
            library = data.get("library", "PrimarySync")

            if not directory:
                return jsonify({"error": "Directory is required"}), 400

            if not folders and not albums:
                return jsonify({"error": "At least one folder or album must be selected"}), 400

            # Store download request in status exchange
            # The download will be initiated by the main process
            _status_exchange.set_download_request({
                "folders": folders,
                "albums": albums,
                "directory": directory,
                "library": library
            })

            # Trigger resume if in watch mode to process the request
            _status_exchange.get_progress().resume = True

            return jsonify({"status": "Download started"})
        except Exception as e:
            logger.error(f"Error starting download: {e}")
            return jsonify({"error": str(e)}), 500

    logger.debug("Starting web server...")
    return waitress.serve(app)
