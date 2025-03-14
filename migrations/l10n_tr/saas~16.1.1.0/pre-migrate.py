from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "l10n_tr.chart_template_common", "l10n_tr.l10n_tr_chart_template")
    util.rename_xmlid(cr, "l10n_tr.tr_kdv_satis_sale_18", "l10n_tr.tr_vat_sale_18")
    util.rename_xmlid(cr, "l10n_tr.tr_kdv_satis_purchase_18", "l10n_tr.tr_vat_purchase_18")

    util.delete_unused(cr, "l10n_tr.chart_template_7a")
    util.delete_unused(cr, "l10n_tr.chart_template_7b")

    if util.version_gte("saas~16.2"):
        # now defined as csv, not updatable from xml.
        util.force_noupdate(cr, "l10n_tr.tax_group_kdv_18", noupdate=False)
        util.force_noupdate(cr, "l10n_tr.tax_group_kdv_20", noupdate=False)
    else:
        util.if_unchanged(cr, "l10n_tr.tax_group_kdv_18", util.update_record_from_xml)
