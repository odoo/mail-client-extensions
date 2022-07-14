# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "account.intrastat.report")
    util.remove_view(cr, "account_intrastat.search_template")
