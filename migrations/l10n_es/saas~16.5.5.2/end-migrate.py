from odoo.upgrade import util

tag_migration_utils = util.import_script("l10n_mn/saas~16.5.1.1/end-migrate.py")


def migrate(cr, version):
    tax_tag_changes = {
        "mod_111_02": ("mod111[02]", "+", "base"),
        "mod_111_03": ("mod111[03]", "-", "tax"),
        "mod_111_05": ("mod111[05]", "+", "base"),
        "mod_111_06": ("mod111[06]", "-", "tax"),
        "mod_111_08": ("mod111[08]", "+", "base"),
        "mod_111_09": ("mod111[09]", "-", "tax"),
        "mod_111_11": ("mod111[11]", "+", "base"),
        "mod_111_12": ("mod111[12]", "-", "tax"),
        "mod_115_02": ("mod115[02]", "+", "base"),
        "mod_115_03": ("mod115[03]", "-", "tax"),
        "mod_303_150": ("mod303[150]", "-", "base"),
        "mod_303_152": ("mod303[152]", "-", "tax"),
        "mod_303_01": ("mod303[01]", "-", "base"),
        "mod_303_03": ("mod303[03]", "-", "tax"),
        "mod_303_153": ("mod303[153]", "-", "base"),
        "mod_303_155": ("mod303[155]", "-", "tax"),
        "mod_303_04": ("mod303[04]", "-", "base"),
        "mod_303_06": ("mod303[06]", "-", "tax"),
        "mod_303_07": ("mod303[07]", "-", "base"),
        "mod_303_09": ("mod303[09]", "-", "tax"),
        "mod_303_10": ("mod303[10]", "+", "base"),
        "mod_303_11": ("mod303[11]", "-", "tax"),
        "mod_303_12": ("mod303[12]", "+", "base"),
        "mod_303_13": ("mod303[13]", "-", "tax"),
        "mod_303_14_sale": ("mod303[14_sale]", "-", "base"),
        "mod_303_14_purchase": ("mod303[14_purchase]", "-", "base"),
        "mod_303_15": ("mod303[15]", "-", "tax"),
        "mod_303_156": ("mod303[156]", "-", "base"),
        "mod_303_158": ("mod303[158]", "-", "tax"),
        "mod_303_16": ("mod303[16]", "-", "base"),
        "mod_303_18": ("mod303[18]", "-", "tax"),
        "mod_303_19": ("mod303[19]", "-", "base"),
        "mod_303_21": ("mod303[21]", "-", "tax"),
        "mod_303_22": ("mod303[22]", "-", "base"),
        "mod_303_24": ("mod303[24]", "-", "tax"),
        "mod_303_25": ("mod303[25]", "-", "base"),
        "mod_303_26": ("mod303[26]", "-", "tax"),
        "mod_303_28": ("mod303[28]", "+", "base"),
        "mod_303_29": ("mod303[29]", "+", "tax"),
        "mod_303_30": ("mod303[30]", "+", "base"),
        "mod_303_31": ("mod303[31]", "+", "tax"),
        "mod_303_32": ("mod303[32]", "+", "base"),
        "mod_303_33": ("mod303[33]", "+", "tax"),
        "mod_303_34": ("mod303[34]", "+", "base"),
        "mod_303_35": ("mod303[35]", "+", "tax"),
        "mod_303_36": ("mod303[36]", "+", "base"),
        "mod_303_37": ("mod303[37]", "+", "tax"),
        "mod_303_38": ("mod303[38]", "+", "base"),
        "mod_303_39": ("mod303[39]", "+", "tax"),
        "mod_303_40": ("mod303[40]", "+", "base"),
        "mod_303_41": ("mod303[41]", "+", "tax"),
        "mod_303_42": ("mod303[42]", "+", "tax"),
        "mod_303_59": ("mod303[59]", "-", "base"),
        "mod_303_60": ("mod303[60]", "-", "base"),
        "mod_303_120": ("mod303[120]", "-", "base"),
        "mod_303_122": ("mod303[122]", "-", "base"),
        "mod_303_123": ("mod303[123]", "-", "base"),
        "mod_303_124": ("mod303[124]", "-", "base"),
    }

    old_tag_ids = tag_migration_utils.migrate_tags_to_tax_tags_engine(cr, "l10n_es", tax_tag_changes)

    cr.execute(
        """
        DELETE FROM account_account_tag_account_tax_repartition_line_rel
                WHERE account_account_tag_id = ANY(%s)
        """,
        [old_tag_ids],
    )
    # reload new tags repartition lines
    cr.commit()
    env = util.env(cr)
    CoA = env["account.chart.template"]
    for company in env["res.company"].search(
        [("chart_template", "in", ("es_pymes", "es_full", "es_assec", "es_common"))]
    ):
        try:
            CoA.try_loading(company.chart_template, company=company, install_demo=False)
            cr.commit()
        except Exception:
            cr.rollback()
