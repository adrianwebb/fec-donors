from pyopenfec import Candidate

from systems.plugins.index import BaseProvider
from utility.data import ensure_list, get_identifier


class Provider(BaseProvider('source', 'candidate')):

    def item_columns(self):
        return {
            'year': [
                'year'
            ],
            'political_office': [
                'office_id',
                'office_name'
            ],
            'political_party': [
                'party_id',
                'party_name'
            ],
            'us_state': [
                'state_id'
            ],
            'us_district': [
                'district_id',
                'state_id',
                'district_number'
            ],
            'candidate': [
                'candidate_id',
                'first_name',
                'last_name',
                'office_id',
                'party_id'
            ],
            'candidacy': [
                'candidacy_id',
                'candidate_id',
                'district_id',
                'year'
            ]
        }

    def load_contexts(self):
        return ensure_list(self.field_years)

    def load_items(self, year):
        print('fetching candidate')
        candidates = Candidate.fetch(
            cycle = [ year ],
            name = ensure_list(self.field_candidates, True),
            office = ensure_list(self.field_office_codes, True),
            party = ensure_list(self.field_party_codes, True),
            per_page = self.page_count
        )
        print(candidates)
        return candidates

    def load_item(self, candidate, year):
        print(candidate)
        name_components = self._normalize_name_components(candidate.name)
        if name_components and len(name_components) >= 2:
            cycle_info = self._find_most_recent_year(candidate.cycles, year)
            election_info = self._find_most_recent_year(candidate.election_years, year)
            district_number = int(candidate.election_districts[election_info['index']])

            if district_number != 0:
                district_id = "{}{}".format(candidate.state, str(district_number))
            else:
                district_id = candidate.state

            candidacy_id = get_identifier([
                candidate.candidate_id,
                district_id,
                candidate.office_full,
                str(election_info['year'])
            ])
            return {
                'year': [
                    [ cycle_info['year'] ],
                    [ election_info['year'] ]
                ],
                'political_office': [
                    candidate.office,
                    candidate.office_full.title()
                ],
                'political_party': [
                    candidate.party,
                    candidate.party_full.title()
                ],
                'us_state': [
                    candidate.state
                ],
                'us_district': [
                    district_id,
                    candidate.state,
                    district_number
                ],
                'candidate': [
                    candidate.candidate_id,
                    self._format_name(name_components[1].split()[0]),
                    self._format_name(name_components[0]),
                    candidate.office,
                    candidate.party
                ],
                'candidacy': [
                    candidacy_id,
                    candidate.candidate_id,
                    district_id,
                    election_info['year']
                ]
            }
        return None


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
