# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_intrastat.search_template_intrastat")
    util.remove_view(cr, "account_intrastat.account_intrastat_main_template")
    util.remove_view(cr, "account_intrastat.search_template_vat")
    util.remove_view(cr, "account_intrastat.search_template_intrastat_extended")
    util.remove_view(cr, "account_intrastat.search_template_intrastat_type")
