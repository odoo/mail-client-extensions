from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "marketing_automation.mailing_mailing_view_form_marketing_activity")
