from systems.plugins.index import BaseProvider
from utility.fec_api import OpenFECAPI


class Provider(BaseProvider('source', 'committee')):

    def item_columns(self):
        return [
            'year',
            'committee_id',
            'name',
            'type',
            'designation',
            'filing_frequency',
            'state_id',
            'party_id',
            'candidate_ids'
        ]

    def load_items(self, context):
        return OpenFECCommittees(
            self.command,
            self.field_year,
            self.page_count
        ).fetch()

    def load_item(self, committee, context):
        cycle_info = self._find_most_recent_year(committee.cycles, self.field_year)
        return [
            cycle_info['year'],
            committee.committee_id,
            committee.name.strip().title(),
            committee.committee_type if committee.committee_type else None,
            committee.designation if committee.designation else None,
            committee.filing_frequency,
            committee.state,
            committee.party,
            ",".join(committee.candidate_ids)
        ]


class OpenFECCommittees(OpenFECAPI):

    @property
    def state_id(self):
        return "committee-index-{}".format(self.year)


    def fetch(self):
        endpoint = 'committees'
        options = {}
        next_page = None

        page = self.command.get_state(self.state_id, None)
        if page:
            options['page'] = page

        options['year'] = [ self.year ]
        options['sort'] = 'name'
        initial_results = self.request(endpoint, options)

        if initial_results.get('results', None) and len(initial_results['results']) > 0:
            for result in initial_results['results']:
                yield type('Committee', (object,), result)

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
                        yield type('Committee', (object,), result)

                next_page += 1
                self.command.set_state(self.state_id, next_page)

        self.command.delete_state(self.state_id)
