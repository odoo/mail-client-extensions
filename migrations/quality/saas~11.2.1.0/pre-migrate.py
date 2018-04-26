# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for field in 'description action_corrective action_preventive'.split():
        cr.execute("UPDATE quality_alert SET {}={}".format(field, util.pg_text2html(field)))
