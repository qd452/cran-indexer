import requests
from typing import List
from datetime import datetime
import re


def name_list_parser(name_str: str):
    name_str = re.sub('and', ',', name_str)
    name_str = re.sub('\[.*?\]', '', name_str)
    name_lst = [n.strip() for n in name_str.split(',') if n.strip()]
    rslt = []
    for name in name_lst:
        name_dct = {}
        m = re.findall('\<.*?\>', name)
        if m and '@' in m[0]:
            name_dct['Email'] = m[0][1:-1]
        name_dct['Name'] = re.sub('\<.*?\>', '', name).strip()
        name_dct['Name'] = re.sub('\(.*?\)', '', name_dct['Name']).strip()
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
            if ':' in l and l[0] != " ":
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

    def _map_ppl_email(self, desc_dct: dict):
        ppl_email = {}
        for ppl in desc_dct['Author'] + desc_dct['Maintainer']:
            name = ppl['Name']
            first_name = last_name = None
            try:
                first_name, *middle_name, last_name = name.split(' ')
            except:
                pass
            # middle_name = middle_name[0] if middle_name else ''
            email = ppl.get('Email', None)
            if email:
                ppl_email[name] = email
                if first_name and last_name:
                    ppl_email[first_name + ' ' + last_name] = email
        for ppl in desc_dct['Author'] + desc_dct['Maintainer']:
            if ppl['Name'] in ppl_email:
                ppl['Email'] = ppl_email[ppl['Name']]

    def parse(self, txt):
        desc_dct = self.parse_txt(txt, self._field)
        self._map_ppl_email(desc_dct)
        return desc_dct


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
    a = 'Hadley Wickham [aut],\n  Yihui Xie [aut, cre] (<https://orcid.org/0000-0003-0645-5666>)\nMaintainer: Yihui Xie <xie@yihui.name>\n'
    r = name_list_parser(a)
    print(r)
    a = 'a, b and c'
    r = name_list_parser(a)
    print(r)
