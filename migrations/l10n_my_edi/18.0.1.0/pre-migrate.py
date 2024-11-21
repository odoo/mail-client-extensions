from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_my_edi.view_invoice_{tree,list}_inherit_l10n_my_myinvois"))
