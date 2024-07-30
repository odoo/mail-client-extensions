from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("industry_fsm_sale{_report,}.worksheet_custom_page"))
