from odoo.upgrade import util

def migrate(cr, version):
    util.remove_field(cr, 'ir.model.data', 'date_init')
    util.remove_field(cr, 'ir.model.data', 'date_update')
