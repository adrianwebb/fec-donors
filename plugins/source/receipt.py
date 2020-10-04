from pyopenfec import ScheduleATransaction

from systems.plugins.index import BaseProvider

import pandas


class Provider(BaseProvider('source', 'receipt')):

    page_count = 100
    columns = [
        'transaction_id',
        'report_year',
        'committee_id',
        'candidate_id',
        'election_type',
        'contribution_receipt_amount',
        'contributor_first_name',
        'contributor_middle_name',
        'contributor_last_name',
        'contributor_street_1',
        'contributor_street_2',
        'contributor_city',
        'contributor_state',
        'contributor_zip',
        'contributor_employer',
        'contributor_occupation'
    ]

    def update(self):
        state_facade = self.facade_index['state']
        committee_facade = self.facade_index['committee']
        data = []

        next_committee_id = self.command.get_state('receipt_import_next')
        process = False if next_committee_id else True

        for committee_id in list(committee_facade.field_values('committee_id')):
            if next_committee_id and committee_id == next_committee_id:
                process = True

            if process:
                self.command.set_state('receipt_import_next', committee_id)

                receipts = ScheduleATransaction.fetch(
                    committee_id = [ committee_id ],
                    two_year_transaction_period = self.field_year,
                    is_individual =  True,
                    sort_null_only = True,
                    per_page = self.page_count
                )
                for receipt in receipts:
                    data.append([
                        receipt.transaction_id if receipt.transaction_id else receipt.sub_id,
                        receipt.report_year,
                        receipt.committee_id,
                        receipt.candidate_id,
                        receipt.election_type,
                        receipt.contribution_receipt_amount,
                        receipt.contributor_first_name.strip().title() if receipt.contributor_first_name else None,
                        receipt.contributor_middle_name.strip().title() if receipt.contributor_middle_name else None,
                        receipt.contributor_last_name.strip().title() if receipt.contributor_last_name else None,
                        receipt.contributor_street_1.strip().title() if receipt.contributor_street_1 else None,
                        receipt.contributor_street_2.strip().title() if receipt.contributor_street_2 else None,
                        receipt.contributor_city.strip().title() if receipt.contributor_city else None,
                        receipt.contributor_state,
                        receipt.contributor_zip,
                        receipt.contributor_employer.strip().title() if receipt.contributor_employer else None,
                        receipt.contributor_occupation.strip().title() if receipt.contributor_occupation else None
                    ])
                    if len(data) >= self.page_count:
                        data = self._save(data)

            self._save(data)
            self.command.delete_state('receipt_import_next')


    def _save(self, data):
        if data:
            records = pandas.DataFrame(data, columns = self.columns)
            self.save(self.validate(records))
            data = []
        return data