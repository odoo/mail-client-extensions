from odoo.upgrade import util


def migrate(cr, version):
    for partner_field in ("mobile", "zip", "street"):
        util.update_field_usage(cr, "project.task", f"partner_{partner_field}", f"partner_id.{partner_field}")
        util.remove_field(cr, "project.task", f"partner_{partner_field}")
