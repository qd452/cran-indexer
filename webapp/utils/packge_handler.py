import requests
import tarfile
import os

try:
    from .parser import DescriptionParser
except ImportError:
    from parser import DescriptionParser

BASE_URL = "https://cran.r-project.org/src/contrib/"


class PacakgeHandlerError(Exception):
    pass


class PackageHandler:
    def __init__(self, pkg_name: str, pkg_version: str):
        self.name = pkg_name
        self.version = pkg_version
        self.url = f'{BASE_URL}{self.name}_{self.version}.tar.gz'
        self.local_fn = f'{self.name}_{self.version}.tar.gz'
        self.full_path = None

    def get_description(self, download_path):
        self.download(download_path)
        desc_txt = self.extract_desc()
        os.remove(self.full_path)
        return DescriptionParser().parse(desc_txt)

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
                if member.name.split('/')[-1] == 'DESCRIPTION':
                    f = tar.extractfile(member)
                    if f is not None:
                        content = f.read()
        return content.decode()


if __name__ == "__main__":
    p = os.path.abspath(os.path.dirname(__file__) + "/output")

    pkg = PackageHandler('MBHdesign', '2.1.6')
    pkg = PackageHandler('AnimalHabitatNetwork', '0.1.0')
    pkg.download(p)
    c = pkg.get_description(p)
    print(c)
