from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "edit.billable.time.target", "job_title")
