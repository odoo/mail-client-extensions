# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # forbid the creation of `name_code_uniq` constraint on `res.country.state` to ensure
    # csv file will be imported.
    # The constraint will be created after cleaning in post script.
    cc = util.ref(cr, 'base.cc')
    if not cc:
        # Why do people remove countries?
        cr.execute("SELECT min(id) FROM res_country")
        [cc] = cr.fetchone() or [None]

    cr.execute("""
        INSERT INTO res_country_state(country_id, code, name)
             VALUES (%(country)s, 'CC', 'CC'),
                    (%(country)s, 'CC', 'CC')
          RETURNING id
    """, dict(country=cc))
    util.ENVIRON['cc_states'] = [s[0] for s in cr.fetchall()]
