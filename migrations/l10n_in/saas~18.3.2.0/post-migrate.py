from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_in.inter_state_group", force_create=False, fields=["code"])
