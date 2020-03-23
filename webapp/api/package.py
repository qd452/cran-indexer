from flask_restplus import Resource, fields, reqparse, Namespace
from webapp.task import sync_package

package_ns = Namespace('pacakge', description='cran pacakge operations')

package = package_ns.model(
    'Package', {
        'name': fields.String(required=True),
        'version': fields.String(required=True),
        'data_publication': fields.DateTime,
        'title': fields.String(required=False),
        'description': fields.String(required=False),
        'authors': fields.List(fields.String),
        'maintainers': fields.List(fields.String)
    })

package_post_parser = reqparse.RequestParser(bundle_errors=True)
package_post_parser.add_argument('name', type=str, required=True,
                                 help='name of the package')
package_post_parser.add_argument('version', type=str, required=True,
                                 help='name of the package')


# @package_ns.route('/')
class PackageList(Resource):
    '''Shows a list of packages, and lets you POST to add new pacakge'''

    @package_ns.doc('list_package')
    @package_ns.marshal_list_with(package)
    def get(self):
        '''List all users'''
        pass

    @package_ns.doc('add package')
    @package_ns.expect(package)
    @package_ns.marshal_with(package_post_parser, code=201)
    def post(self):
        '''Create a new User'''
        args = package_post_parser.parse_args()
        pass


@package_ns.route('/sync')
class SyncRemote(Resource):
    def get(self):
        sync_package.apply_async()
        return 'Success - Syncing', 200
