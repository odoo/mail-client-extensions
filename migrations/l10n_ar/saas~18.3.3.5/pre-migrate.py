from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_ar.partner_info")
    util.rename_xmlid(cr, "l10n_ar.address", "l10n_ar.address_form_fields")
