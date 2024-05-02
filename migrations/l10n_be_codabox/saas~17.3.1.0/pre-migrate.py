from odoo.upgrade import util


def migrate(cr, version):
    util.remove_group(cr, "l10n_be_codabox.group_access_connection_settings")
