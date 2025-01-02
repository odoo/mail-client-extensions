from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_ar_website_sale", "l10n_ar")
    util.merge_module(cr, "l10n_co_edi_website_sale", "l10n_co_edi")
    pv = util.parse_version
    if pv(version) < pv("saas~18.1"):
        util.rename_module(cr, "l10n_ec_website_sale", "l10n_ec_sale")
    else:
        util.force_migration_of_fresh_module(cr, "l10n_ec_sale")
    util.merge_module(cr, "l10n_ec_website_sale", "l10n_ec_sale")
    util.merge_module(cr, "l10n_es_website_sale", "l10n_es")
    util.merge_module(cr, "l10n_it_edi_website_sale", "l10n_it_edi")
    util.merge_module(cr, "l10n_pe_website_sale", "l10n_pe")
