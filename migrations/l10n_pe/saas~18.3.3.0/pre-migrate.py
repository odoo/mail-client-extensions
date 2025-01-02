from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_pe.partner_info")
    util.remove_view(cr, "l10n_pe.partner_address_info")
    util.rename_xmlid(cr, "l10n_pe.address", "l10n_pe.address_form_fields")
