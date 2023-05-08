from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "voip_crm.action_add_to_call_queue")
