# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "ir_model", "website_form_key", "varchar")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("website_{crm,form}.contactus_thanks"))
