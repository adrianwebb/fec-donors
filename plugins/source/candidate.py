from systems.plugins.index import BaseProvider
from utility.fec_api import OpenFECAPI


class Provider(BaseProvider('source', 'candidate')):

    def item_columns(self):
        return [
            'year',
            'office_id',
            'party_id',
            'state_id',
            'district_id',
            'district_number',
            'candidate_id',
            'first_name',
            'last_name',
            'candidacy_id'
        ]

    def load_items(self, context):
        return OpenFECCandidates(
            self.command,
            self.field_year,
            self.page_count
        ).fetch()

    def load_item(self, candidate, context):
        name_components = self._normalize_name_components(candidate.name)
        if name_components and len(name_components) >= 2:
            election_info = self._find_most_recent_year(candidate.election_years, self.field_year)
            district_number = candidate.election_districts[election_info['index']]

            return [
                election_info['year'],
                candidate.office,
                candidate.party,
                candidate.state,
                self._get_district_id(candidate.state, district_number),
                district_number,
                candidate.candidate_id,
                self._format_name(name_components[1].split()[0]),
                self._format_name(name_components[0]),
                self._get_candidacy_id(
                    candidate.candidate_id,
                    candidate.state,
                    district_number,
                    candidate.office,
                    election_info['year']
                )
            ]
        return None


class OpenFECCandidates(OpenFECAPI):

    @property
    def state_id(self):
        return "candidate-index-{}".format(self.year)


    def fetch(self):
        endpoint = 'candidates'
        options = {}
        next_page = None

        page = self.command.get_state(self.state_id, None)
        if page:
            options['page'] = page

        options['cycle'] = [ self.year ]
        options['sort'] = 'name'
        initial_results = self.request(endpoint, options)

        if initial_results.get('results', None) and len(initial_results['results']) > 0:
            for result in initial_results['results']:
                yield type('Candidate', (object,), result)

        if initial_results.get('pagination', None):
            if initial_results['pagination'].get('pages', None):
                if initial_results['pagination']['pages'] > 1:
                    next_page = page + 1 if page else 2
                    self.command.set_state(self.state_id, next_page)

        if next_page:
            while next_page <= initial_results['pagination']['pages']:
                params = dict(options)
                params['page'] = next_page
                paged_results = self.request(endpoint, params)

                if paged_results.get('results', None) and len(paged_results['results']) > 0:
                    for result in paged_results['results']:
                        yield type('Candidate', (object,), result)

                next_page += 1
                self.command.set_state(self.state_id, next_page)

        self.command.delete_state(self.state_id)
