from systems.plugins.index import ProviderMixin
from utility.data import get_identifier

import re


class FECImportMixin(ProviderMixin('fec_import')):

    def _get_district_number(self, number):
        try:
            return int(number)
        except Exception:
            return None

    def _get_district_id(self, state, district_number):
        district_number = self._get_district_number(district_number)
        if district_number is not None and district_number != 0:
            return "{}{}".format(state, str(district_number))
        else:
            return state

    def _get_candidacy_id(self, candidate_id, state, district_number, office, year):
        district_number = self._get_district_number(district_number)
        return get_identifier([
            candidate_id,
            state,
            str(district_number) if district_number is not None else '',
            office,
            str(int(year))
        ])


    def _format_name(self, name):
        return re.sub(r'\s+', '-', re.sub('-', ' ', name.strip()).title())

    def _normalize_name_components(self, name):
        name_components = name.split(",")
        final_components = []

        if len(name_components) == 1:
            name_components = name.split()
            name_components = [name_components[-1], name_components[0]]

        for component in name_components:
            if component:
                final_components.append(component)

        return final_components


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
