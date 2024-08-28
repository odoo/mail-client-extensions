from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "appointment_crm.appointment_crm_tag")
