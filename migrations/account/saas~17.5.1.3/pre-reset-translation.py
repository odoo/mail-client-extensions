from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "account.view_move_form", reset_translations={"arch_db"})
