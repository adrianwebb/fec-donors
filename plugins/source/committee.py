from pyopenfec import Committee

from systems.plugins.index import BaseProvider

import pandas


class Provider(BaseProvider('source', 'committee')):

    page_count = 100
    columns = [
        'committee_id',
        'name',
        'type',
        'designation',
        'filing_frequency',
        'state',
        'party',
        'candidate_ids'
    ]

    def update(self):
        candidate_facade = self.facade_index['candidate']
        data = []

        next_candidate_id = self.command.get_state('committee_import_next')
        process = False if next_candidate_id else True

        for candidate_id in list(candidate_facade.field_values('candidate_id')):
            if next_candidate_id and candidate_id == next_candidate_id:
                process = True

            if process:
                self.command.set_state('committee_import_next', candidate_id)

                committees = Committee.fetch(
                    candidate_id = [ candidate_id ],
                    year = self.field_year,
                    q = self.field_committees,
                    committee_type = self.field_type_code,
                    party = [ self.field_party_code ],
                    per_page = self.page_count
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
                    if len(data) >= self.page_count:
                        data = self._save(data)

            self._save(data)
            self.command.delete_state('committee_import_next')


    def _save(self, data):
        if data:
            records = pandas.DataFrame(data, columns = self.columns)
            self.save(self.validate(records))
            data = []
        return data
