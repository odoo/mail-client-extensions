from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "l10n_in_edi"):
        util.move_field_to_module(cr, "res.company", "l10n_in_edi_production_env", "l10n_in_edi", "l10n_in")
        util.move_field_to_module(cr, "res.config.settings", "l10n_in_edi_production_env", "l10n_in_edi", "l10n_in")
        util.rename_xmlid(cr, *util.expand_braces("l10n_in{_edi,}.iap_service_l10n_in_edi"))
    util.remove_field(cr, "product.template", "l10n_in_hsn_description")
    util.rename_field(cr, "account.move", "l10n_in_hsn_code_warning", "l10n_in_warning")

    cr.execute(r"""
        SELECT ref.name
          FROM ir_model_data ref
         WHERE (ref.name ILIKE 'tcs\_report%'
            OR ref.name ILIKE 'tds\_report%')
           AND ref.module = 'l10n_in'
           AND ref.model IN ('account.report', 'account.report.line', 'account.report.expression', 'account.report.column');
    """)
    xmlids = cr.fetchall()

    if util.module_installed(cr, "l10n_in_withholding"):
        for name in xmlids:
            util.rename_xmlid(cr, f"l10n_in.{name}", f"l10n_in_withholding.{name}")
    else:
        for name in xmlids:
            util.remove_record(cr, f"l10n_in.{name}")
