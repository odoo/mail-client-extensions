# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.version_gte("saas~12.5"):
        # This no longer applies since odoo/odoo@acbca1195a3ad54fe5bc88ceae462993946335a6
        util.ensure_xmlid_match_record(cr, "point_of_sale.pos_sale_journal", "account.journal", {"code": "POSS"})
