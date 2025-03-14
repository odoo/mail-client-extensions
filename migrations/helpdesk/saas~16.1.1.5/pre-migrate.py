from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "helpdesk.helpdesk_stage_company_rule")
