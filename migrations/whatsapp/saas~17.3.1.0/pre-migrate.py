from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "whatsapp.group_whatsapp_admin", noupdate=False)
    util.remove_record(cr, "whatsapp.module_whatsapp")
