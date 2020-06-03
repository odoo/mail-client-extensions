# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("SELECT count(id) FROM res_company")
    (company_count,) = cr.fetchone()
    cr.execute("SELECT company_id FROM res_currency GROUP BY company_id")
    if cr.rowcount == 1 or company_count == 1:

        # deduplicate currencies
        cr.execute("SELECT array_agg(id ORDER BY id) FROM res_currency GROUP BY name HAVING count(id) > 1")
        for (dupes,) in cr.fetchall():
            keep = dupes.pop(0)
            idmap = {d: keep for d in dupes}
            util.replace_record_references_batch(cr, idmap, "res.currency")
            for dup in dupes:
                util.remove_record(cr, ("res.currency", dup))

        cr.execute("UPDATE res_currency SET company_id=NULL")
