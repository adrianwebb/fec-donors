from systems.plugins.index import ProviderMixin

import re


class FECSourceMixin(ProviderMixin('fec_source')):

    def _format_name(self, name):
        return re.sub(r'\s+', '-', re.sub('-', ' ', name.strip()).title())


    def _find_most_recent_year(self, years, year):
        info = {
            'index': 0,
            'year': years[0]
        }
        for index, year_item in enumerate(years):
            if year_item <= year:
                info['index'] = index
                info['year'] = year_item
            else:
                break
        return info
