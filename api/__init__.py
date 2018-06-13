
from cornice import Service
from cornice.service import get_services
from cornice_swagger.swagger import CorniceSwagger
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from pyramid.paster import get_appsettings
from pyramid.response import Response
from pyramid.view import view_config, notfound_view_config

from prometheus_client import generate_latest


import logging

LOGGER = logging.getLogger(__name__)


# Create a service to serve our OpenAPI spec
swagger = Service(name='OpenAPI',
                  path='/__api__',
                  description="OpenAPI documentation")


@swagger.get()
def openAPI_spec(request):
    my_generator = CorniceSwagger(services=get_services())
    my_generator.summary_docstrings = True
    return my_generator.generate('Catalog Manager', '1.0.0')


@view_config(route_name='home')
def home(request):
    return Response('')


@view_config(route_name='metrics')
def metrics(request):
    return Response(
        body=generate_latest(),
        charset='utf-8',
        content_type='text/plain')


@notfound_view_config()
def notfound(request):
    return HTTPNotFound(body='{"message": "Not found"}')


def includeme(config):
    config.include("cornice")
    config.include('cornice_swagger')
    config.scan("api.views")


def hide(param_name, param_value, name='password'):
    return param_value if name not in param_name else '*'*2*len(param_value)


def main(global_config, **settings):
    config = Configurator(settings=settings)

    LOGGER.info(
        {
            'CatalogManager started': {
                param_name: hide(param_name, param_value)
                for param_name, param_value in settings.items()
                if param_name.startswith('catalogmanager')
            }
        }
    )
    config.include(includeme)

    config.add_route('home', '/')
    config.add_route('metrics', '/metrics')

    def couchdb_settings(request):
        ini_config = request.registry.settings
        return {
            'database_uri': '{}:{}'.format(
                ini_config.get('catalogmanager.db.host', ''),
                ini_config.get('catalogmanager.db.port', '')
            ),
            'database_username': ini_config.get(
                'catalogmanager.db.username',
                ''
            ),
            'database_password': ini_config.get(
                'catalogmanager.db.password',
                ''
            )
        }

    config.add_request_method(couchdb_settings, 'db_settings', reify=True)

    config.scan()
    return config.make_wsgi_app()
