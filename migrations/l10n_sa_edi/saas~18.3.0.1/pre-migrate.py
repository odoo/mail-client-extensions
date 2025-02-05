from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, "res.partner", *eb("l10n_sa_{,edi_}additional_identification_scheme"))
    util.rename_field(cr, "res.partner", *eb("l10n_sa_{,edi_}additional_identification_number"))
    util.rename_field(cr, "res.company", *eb("l10n_sa_{,edi_}additional_identification_scheme"))
    util.rename_field(cr, "res.company", *eb("l10n_sa_{,edi_}additional_identification_number"))
