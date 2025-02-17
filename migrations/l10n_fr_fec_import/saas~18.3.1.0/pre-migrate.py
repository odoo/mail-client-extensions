from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.fec.import.wizard", "attachment_id")
    util.remove_field(cr, "account.fec.import.wizard", "attachment_name")

    util.remove_record(cr, "l10n_fr_fec_import.import_action")
