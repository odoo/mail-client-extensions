from odoo.upgrade import util


def migrate(cr, version):
    script = util.import_script("l10n_in/saas~18.2.2.0/pre-migrate.py")
    script._l10n_in_enable_feature(cr, "l10n_in_edi_feature")
