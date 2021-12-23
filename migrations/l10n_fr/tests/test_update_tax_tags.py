# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("14.0")
class CheckUpgradeTaxTags(UpgradeCase):
    def prepare(self):
        # assume there is only the l10n_fr + its CoA installed
        # case 1: someone removed a tax -> should appear with the info from the template and the correct tags
        # case 2: someone removed some lines of a tax -> create a new tax with the correct tags, old tax should still be there
        # case 3: someone added a tag on a tax -> user defined tag should still be there + the new tags

        # look for one french company
        l10n_fr_chart_template_id = self.env.ref("l10n_fr.l10n_fr_pcg_chart_template").id
        fr_companies = self.env["res.company"].search([("chart_template_id", "=", l10n_fr_chart_template_id)])
        company = fr_companies[0]

        # case 1
        xmlid_1 = f"l10n_fr.{company.id}_tva_acq_specifique_TTC"
        self.env.ref(xmlid_1).unlink()

        # case 2
        # (it should not be linked to any aml, otherwise, the unlink will fail)
        xmlid_2 = f"l10n_fr.{company.id}_tva_intermediaire_ttc"
        tax = self.env.ref(xmlid_2)
        old_tax_id = tax.id
        tax.invoice_repartition_line_ids[1].unlink()
        tax.refund_repartition_line_ids[1].unlink()

        # case 3
        xmlid_3 = f"l10n_fr.{company.id}_tva_intermediaire_encaissement"
        tax = self.env.ref(xmlid_3)

        new_tag = self.env["account.account.tag"].create(
            {  # create tag
                "name": "user defined tag",
                "applicability": "taxes",
                "country_id": company.country_id.id,
            }
        )
        tax.invoice_repartition_line_ids[1].sudo().write({"tag_ids": [(4, new_tag.id)]})  # link it

        return {
            "case_1": {
                "xmlid": xmlid_1,
                "template_xmlid": "l10n_fr.tva_acq_specifique_TTC",
            },
            "case_2": {
                "xmlid": xmlid_2,
                "template_xmlid": "l10n_fr.tva_intermediaire_ttc",
                "old_tax_id": old_tax_id,
            },
            "case_3": {
                "xmlid": xmlid_3,
                "user_defined_tag_id": new_tag.id,
            },
        }

    def check(self, init):
        def test_tax_equal_template(new_tax, new_template_tax):
            for repartition_type in ["invoice_repartition_line_ids", "refund_repartition_line_ids"]:
                self.assertEqual(
                    new_tax[repartition_type].mapped("factor_percent"),
                    new_template_tax[repartition_type].mapped("factor_percent"),
                )
                self.assertEqual(
                    new_tax[repartition_type].mapped("repartition_type"),
                    new_template_tax[repartition_type].mapped("repartition_type"),
                )
                for line, template_line in zip(new_tax[repartition_type], new_template_tax[repartition_type]):
                    tags = template_line.plus_report_line_ids.mapped("tag_ids").filtered(lambda x: not x.tax_negate)
                    tags += template_line.minus_report_line_ids.mapped("tag_ids").filtered(lambda x: x.tax_negate)
                    tags += template_line.tag_ids
                    self.assertEqual(
                        sorted(line.tag_ids.ids),
                        sorted(tags.ids),
                    )
                self.assertEqual(
                    new_tax[repartition_type].mapped("account_id").mapped("code"),
                    new_template_tax[repartition_type].mapped("account_id").mapped("code"),
                )

        # case 1: a new tax with the same xmlid exists + the new tax is the same as the tax template
        new_tax = self.env.ref(init["case_1"]["xmlid"])
        new_template_tax = self.env.ref(init["case_1"]["template_xmlid"])
        test_tax_equal_template(new_tax, new_template_tax)

        # case 2: old tax still exists + new tax is the same as the tax template
        new_tax = self.env.ref(init["case_2"]["xmlid"])
        self.env["account.tax"].browse(init["case_2"]["old_tax_id"])
        new_template_tax = self.env.ref(init["case_2"]["template_xmlid"])
        test_tax_equal_template(new_tax, new_template_tax)

        # case 3: tax still has the "user defined tag" ?
        tax = self.env.ref(init["case_3"]["xmlid"])
        list_tags = tax.invoice_repartition_line_ids[1].tag_ids.ids
        self.assertTrue(init["case_3"]["user_defined_tag_id"] in list_tags)
