import requests
from typing import List
from datetime import datetime
import re


def name_list_parser(name_lst: str):
    name_lst = re.sub('\[.*?\]', '', name_lst)
    name_lst = [n.strip() for n in name_lst.split(',')]
    rslt = []
    for name in name_lst:
        name_dct = {}
        m = re.findall('\<.*?\>', name)
        if m and '@' in m[0]:
            name_dct['Email'] = m[0][1:-1]
        name_dct['Name'] = re.sub('\<.*?\>', '', name).strip()
        rslt.append(name_dct)
    return rslt


class Fields:
    String = lambda x: x
    NameList = name_list_parser
    Datetime = lambda x: datetime.fromisoformat(x.rsplit(' ', 1)[0].strip()) if x.endswith('UTC') else \
        datetime.fromisoformat(x)


class Parser:
    def parse_txt(self, txt: str, fields: dict) -> dict:
        lst = []
        for l in txt.split('\n'):
            if ':' in l:
                lst.append([x.strip() for x in l.split(':', 1)])
            else:
                lst[-1][1] += ' ' + l.strip()

        pkg_dct = {}
        for entity, val in lst:
            val = val.strip()
            if entity in fields:
                pkg_dct[entity] = fields[entity](val)
        return pkg_dct


class DescriptionParser(Parser):
    _field = {'Package': Fields.String,
              'Version': Fields.String,
              'Date/Publication': Fields.Datetime,
              'Title': Fields.String,
              'Description': Fields.String,
              'Author': Fields.NameList,
              'Maintainer': Fields.NameList}

    def __init__(self):
        super(DescriptionParser, self).__init__()

    def parse(self, txt):
        return self.parse_txt(txt, self._field)


class PackageParser(Parser):
    _field = {'Package': Fields.String,
              'Version': Fields.String}

    _url = 'https://cran.r-project.org/src/contrib/PACKAGES'

    def __init__(self):
        super(PackageParser, self).__init__()

    def parse(self, txt):
        return self.parse_txt(txt, self._field)

    def parse_from_url(self):
        r = requests.get(self._url)
        # around 3mb
        pkgs_txt = r.text.split('\n\n')
        return [self.parse_txt(pkg_txt, self._field) for pkg_txt in pkgs_txt]


if __name__ == "__main__":
    # pp = PackageParser()
    # t = pp.parse_from_url()
    # print(t)

    # r = requests.get('https://cran.r-project.org/src/contrib/')
    # print(r.text)

    # pkgs = [x for x in pd.read_html('https://cran.r-project.org/src/contrib/')[0]['Name'].to_list() if
    #         isinstance(x, str) and x.endswith('.tar.gz')]
    # print(pkgs[:100])
    # print(len(pkgs))

    a = "asdfasdf <asdfa@gags>, asdfs asdfasd <asdfsf>, aa"
    r = name_list_parser(a)
    print(r)
