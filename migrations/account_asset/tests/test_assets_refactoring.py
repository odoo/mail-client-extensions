# -*- coding: utf-8 -*-

import datetime

from freezegun import freeze_time

from odoo import fields

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util.accounting import no_fiscal_lock

REF_DATE = "2020-10-06"
REF_DATE_2 = "2023-03-31"


@change_version("16.0")
class AssetsRevampingCase(UpgradeCase):
    def prepare(self):
        self.env.company.fiscalyear_last_month = "12"
        self.env.company.fiscalyear_last_day = 31

        with freeze_time(REF_DATE):
            account_asset, account_asset_depreciation_expense, account_depreciation = self.env[
                "account.account"
            ].create(
                [
                    {
                        "name": "_UPG_ fixed assets",
                        "code": "999241000",
                        "user_type_id": self.env.ref("account.data_account_type_current_assets").id,
                    },
                    {
                        "name": "_UPG_ assets depreciation",
                        "code": "999241009",
                        "user_type_id": self.env.ref("account.data_account_type_expenses").id,
                    },
                    {
                        "name": "_UPG_ assets depreciation expense",
                        "code": "999630200",
                        "user_type_id": self.env.ref("account.data_account_type_current_assets").id,
                    },
                ]
            )
            journal = self.env["account.journal"].create(
                {"name": "_UPG_ miscellaneous", "type": "general", "code": "UPG_M"}
            )
            asset = (
                self.env["account.asset"]
                .with_context(asset_type="purchase")
                .create(
                    {
                        "account_depreciation_id": account_depreciation.id,
                        "account_depreciation_expense_id": account_asset_depreciation_expense.id,
                        "account_asset_id": account_asset.id,
                        "journal_id": journal.id,
                        "salvage_value": 2000.0,
                        "state": "open",
                        "method_period": "12",
                        "method_number": 5,
                        "name": "CEO's Car",
                        "original_value": 12000.0,
                    }
                )
            )
            asset.validate()
            asset2 = (
                self.env["account.asset"]
                .with_context(asset_type="purchase")
                .create(
                    {
                        "account_depreciation_id": account_depreciation.id,
                        "account_depreciation_expense_id": account_asset_depreciation_expense.id,
                        "account_asset_id": account_asset.id,
                        "journal_id": journal.id,
                        "salvage_value": 2000.0,
                        "state": "open",
                        "method_period": "12",
                        "method_number": 5,
                        "name": "CEO's Car",
                        "original_value": 12000.0,
                    }
                )
            )
            asset2.validate()

        with freeze_time(REF_DATE_2), no_fiscal_lock(self.env.cr):
            asset_imported = (
                self.env["account.asset"]
                .with_context(asset_type="purchase")
                .create(
                    {
                        "account_depreciation_id": account_depreciation.id,
                        "account_depreciation_expense_id": account_asset_depreciation_expense.id,
                        "account_asset_id": account_asset.id,
                        "journal_id": journal.id,
                        "acquisition_date": "2018-10-01",
                        "first_depreciation_date": "2022-12-31",
                        "method_period": "12",
                        "method_number": 5,
                        "name": "Asset To sell",
                        "original_value": 2000.0,
                        "already_depreciated_amount_import": 1000,
                        "depreciation_number_import": 2,
                        "first_depreciation_date_import": "2019-06-11",
                    }
                )
            )
            asset_imported.validate()

        with freeze_time("2023-06-25"), no_fiscal_lock(self.env.cr):
            asset_imported2 = (
                self.env["account.asset"]
                .with_context(asset_type="purchase")
                .create(
                    {
                        "account_depreciation_id": account_depreciation.id,
                        "account_depreciation_expense_id": account_asset_depreciation_expense.id,
                        "account_asset_id": account_asset.id,
                        "journal_id": journal.id,
                        "acquisition_date": "2021-06-30",
                        "first_depreciation_date": "2022-10-30",
                        "method_period": "1",
                        "method_number": 48,
                        "name": "Asset imported to sell",
                        "original_value": 2000.0,
                        "already_depreciated_amount_import": 501.92,
                        "depreciation_number_import": 12,
                        "first_depreciation_date_import": "2021-06-30",
                    }
                )
            )
            asset_imported2.validate()

        with freeze_time(REF_DATE_2), no_fiscal_lock(self.env.cr):
            asset_imported3 = (
                self.env["account.asset"]
                .with_context(asset_type="purchase")
                .create(
                    {
                        "account_depreciation_id": account_depreciation.id,
                        "account_depreciation_expense_id": account_asset_depreciation_expense.id,
                        "account_asset_id": account_asset.id,
                        "journal_id": journal.id,
                        "acquisition_date": "2021-06-30",
                        "first_depreciation_date": "2022-10-30",
                        "method_period": "1",
                        "method_number": 30,
                        "name": "Asset imported to sell",
                        "original_value": 2000.0,
                        "already_depreciated_amount_import": 1990,
                        "depreciation_number_import": 12,
                        "first_depreciation_date_import": "2021-06-30",
                    }
                )
            )
            asset_imported3.validate()

        return {
            "assets": [
                asset.id,
                asset2.id,
                asset_imported.id,
                asset_imported2.id,
                asset_imported3.id,
            ],
        }

    def check(self, init):
        ref = datetime.date.fromisoformat(REF_DATE)
        d = datetime.date(
            year=ref.year,
            month=int(self.env.company.fiscalyear_last_month),
            day=self.env.company.fiscalyear_last_day,
        )
        if d >= ref:
            d = d.replace(year=d.year - 1)
        d += datetime.timedelta(days=1)

        (asset1, asset2, asset_imported, asset_imported2, asset_imported3) = self.env["account.asset"].browse(
            init["assets"]
        )

        for asset in (asset1, asset2):
            moves = asset.depreciation_move_ids.sorted(lambda m: m.id)
            for i, depreciation_move in enumerate(moves):
                with self.subTest(depreciation_move=depreciation_move, i=i):
                    self.assertEqual(depreciation_move.asset_depreciation_beginning_date, d.replace(year=d.year + i))
                    self.assertEqual(depreciation_move.asset_number_days, 360)
                    self.assertEqual(depreciation_move.depreciation_value, 2000)

        self.assertRecordValues(
            asset_imported,
            [
                {
                    "prorata_date": fields.Date.from_string("2017-01-01"),
                    "method_number": 10,
                    "prorata_computation_type": "constant_periods",
                }
            ],
        )

        with freeze_time(REF_DATE_2), no_fiscal_lock(self.env.cr):
            self.env["asset.modify"].create(
                {
                    "name": "Nothing changed",
                    "asset_id": asset_imported.id,
                    "date": datetime.date.today(),
                }
            ).modify()

        self.assertRecordValues(
            asset_imported.depreciation_move_ids.sorted(lambda m: (m.date, m.id)),
            [
                {"date": fields.Date.from_string("2022-12-31"), "depreciation_value": 200},
                {"date": fields.Date.from_string("2023-03-31"), "depreciation_value": 50},
                {"date": fields.Date.from_string("2023-12-31"), "depreciation_value": 150},
                {"date": fields.Date.from_string("2024-12-31"), "depreciation_value": 200},
                {"date": fields.Date.from_string("2025-12-31"), "depreciation_value": 200},
                {"date": fields.Date.from_string("2026-12-31"), "depreciation_value": 200},
            ],
        )

        self.assertRecordValues(
            asset_imported2,
            [
                {
                    "prorata_date": fields.Date.from_string("2021-06-01"),
                    "method_number": 64,
                    "prorata_computation_type": "constant_periods",
                }
            ],
        )

        self.assertRecordValues(
            asset_imported3,
            [
                {
                    "prorata_date": fields.Date.from_string("2020-04-01"),
                    "method_number": 30,
                    "prorata_computation_type": "constant_periods",
                }
            ],
        )
