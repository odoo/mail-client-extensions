# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.3")
class TestPartnerDefaultVIES(UpgradeCase):
    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------
    def _standard_move_dict(self, company, partner):
        """Create a dictionary for a move using the specified company and partner"""
        return {
            "partner_id": partner.id,
            "move_type": "out_invoice",
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "mandatory line",
                        "price_unit": 10000,
                        "quantity": 1,
                        "tax_ids": [],
                    },
                )
            ],
        }

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------
    def _test_partner_vies_default_true_by_fpos(self, company):
        """VIES valid for this partner should be set to true in migration because of a fiscal position

        When the upgrade migration occurs, it should detect that this partner has:
        - a vat code that could be tested against the VIES system
        - a posted account move that utilises a fiscal position that would represent
          some kind of EU intracommunity trade
        Thus we can set VIES as valid by default for this partner
        """
        partner_to_update = self.env["res.partner"].create(
            {
                "name": "Deutsch Co",
                "country_id": self.env.ref("base.de").id,
                "vat": "DE123456788",
            }
        )

        valid_fpos = (
            self.env["account.fiscal.position"]
            .with_company(company)
            .create(
                {
                    "name": "probably-an-intracommunity-position",
                    "auto_apply": True,
                    "vat_required": True,
                    "country_group_id": self.env.ref("base.europe").id,
                }
            )
        )

        self.env["account.move"].with_company(company).create(
            {
                **self._standard_move_dict(company, partner_to_update),
                "fiscal_position_id": valid_fpos.id,
            }
        ).action_post()

        return partner_to_update.id

    def _test_partner_vies_default_true_by_move(self, company):
        """VIES valid for this partner should be set to true in migration because of a move

        When the upgrade migration occurs, it should detect that this partner has:
        - a vat code that could be tested against the VIES system
        - a move posted by an EU company and no total tax and no fiscal position
        Thus we can set VIES as valid by default for this partner
        """
        partner_to_update = self.env["res.partner"].create(
            {
                "name": "French Co",
                "country_id": self.env.ref("base.fr").id,
                "vat": "FR23334175221",
            }
        )

        self.env["account.move"].with_company(company).create(
            {
                **self._standard_move_dict(company, partner_to_update),
                "fiscal_position_id": None,
            }
        ).action_post()
        return partner_to_update.id

    def _test_partner_vies_default_false_by_company(self, company):
        """VIES valid for this partner should be set to true in migration because of the move

        When the upgrade migration occurs, it should detect that this partner has:
        - a vat code that could be tested against the VIES system
        - a posted move with and no total tax and no fiscal position, but not belonging to an EU company
        Thus we can set VIES as not valid by default for this partner
        """
        partner_to_update = self.env["res.partner"].create(
            {
                "name": "Spanish Co",
                "country_id": self.env.ref("base.es").id,
                "vat": "ESA12345674",
            }
        )

        # The move is the same as before, it's posted using a company outside of the EU
        # (this means the partner has no invoices from an EU company)
        self.env["account.move"].with_company(company).create(
            self._standard_move_dict(company, partner_to_update),
        ).action_post()
        return partner_to_update.id

    # -------------------------------------------------------------------------
    # PREPARE
    # -------------------------------------------------------------------------
    def prepare(self):
        primary_company = self.env["res.company"].create({"name": "primary company for TestPartnerDefaultVIES"})
        secondary_company = self.env["res.company"].create({"name": "secondary company for TestPartnerDefualtVIES"})
        for company in (primary_company, secondary_company):
            if util.version_gte("saas~16.2"):
                self.env["account.chart.template"].try_loading("generic_coa", company=company, install_demo=False)
            elif util.version_gte("16.0"):
                self.env.ref("l10n_generic_coa.configurable_chart_template").try_loading(
                    company=company, install_demo=False
                )
            else:
                self.env.ref("l10n_generic_coa.chart_template").try_loading(company=company, install_demo=False)
            primary_company.account_fiscal_country_id = self.env.ref("base.be")

        return {
            "partner_ids": (
                self._test_partner_vies_default_true_by_fpos(primary_company),
                self._test_partner_vies_default_true_by_move(primary_company),
                self._test_partner_vies_default_false_by_company(secondary_company),
            ),
        }

    def check(self, init):
        valid_partner_fpos, valid_partner_move, invalid_partner = self.env["res.partner"].browse(init["partner_ids"])
        self.assertTrue(valid_partner_fpos.vies_valid)
        self.assertTrue(valid_partner_move.vies_valid)
        self.assertFalse(invalid_partner.vies_valid)
