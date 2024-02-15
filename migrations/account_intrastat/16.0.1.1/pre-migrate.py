from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_intrastat.search_template_vat")
    util.remove_view(cr, "account_intrastat.search_template_intrastat_extended")
    util.remove_view(cr, "account_intrastat.search_template_intrastat_type")
