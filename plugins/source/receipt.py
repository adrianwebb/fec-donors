from systems.plugins.index import BaseProvider
from utility.fec_api import OpenFECAPI
from utility.data import get_identifier


class Provider(BaseProvider('source', 'receipt')):

    def item_columns(self):
        return [
            'contributor_id',
            'first_name',
            'middle_name',
            'last_name',
            'street_1',
            'street_2',
            'city',
            'state_id',
            'zipcode',
            'employer',
            'occupation',
            'transaction_id',
            'committee_id',
            'election_type',
            'amount',
            'year'
        ]

    def load_items(self, context):
        return OpenFECReceipts(
            self.command,
            self.field_year,
            self.page_count
        ).fetch()

    def load_item(self, receipt, context):
        first_name = receipt.contributor_first_name.strip().title() if receipt.contributor_first_name else None
        middle_name = receipt.contributor_middle_name.strip().title() if receipt.contributor_middle_name else None
        last_name = receipt.contributor_last_name.strip().title() if receipt.contributor_last_name else None
        street1 = receipt.contributor_street_1.strip().title() if receipt.contributor_street_1 else None
        street2 = receipt.contributor_street_2.strip().title() if receipt.contributor_street_2 else None
        city = receipt.contributor_city.strip().title() if receipt.contributor_city else None
        state = receipt.contributor_state
        zipcode = receipt.contributor_zip
        employer = receipt.contributor_employer.strip().title() if receipt.contributor_employer else None
        occupation = receipt.contributor_occupation.strip().title() if receipt.contributor_occupation else None
        contributor_id = get_identifier([
            first_name,
            middle_name,
            last_name,
            street1,
            street2,
            city,
            state,
            zipcode
        ])

        return [
            contributor_id,
            first_name,
            middle_name,
            last_name,
            street1,
            street2,
            city,
            state,
            zipcode,
            employer,
            occupation,
            receipt.sub_id,
            receipt.committee_id,
            receipt.election_type,
            receipt.contribution_receipt_amount,
            receipt.report_year
        ]


class OpenFECReceipts(OpenFECAPI):

    @property
    def state_id(self):
        return "receipt-index-{}".format(self.year)


    def fetch(self):
        endpoint = 'schedules/schedule_a'
        options = {}
        last_index = None

        indexes = self.command.get_state(self.state_id, None)
        if indexes:
            options['last_index'] = indexes['last_index']
            options['last_contribution_receipt_date'] = indexes['last_contribution_receipt_date']

        options['is_individual'] = True
        options['two_year_transaction_period'] = [ self.year ]
        options['sort'] = 'contribution_receipt_date'

        initial_results = self.request(endpoint, options)

        if initial_results.get('results', None) and len(initial_results['results']) > 0:
            for result in initial_results['results']:
                yield type('Receipt', (object,), result)

        if initial_results.get('pagination', None):
            if initial_results['pagination'].get('pages', None):
                if initial_results['pagination']['pages'] > 1:
                    indexes = initial_results['pagination']['last_indexes']
                    last_index = int(indexes['last_index'])
                    last_date = indexes['last_contribution_receipt_date']
                    self.command.set_state(self.state_id, indexes)

        if last_index:
            while last_index is not None:
                params = dict(options)
                params['last_index'] = int(last_index)
                params['last_contribution_receipt_date'] = last_date
                indexed_results = self.request(endpoint, params)

                if indexed_results.get('results', None) and len(indexed_results['results']) > 0:
                    for result in indexed_results['results']:
                        yield type('Receipt', (object,), result)

                    indexes = indexed_results['pagination']['last_indexes']
                    last_index = indexes['last_index']
                    last_date = indexes['last_contribution_receipt_date']
                    self.command.set_state(self.state_id, indexes)
                else:
                    last_index = None

        self.command.delete_state(self.state_id)
