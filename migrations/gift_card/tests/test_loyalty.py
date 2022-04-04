# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.3")
class TestLoyalty(UpgradeCase):
    def prepare(self):
        # Weird case when we have gift cards in multiple companies
        companies = self.env["res.company"].create(
            [
                {
                    "name": "UPGRADE_gift_card_1",
                },
                {
                    "name": "UPGRADE_gift_card_2",
                },
            ]
        )
        self.env["gift.card"].create(
            [
                {
                    "company_id": companies[0].id,
                    "initial_amount": 50,
                },
                {
                    "company_id": companies[1].id,
                    "initial_amount": 50,
                },
                {
                    "company_id": companies[1].id,
                    "initial_amount": 50,
                },
            ]
        )

        return (companies.ids,)

    def check(self, init):
        # The check is done in migrations/loyalty/tests/test_migrate_gift_card.py
        return
