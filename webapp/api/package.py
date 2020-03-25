from flask_restplus import Resource, fields, reqparse, Namespace
from flask import current_app
from webapp.task import sync_package, process_package, is_package_processed_strict
from webapp import mongo, cache
from webapp.utils.packge_handler import PackageHandler, PacakgeHandlerError
import bson
import json

package_ns = Namespace('package', description='cran package operations')

package = package_ns.model(
    'Package', {
        'Package': fields.String(required=True),
        'Version': fields.String(required=True),
        'Date/Publication': fields.DateTime,
        'Title': fields.String(required=False),
        'Description': fields.String(required=False),
        'Author': fields.List(fields.Raw),
        'Maintainer': fields.List(fields.Raw)
    })

package_list_get_parser = reqparse.RequestParser(bundle_errors=True)
package_list_get_parser.add_argument('package', type=str, required=True,
                                     help='query condition for getting pacakges')

package_post_parser = reqparse.RequestParser(bundle_errors=True)
package_post_parser.add_argument('name', type=str, required=True,
                                 help='name of the package')
package_post_parser.add_argument('version', type=str, required=True,
                                 help='version of the package')


@package_ns.route('/')
class PackageList(Resource):
    '''Shows a list of packages, and lets you POST to add new package'''

    @package_ns.doc('list_package')
    @package_ns.expect(package_list_get_parser)
    @package_ns.marshal_list_with(package, code=200)
    def get(self):
        '''List packages based on requirement'''
        pkg_contains = package_list_get_parser.parse_args()['package']
        regex = bson.regex.Regex(f".*{pkg_contains}.*")
        cursor = mongo.db.package.find({"Package": regex})
        # explain_str = json.dumps(cursor.explain(), indent=4)
        # ixscan = 'IXSCAN' in explain_str
        # if not ixscan:
        #     raise Exception(f'Not using IXSCAN:\n{explain_str}')
        pkg_lst = []
        for c in cursor:
            pkg_lst.append(c)
        return pkg_lst

    @package_ns.doc('add package')
    @package_ns.expect(package_post_parser)
    @package_ns.marshal_with(package, code=201)
    def post(self):
        '''Add new package synchronously'''
        args = package_post_parser.parse_args()
        pkg_name, pkg_version = args['name'], args['version']
        if is_package_processed_strict(pkg_name, pkg_version):
            pkg = mongo.db.package.find_one(
                {"Package": pkg_name, "Version": pkg_version})
            return pkg, 201
        try:
            pkg_handler = PackageHandler(pkg_name, pkg_version)
            app = current_app._get_current_object()
            desc = pkg_handler.get_description(app.config['TMP_DIR'])
            pkg_id = mongo.db.package.insert_one(desc).inserted_id
            pkg_ver = pkg_name + '_' + pkg_version
            cache.sadd('processed', pkg_ver)
        except PacakgeHandlerError as e:
            package_ns.abort(400, f'Bad Request: {e}')
        except Exception as e:
            package_ns.abort(500, f'Internal server error')
        return desc, 201


@package_ns.route('/<string:package_name>')
@package_ns.response(404, 'Package not found')
class Package(Resource):
    '''Show list of package by give package name and allows you to delete them'''

    @package_ns.doc('get package')
    @package_ns.marshal_list_with(package)
    def get(self, package_name):
        '''Fetch a given resource'''
        cursor = mongo.db.package.find({"Package": package_name})
        pkg_lst = []
        for c in cursor:
            pkg_lst.append(c)
        return pkg_lst

    @package_ns.doc('delete package')
    @package_ns.response(204, 'Package deleted')
    def delete(self, package_name):
        '''Delete packages given its package name'''
        cursor = mongo.db.package.find({"Package": package_name})
        pkg_lst = [c for c in cursor]
        pkg_ver = [p['Package'] + '_' + p['Version'] for p in pkg_lst]
        cache.srem('processed', *pkg_ver)
        mongo.db.package.delete_many({"Package": package_name})
        return '', 204


@package_ns.route('/sync')
class SyncRemote(Resource):
    def get(self):
        sync_package.apply_async()
        return 'Success - Syncing', 200
