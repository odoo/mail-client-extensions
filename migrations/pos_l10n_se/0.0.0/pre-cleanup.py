from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("17.0", "saas~18.1"):
        # gone in stable without any upgrade script: https://github.com/odoo/enterprise/pull/76285
        util.remove_view(cr, "pos_l10n_se.daily_report")
