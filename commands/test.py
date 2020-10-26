from systems.commands.index import Command

from pyopenfec import Candidate, Committee
from django.core.serializers.json import DjangoJSONEncoder

import json


class Test(Command('test')):

    def exec(self):
        year = 2018

        # results = Candidate.fetch(
        #     cycle = [ year ],
        #     name = [ 'Bernard Sanders' ],
        #     per_page = 100
        # )
        results = Committee.fetch(
            candidate_id = [ 'S4VT00033' ],
            year = [ year ],
            per_page = 100
        )
        for result in results:
            self.data('result {}'.format(year), json.dumps(result.__dict__, indent = 2, cls = DjangoJSONEncoder))
