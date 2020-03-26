import connexion
from connexion.resolver import Resolver
import doc_converter.common.util
from doc_converter.common.util import dictConfig
import doc_converter.spooler 
import doc_converter.views
from doc_converter.views import view_resolver
from wsgi_microservice_middleware import RequestIdMiddleware

app = connexion.FlaskApp('doc_converter')
app.add_api('openapi.yaml', resolver=Resolver(function_resolver=view_resolver))
app.app.logger.info('Application configured.  Ready to run.')
app.app.wsgi_app = RequestIdMiddleware(app.app.wsgi_app)

if __name__ == '__main__':
    app.run(port=8080, debug=True, use_reloader=False, threaded=False)