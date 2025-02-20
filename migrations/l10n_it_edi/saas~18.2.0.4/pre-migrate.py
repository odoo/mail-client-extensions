from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "l10n_it_edi.address", "l10n_it_edi.address_form_fields")
