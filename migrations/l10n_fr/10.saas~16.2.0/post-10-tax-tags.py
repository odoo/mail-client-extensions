# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    for old, news in [
        ("tax_20_0", ["tag_fr_02", "tag_fr_11"]),
        ("tax_8_5", ["tag_fr_04", "tag_fr_13"]),
        ("tax_10_0", ["tag_fr_05", "tag_fr_14"]),
        ("tax_5_5", ["tag_fr_08", "tag_fr_17"]),
        ("tax_2_1", ["tag_fr_09", "tag_fr_18"]),
        ("tax_20_0_TTC", ["tag_fr_02", "tag_fr_11"]),
        ("tax_8_5_TTC", ["tag_fr_04", "tag_fr_13"]),
        ("tax_10_0_TTC", ["tag_fr_05", "tag_fr_14"]),
        ("tax_5_5_TTC", ["tag_fr_08", "tag_fr_17"]),
        ("tax_2_1_TTC", ["tag_fr_09", "tag_fr_18"]),
        ("tax_ACH-20_0", ["tag_fr_20", "tag_fr_30"]),
        ("tax_ACH-8_5", ["tag_fr_23", "tag_fr_32"]),
        ("tax_ACH-10_0", ["tag_fr_24", "tag_fr_33"]),
        ("tax_ACH-5_5", ["tag_fr_27", "tag_fr_36"]),
        ("tax_ACH-2_1", ["tag_fr_28", "tag_fr_37"]),
        ("tax_ACH-20_0_TTC", ["tag_fr_20", "tag_fr_30"]),
        ("tax_ACH-8_5_TTC", ["tag_fr_23", "tag_fr_32"]),
        ("tax_ACH-10_0_TTC", ["tag_fr_24", "tag_fr_33"]),
        ("tax_ACH-tax_5_5", ["tag_fr_08", "tag_fr_17"]),
        ("tax_ACH-2_1_TTC", ["tag_fr_28", "tag_fr_37"]),
        ("tax_IMMO_20_0", ["tag_fr_39", "tag_fr_48"]),
        ("tax_IMMO_8_5", ["tag_fr_41", "tag_fr_50"]),
        ("tax_IMMO-10_0", ["tag_fr_42", "tag_fr_51"]),
        ("tax_IMMO_5_5", ["tag_fr_45", "tag_fr_54"]),
        ("tax_IMMO-2_1", ["tag_fr_46", "tag_fr_55"]),
        ("tax_ACH_UE_due_20_0", ["tag_fr_57", "tag_fr_66"]),
        ("tax_ACH_UE_due_8_5", ["tag_fr_59", "tag_fr_68"]),
        ("tax_ACH_UE_due_10_0", ["tag_fr_60", "tag_fr_69"]),
        ("tax_ACH_UE_due_5_5", ["tag_fr_63", "tag_fr_72"]),
        ("tax_ACH_UE_due_2_1", ["tag_fr_73", "tag_fr_64"]),
        ("tax_ACH_UE_ded_20_0", ["tag_fr_84", "tag_fr_75"]),
        ("tax_ACH_UE_ded_8_5", ["tag_fr_86", "tag_fr_77"]),
        ("tax_ACH_UE_ded_10_0", ["tag_fr_87", "tag_fr_78"]),
        ("tax_ACH_UE_ded_5_5", ["tag_fr_90", "tag_fr_81"]),
        ("tax_ACH_UE_ded_2_1", ["tag_fr_91", "tag_fr_82"]),
        ("tax_EXO_0", ["tag_fr_95"]),
        ("tax_EXPORT_0", ["tag_fr_93"]),
        ("tax_UE_0", ["tag_fr_94"]),
        ("tax_IMPORT_0", ["tag_fr_97"]),
        ("tax_ACH_UE_ded_20_0", ["tag_fr_84", "tag_fr_75"]),
    ]:
        old_tag_id = util.ref(cr, "l10n_fr.%s" % old)
        if old_tag_id:
            env["account.tax"].search([("tag_ids", "in", old_tag_id)]).write(
                {"tag_ids": [(4, util.ref(cr, "l10n_fr.%s" % new)) for new in news]}
            )
