from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "ir_attachment", "res_field", "varchar")
