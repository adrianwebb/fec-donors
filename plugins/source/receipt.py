from pyopenfec import ScheduleATransaction

from systems.plugins.index import BaseProvider
from django.core.serializers.json import DjangoJSONEncoder

import pandas
import json


class Provider(BaseProvider('source', 'receipt')):

    def load(self):
        committee_facade = self.facade_index['committee']
        committees = {}
        data = []

        for committee_id in list(committee_facade.field_values('committee_id')):
            committees[committee_id] = True

        receipts = ScheduleATransaction.fetch(
            two_year_transaction_period = self.field_year,
            sort_null_only = True,
            is_individual =  True,
            per_page = 100
        )
        index = 0
        for receipt in receipts:
            if receipt.committee_id and receipt.committee_id in committees:
                transaction_id = receipt.transaction_id if receipt.transaction_id else receipt.sub_id
                data.append([
                    transaction_id,
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
                if index >= 3:
                    break
                index = index + 1

        print(data)
        return pandas.DataFrame(data, columns = [
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
        ])
