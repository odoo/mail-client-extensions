# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_m2m(cr, "account_reconcile_model_account_tax_rel", "account_reconcile_model", "account_tax")
    cr.execute(
        """
        INSERT INTO account_reconcile_model_account_tax_rel(account_reconcile_model_id, account_tax_id)
             SELECT id, tax_id
               FROM account_reconcile_model
              WHERE tax_id IS NOT NULL
    """
    )
    util.create_m2m(cr, "account_reconcile_model_account_tax_bis_rel", "account_reconcile_model", "account_tax")
    cr.execute(
        """
        INSERT INTO account_reconcile_model_account_tax_bis_rel(account_reconcile_model_id, account_tax_id)
             SELECT id, second_tax_id
               FROM account_reconcile_model
              WHERE second_tax_id IS NOT NULL
    """
    )

    util.create_column(cr, "account_reconcile_model", "show_force_tax_included", "boolean")
    util.create_column(cr, "account_reconcile_model", "show_second_force_tax_included", "boolean")
    cr.execute(
        """
        UPDATE account_reconcile_model
           SET show_force_tax_included = (tax_id IS NOT NULL),
               show_second_force_tax_included = (second_tax_id IS NOT NULL)
    """
    )

    fields = """
        is_tax_price_included
        tax_amount_type
        tax_id

        is_second_tax_price_included
        second_tax_amount_type
        second_tax_id
    """
    for field in util.splitlines(fields):
        util.remove_field(cr, "account.reconcile.model", field)

    # and the template
    util.create_m2m(
        cr,
        "account_reconcile_model_template_account_tax_template_rel",
        "account_reconcile_model_template",
        "account_tax_template",
    )
    cr.execute(
        """
        INSERT INTO account_reconcile_model_template_account_tax_template_rel(
            account_reconcile_model_template_id, account_tax_template_id
        )
        SELECT id, tax_id
          FROM account_reconcile_model_template
         WHERE tax_id IS NOT NULL
    """
    )
    util.create_m2m(
        cr,
        "account_reconcile_model_tmpl_account_tax_bis_rel",
        "account_reconcile_model_template",
        "account_tax_template",
    )
    cr.execute(
        """
        INSERT INTO account_reconcile_model_tmpl_account_tax_bis_rel(
            account_reconcile_model_template_id, account_tax_template_id
        )
        SELECT id, second_tax_id
          FROM account_reconcile_model_template
         WHERE second_tax_id IS NOT NULL
    """
    )

    util.remove_field(cr, "account.reconcile.model.template", "tax_id")
    util.remove_field(cr, "account.reconcile.model.template", "second_tax_id")
