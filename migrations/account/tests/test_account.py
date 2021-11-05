# -*- coding: utf-8 -*-
from odoo.tests import tagged

from odoo.addons.base.maintenance.migrations.testing import IntegrityCase, UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import version_gte
from odoo.addons.base.maintenance.migrations.util.accounting import no_fiscal_lock


def _amount_query(additionnal_condition=""):
    # The main problem is the change of model from account.invoice to account.move without any
    # easy way to make a matching between them. We need to tepresent amount_total_signed and
    # other values independently of their ids.
    # this solution aggregates all column, only using data that are not demo

    if version_gte("12.4"):  # 12.4 -> master post accountpocalypse
        model_name = "account.move"
    else:  # -> 12.3
        model_name = "account.invoice"

    table_name = model_name.replace(".", "_")

    return """
        SELECT
        journal_id,
        sum({table_name}.amount_untaxed) as amount_untaxed_sum,
        sum({table_name}.amount_tax) as amount_tax_sum,
        sum({table_name}.amount_total) as amount_total_sum,
        sum({table_name}.amount_untaxed_signed) as amount_untaxed_signed_sum,
        sum({table_name}.amount_total_signed) as amount_total_signed_sum
        FROM {table_name}
        LEFT JOIN ir_model_data
        ON ir_model_data.res_id = {table_name}.id
        AND ir_model_data.model = '{model_name}'
        WHERE ir_model_data.id is null
        AND {table_name}.type in ('out_invoice','in_invoice','out_refund','in_refund')
        {additionnal_condition}
        GROUP BY journal_id""".format(
        table_name=table_name, model_name=model_name, additionnal_condition=additionnal_condition
    )


@change_version("12.4")  # prepare: [12.0, 12.4[     check: [12.4, 13]
@tagged("-upgrade", "to_fix")
class AmountTotalSignedCornerCase(UpgradeCase):
    """
    This tests is completely broken!
    1. A first version of this tests inspired from 12.0 test_customer_invoice_tax_include_base_amount
    was showing difference between pre and post migration.

        [9, 81.72, 425.58, 507.3, 81.72, 507.3]
        [9, 507.3, 0.0, 507.3, 507.3, 507.3]

    2 This second version is trying to get rid of demo data (demo data are updated,
        can change, result may be wrong without migration idea, it is better to create
        all test data from scratch as much as possible)

    -> the migration doesn't even pass
    Trying to add not null on account_move.currency_id fails, because there is no
    journal for the active company., leading to an error during migration:
        File "/home/xdo/osrc/13.0/odoo/odoo/fields.py", line 893, in update_db_notnull
            model._init_column(self.name)
        File "/home/xdo/osrc/13.0/odoo/odoo/models.py", line 2400, in _init_column
            value = field.convert_to_write(value, self)
        File "/home/xdo/osrc/13.0/odoo/addons/account/models/account_move.py", line 84, in _get_default_currency
            journal = self._get_default_journal()
        File "/home/xdo/osrc/13.0/odoo/addons/account/models/account_move.py", line 74, in _get_default_journal
            raise UserError(error_msg)
        odoo.exceptions.UserError: ('Please define an accounting miscellaneous journal in your company', '')

    Even if the column has no not null (and may not have one?)
    A solution would be to add not null in pre to avoid orm to add it automatically, or ovveride _init_column

        def _init_column(self, fname):
        if fname == 'currency_id':
            return
        return super()._init_column(fname)

    It is still possible that the presented data here are wrong, is it possible that the default company used in
    _get_default_journal should have a journal in any case? anyway, it would be a bad default value for an
    account_move in another company. In this case the better solution would be to ovveride _init_column a clever
    way to compute the defaul currency group by account_move company id id necessary.

    3. The proposed solution applied in 13.0 allows the migration to finish successfully, but the final result
    is nonsence:
        [1, 81.72, 425.58, 507.3, 81.72, 507.3]
        [1, 0.0, 0.0, 0.0, 0.0, 0.0]
    At this point, I don't know if this data are not correctly initialized, or upgrade scripts are
    wrong, but this need to be fixed latter.

    """

    def prepare(self):
        with no_fiscal_lock(self.env.cr):
            res_users_account_manager = self.env.ref("account.group_account_manager")
            partner_manager = self.env.ref("base.group_partner_manager")
            currency = self.env.ref("base.USD")
            company = self.env["res.company"].create({"name": "company for upgrade tests", "currency_id": currency.id})

            account_user = (
                self.env["res.users"]
                .with_context({"no_reset_password": True})
                .create(
                    {
                        "name": "Accountant for upgrade tests",
                        "company_id": company.id,
                        "company_ids": [(4, company.id)],
                        "login": "acc",
                        "email": "accountuser@yourcompany.com",
                        "groups_id": [(6, 0, [res_users_account_manager.id, partner_manager.id])],
                    }
                )
            )
            self_sudo = account_user.sudo(account_user)
            journal = self_sudo.env["account.journal"].create(
                {"name": "Sale tests upgrade", "type": "sale", "code": "SALEUP"}
            )
            account = self_sudo.env["account.account"].create(
                {
                    "name": "Test account account for amount total signed",
                    "user_type_id": self_sudo.env.ref("account.data_account_type_revenue").id,
                    "code": "aaaaa",
                }
            )
            tax_0 = self_sudo.env["account.tax"].create(
                {"name": "Tax 0.0", "amount": 5.31, "amount_type": "percent", "type_tax_use": "sale", "sequence": 10}
            )
            tax_rec = self_sudo.env["account.tax"].create(
                {
                    "name": "Tax REC",
                    "amount": 10.0,
                    "amount_type": "fixed",
                    "type_tax_use": "sale",
                    "include_base_amount": True,
                    "sequence": 5,
                }
            )
            uom_id = self_sudo.env.ref("uom.product_uom_hour").id

            template = self_sudo.env["account.account.template"].create(
                {
                    "name": "Test account template for amount total signed",
                    "code": "aaaa",
                    "user_type_id": self_sudo.env.ref("account.data_account_type_revenue").id,
                }
            )
            partner = self_sudo.env["res.partner"].create(
                {"name": "Test partner for amount total signed", "property_account_receivable_id": template.id}
            )
            product = self_sudo.env["product.product"].create(
                {
                    "name": "Test product for amount total signed",
                    "standard_price": 20.5,
                    "list_price": 30.75,
                    "type": "service",
                    "uom_id": uom_id,
                    "uom_po_id": uom_id,
                }
            )
            invoice_line_data_rec = [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "quantity": 40.0,
                        "account_id": account.id,
                        "name": "product test 1",
                        "discount": 10.00,
                        "price_unit": 2.27,
                        "invoice_line_tax_ids": [(6, 0, [tax_rec.id, tax_0.id])],
                        "partner_id": partner.id,
                    },
                )
            ]
            invoice_rec = self_sudo.env["account.invoice"].create(
                dict(
                    name="Test Upgrades",
                    journal_id=journal.id,
                    partner_id=partner.id,
                    invoice_line_ids=invoice_line_data_rec,
                )
            )

            invoice_rec.action_invoice_open()

            self.env.cr.execute(_amount_query("AND journal_id = %s"), [journal.id])
            result = self.env.cr.fetchall()
        return journal.id, result

    def check(self, init):
        journal_id, init_result = init
        self.env.cr.execute(_amount_query("AND journal_id = %s"), [journal_id])
        result = self.env.cr.fetchall()
        self.assertEqual(
            init_result,
            result,
            "Some difference found in aggregates totals:\n"
            "(journal_id, amount_untaxed, amount_tax, amount_total, amount_untaxed_signed, amount_total_signed)",
        )


@tagged("-upgrade", "to_fix", "-integrity_case")
class AmountTotalSignedIntegrity(IntegrityCase):

    message = (
        "Some difference found in aggregates totals:\n"
        "(journal_id, amount_untaxed, amount_tax, amount_total, amount_untaxed_signed, amount_total_signed)"
    )

    def invariant(self):
        self.env.cr.execute(_amount_query())
        result = self.env.cr.fetchall()
        return result
