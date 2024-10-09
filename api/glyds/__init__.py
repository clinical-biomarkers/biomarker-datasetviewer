import os
import logging 
from flask import Flask, Blueprint, request
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from flask_restx import Api, Resource, fields
from flask_restx.apidoc import apidoc

from .dataset import api as dataset_api





def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.url_map.strict_slashes = False

    #CORS(app, supports_credentials=True)
    CORS(app)

    # logging.basicConfig(level = logging.DEBUG)
    # app.logger.debug(f'STATIC FOLDER: {app.static_folder}')
    # app.logger.debug(f'STATIC URL PATH: {app.static_url_path}')
    # app.logger.debug(f'APIDOC STATIC URL PATH: {apidoc._static_url_path}')
    # app.logger.debug(f'APIDOC STATIC FOLDER: {apidoc.static_folder}')
    api = Api(app, version='1.0', title='GlyGen Dataset APIs', description='Documentation for the GlyGen Dataset APIs')
    api.add_namespace(dataset_api)
    # apidoc.static_url_path = '/biomarker-partnership/api'

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if app.config["ENV"] == "production":
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_pyfile('config.dev.py', silent=True)

    jwt = JWTManager(app)

    app.config['MONGODB_CONNSTRING'] = os.getenv('MONGODB_CONNSTRING', default=None)


    from . import db

    from . import misc
    app.register_blueprint(misc.bp)

    from . import gsd
    app.register_blueprint(gsd.bp)

    # @app.before_request
    # def log_request_info():
    #     app.logger.debug('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    #     app.logger.debug('HEADERS: %s', request.headers)
    #     app.logger.debug('BODY: %s', request.get_data())
    #     app.logger.debug('REQUEST PATH: %s', request.path)
    #     app.logger.debug('FULL PATH: %s', request.url)
    
    # @app.after_request
    # def log_response_info(response):
    #     app.logger.debug('-----------------------------------------------------------------------------------------')
    #     app.logger.debug('STATUS %s', response.status)
    #     app.logger.debug('HEADERS %s', response.headers)
    #     return response 

    app.add_url_rule('/', endpoint='index')



    return app
