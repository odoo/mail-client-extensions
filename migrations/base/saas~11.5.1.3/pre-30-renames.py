# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("base.module_category_{website_,}sign"))

    cr.execute("UPDATE report_paperformat SET name='A4' WHERE id=%s", [util.ref(cr, "base.paperformat_euro")])

    # TODO rename demo data
