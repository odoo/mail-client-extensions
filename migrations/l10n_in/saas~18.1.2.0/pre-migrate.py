from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, "res.config.settings", *eb("module_l10n_in{_edi,}_ewaybill"))
