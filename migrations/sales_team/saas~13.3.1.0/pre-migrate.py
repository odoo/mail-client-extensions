# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.move_model(cr, "crm.lead.tag", "crm", "sales_team", move_data=True)
    util.rename_model(cr, "crm.lead.tag", "crm.tag")
