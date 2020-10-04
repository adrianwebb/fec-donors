from pyopenfec import ScheduleATransaction

from systems.plugins.index import BaseProvider
from utility.data import ensure_list, get_identifier


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

    def load_contexts(self):
        return self.facade_index['committee'].field_values('committee_id')

    def load_items(self, committee_id):
        return ScheduleATransaction.fetch(
            committee_id = [ committee_id ],
            two_year_transaction_period = ensure_list(self.field_years, True),
            is_individual =  True,
            sort_null_only = True,
            per_page = self.page_count
        )

    def load_item(self, receipt, committee_id):
        transaction_id = receipt.transaction_id if receipt.transaction_id else receipt.sub_id
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
            transaction_id,
            receipt.committee_id,
            receipt.election_type,
            receipt.contribution_receipt_amount,
            receipt.report_year
        ]
