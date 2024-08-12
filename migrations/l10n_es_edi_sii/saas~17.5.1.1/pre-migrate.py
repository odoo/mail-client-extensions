from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_model(cr, *eb("l10n_es_edi{,_sii}.certificate"))

    util.rename_field(cr, "res.company", *eb("l10n_es_{edi,sii}_certificate_id"))
    util.rename_field(cr, "res.company", *eb("l10n_es_{edi,sii}_certificate_ids"))
    util.rename_field(cr, "res.company", *eb("l10n_es_{edi,sii}_tax_agency"))
    util.rename_field(cr, "res.company", *eb("l10n_es_{edi,sii}_test_env"))

    util.rename_field(cr, "res.config.settings", *eb("l10n_es_{edi,sii}_certificate_ids"))
    util.rename_field(cr, "res.config.settings", *eb("l10n_es_{edi,sii}_tax_agency"))
    util.rename_field(cr, "res.config.settings", *eb("l10n_es_{edi,sii}_test_env"))

    util.rename_xmlid(cr, *eb("l10n_es_edi_sii.access_l10n_es_edi{,_sii}_certificate"))
    util.rename_xmlid(cr, *eb("l10n_es_edi_sii.l10n_{ec,es_sii}_digital_certificate"))
    util.rename_xmlid(cr, *eb("l10n_es_edi_sii.l10n_es_edi{,_sii}_certificate_form"))
    util.rename_xmlid(cr, *eb("l10n_es_edi_sii.l10n_es_edi{,_sii}_certificate_tree"))
    util.rename_xmlid(cr, *eb("l10n_es_edi_sii.l10n_es_edi{,_sii}_certificate_action"))
    util.rename_xmlid(cr, *eb("l10n_es_edi_sii.menu_l10n_es_edi{,_sii}_root"))
    util.rename_xmlid(cr, *eb("l10n_es_edi_sii.menu_l10n_es_edi{,_sii}_certificates"))
