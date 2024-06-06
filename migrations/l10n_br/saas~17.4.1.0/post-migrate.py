from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "base.br", from_module="l10n_br")
