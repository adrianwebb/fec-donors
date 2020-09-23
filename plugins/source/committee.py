from pyopenfec import Committee

from systems.plugins.index import BaseProvider

import pandas


class Provider(BaseProvider('source', 'committee')):

    def load(self):
        data = []
        committees = Committee.fetch(
            year = self.field_year,
            q = self.field_committees,
            committee_type = self.field_type_code,
            party = [ self.field_party_code ]
        )
        for committee in committees:
            data.append([
                committee.committee_id,
                committee.name.strip().title(),
                committee.committee_type_full,
                committee.designation_full,
                committee.filing_frequency,
                committee.state,
                committee.party_full,
                ",".join(committee.candidate_ids)
            ])

        return pandas.DataFrame(data, columns = [
            'committee_id',
            'name',
            'type',
            'designation',
            'filing_frequency',
            'state',
            'party',
            'candidate_ids'
        ])
