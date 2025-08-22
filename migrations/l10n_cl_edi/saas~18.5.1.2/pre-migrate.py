from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_model(cr, *eb("l10n_cl.{account.invoice,edi}.reference"))
    util.rename_xmlid(cr, *eb("l10n_cl_edi.access_{account_invoice,cl_edi}_reference"))
    util.rename_xmlid(cr, *eb("l10n_cl_edi.access_{account_invoice,cl_edi}_reference_manager"))
