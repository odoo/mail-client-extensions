from odoo.upgrade import util


def migrate(cr, version):
    # deprecated identification types
    util.delete_unused(cr, "l10n_co.diplomatic_card")
    util.delete_unused(cr, "l10n_co.id_document")
