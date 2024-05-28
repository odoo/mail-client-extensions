from odoo.upgrade import util


def migrate(cr, version):
    util.remove_group(cr, "l10n_be_codabox.group_access_connection_settings")
    util.remove_view(cr, "l10n_be_codabox.soda_import_wizard_view_form_codabox")
    util.remove_record(cr, "l10n_be_codabox.action_open_accounting_settings")
