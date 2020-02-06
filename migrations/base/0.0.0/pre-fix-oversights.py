# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("10.saas~18"):
        # Should have been removed in saas~18...
        cr.execute("ALTER TABLE res_partner_title DROP CONSTRAINT IF EXISTS res_partner_title_name_uniq")
        cr.execute("DELETE FROM ir_model_constraint WHERE name='res_partner_title_name_uniq'")
