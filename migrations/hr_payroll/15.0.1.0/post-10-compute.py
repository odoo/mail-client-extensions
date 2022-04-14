from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "hr.payslip", ["salary_attachment_ids"])
