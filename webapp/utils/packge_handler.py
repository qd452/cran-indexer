import requests
import tarfile
import os
import logging

try:
    from .parser import DescriptionParser
except ImportError:
    from parser import DescriptionParser

BASE_URL = "https://cran.r-project.org/src/contrib/"
logger = logging.getLogger(__name__)


class PacakgeHandlerError(Exception):
    pass


class PackageHandler:
    def __init__(self, pkg_name: str, pkg_version: str):
        self.name = pkg_name
        self.version = pkg_version
        self.url = f'{BASE_URL}{self.name}_{self.version}.tar.gz'
        self.local_fn = f'{self.name}_{self.version}.tar.gz'
        self.full_path = None

    def get_description(self, download_path, remove_local=True):
        self.download(download_path)
        desc_txt = self.extract_desc()
        if remove_local:
            os.remove(self.full_path)
        desc_dct = DescriptionParser().parse(desc_txt)
        desc_dct['TAR_URL'] = self.url  # also save the url

        # In case of the DESCRIPTION FILE missing the package name and version
        # just update those fields by using the information from PACKAGE
        if desc_dct.get('Package', None) is None:
            logger.warning(f'{self.name} has no Package name in DESCRIPTION')
            desc_dct['Package'] = self.name
        if desc_dct.get('Version', None) is None:
            logger.warning(f'{self.version} has no Package version in DESCRIPTION')
            desc_dct['Version'] = self.version
        return desc_dct

    def download(self, download_path, chunk_size=16 * 1024):
        '''

        :param download_path: local download path
        :param chunk_size: keep memory usage to 16kb
        :return:
        '''
        self.full_path = os.path.join(download_path, self.local_fn)
        with requests.get(self.url) as r:
            if r.status_code != 200:
                raise PacakgeHandlerError(f'Unable to download {self.name}_{self.version} from {self.url}')
            with open(self.full_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)

    def extract_desc(self):
        if not self.full_path:
            raise PacakgeHandlerError("Package doesn't exist in local")
        content = ""
        with tarfile.open(self.full_path, "r:gz") as tar:
            for member in tar.getmembers():
                sp = member.name.split('/')
                # in case of some of the files has multiple DESCRIPTION FILES
                if len(sp) == 2 and sp[-1] == 'DESCRIPTION':
                    f = tar.extractfile(member)
                    if f is not None:
                        content = f.read()
        try:
            content_str = content.decode(encoding='utf-8')
        except:
            content_str = content.decode(encoding="ISO-8859-1")
        return content_str


if __name__ == "__main__":
    p = os.path.abspath(os.path.dirname(__file__) + "/output")
    pkg = PackageHandler('MBHdesign', '2.1.6')
    pkg = PackageHandler('AnimalHabitatNetwork', '0.1.0')
    'webapp/utils/output/Rd2roxygen_1.9.tar.gz'
    pkg = PackageHandler('Rd2roxygen', '1.9')
    # pkg.download(p)
    c = pkg.get_description(p, remove_local=False)
    from pprint import pprint
    pprint(c)
