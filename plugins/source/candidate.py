from pyopenfec import Candidate

from systems.plugins.index import BaseProvider

import pandas
import re


class Provider(BaseProvider('source', 'candidate')):

    def load(self):
        data = []
        candidates = Candidate.fetch(
            year = self.field_year,
            name = self.field_candidates,
            office = self.field_office_code,
            party = [ self.field_party_code ],
            per_page = 100
        )
        for candidate in candidates:
            name_components = self._normalize_name_components(candidate.name)
            if name_components and len(name_components) >= 2:
                data.append([
                    candidate.candidate_id,
                    self._format_name(name_components[1].split()[0]),
                    self._format_name(name_components[0]),
                    candidate.office_full,
                    candidate.state,
                    candidate.district_number,
                    candidate.party_full
                ])

        return pandas.DataFrame(data, columns = [
            'candidate_id',
            'first_name',
            'last_name',
            'office',
            'state',
            'district',
            'party'
        ])


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

    def _format_name(self, name):
        return re.sub(r'\s+', '-', re.sub('-', ' ', name.strip()).title())
