from systems.plugins.index import BaseProvider
from utility.data import ensure_list

import psycopg2
import psycopg2.extras


class Provider(BaseProvider('source', 'committee_db')):

    def update(self):
        try:
            config_facade = self.facade_index['config']

            host = config_facade.retrieve(self.field_host)
            if host:
                host = host.value
            else:
                self.command.error("Host configuration {} required when using source plugin committee db".format(self.field_host))

            user = config_facade.retrieve(self.field_user)
            if user:
                user = user.value
            else:
                self.command.error("User configuration {} required when using source plugin committee db".format(self.field_user))

            password = config_facade.retrieve(self.field_password)
            if password:
                password = password.value
            else:
                self.command.error("Password configuration {} required when using source plugin committee db".format(self.field_password))

            database = config_facade.retrieve(self.field_database)
            if database:
                database = database.value
            else:
                self.command.error("Database configuration {} required when using source plugin committee db".format(self.field_database))

            connection = psycopg2.connect(
                host = host,
                user = user,
                password = password,
                database = database
            )
            self.cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
            super().update()

        finally:
            if connection:
                self.cursor.close()
                connection.close()


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
            'party_name',
            'candidate_ids'
        ]

    def load_contexts(self):
        candidates = list(self.facade_index['candidate'].field_values('candidate_id'))
        contexts = []
        for year in ensure_list(self.field_years):
            for candidate_id in candidates:
                contexts.append({
                    'year': year,
                    'candidate_id': candidate_id
                })
        return contexts

    def load_items(self, context):
        query = "select cycles, committee_id, name, committee_type_full, designation_full, filing_frequency, state, party, party_full, candidate_ids from disclosure.ofec_committee_history"
                " where candidate_ids @> ARRAY['%s']"
                " and cycles_has_activity @> ARRAY[%s]"

        args = [context['candidate_id'], context['year']]

        if self.field_type_codes:
            type_codes = ensure_list(self.field_type_codes, True)
            query += " and committee_type IN ({})".format(
                ",".join('%s' * len(type_codes))
            )
            args.extend(type_codes)

        if self.field_party_codes:
            party_codes = ensure_list(self.field_party_codes, True)
            query += " and party IN ({})".format(
                ",".join('%s' * len(party_codes))
            )
            args.extend(party_codes)

        self.cursor.execute(query, args)
        return self.cursor.fetchall()

    def load_item(self, committee, context):
        cycle_info = self._find_most_recent_year(committee['cycles'], context['year'])
        return [
            cycle_info['year'],
            committee['committee_id'],
            committee['name'].strip().title(),
            committee['committee_type_full'].title() if committee['committee_type_full'] else None,
            committee['designation_full'].title() if committee['designation_full'] else None,
            committee['filing_frequency'],
            committee['state'],
            committee['party'],
            committee['party_full'].title() if committee['party_full'] else None,
            ",".join(committee['candidate_ids'])
        ]
