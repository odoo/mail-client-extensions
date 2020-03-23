# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "crm.reveal.rule", "leads_count", "lead_count")
