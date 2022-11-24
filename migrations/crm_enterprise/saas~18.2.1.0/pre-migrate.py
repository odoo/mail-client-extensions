from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "crm_enterprise.crm_activity_report_view_search")
