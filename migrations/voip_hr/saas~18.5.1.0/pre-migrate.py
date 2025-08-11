from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "voip_hr.voip_call_hr_access_rule")
