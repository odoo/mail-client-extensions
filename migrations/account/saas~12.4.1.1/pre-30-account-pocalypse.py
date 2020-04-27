# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    is_account_voucher_installed = util.table_exists(cr, "account_voucher")

    # =======================================================================================
    # Migrate chatters
    # =======================================================================================

    model_account_move = util.ref(cr, "account.model_account_move")
    model_account_invoice_id = util.ref(cr, "account.model_account_invoice")
    model_account_voucher_id = util.ref(cr, "account.model_account_voucher")
    cr.execute(
        """
        UPDATE mail_activity
           SET res_model_id = %s
         WHERE res_model IN ('account.invoice', 'account.voucher')
        """,
        [model_account_move],
    )
    cr.execute(
        """
        UPDATE mail_alias
           SET alias_model_id = %s
         WHERE alias_model_id IN (%s, %s)
        """,
        [model_account_move, model_account_invoice_id, model_account_voucher_id],
    )
    cr.execute(
        """
        UPDATE mail_alias
           SET alias_parent_model_id = %s
         WHERE alias_parent_model_id IN (%s, %s)
        """,
        [model_account_move, model_account_invoice_id, model_account_voucher_id],
    )
    cr.execute(
        """
        UPDATE mail_message_subtype
           SET res_model = 'account.move'
         WHERE res_model IN ('account.invoice', 'account.voucher');
        """
    )
    cr.execute(
        """
        UPDATE mail_template
           SET model_id = %s, model = 'account.move'
         WHERE model IN ('account.invoice', 'account.voucher');
        """,
        [model_account_move],
    )

    # =======================================================================================
    # What? Some developers use server action?
    # =======================================================================================
    cr.execute(
        "UPDATE ir_act_server SET binding_model_id= %s WHERE binding_model_id in %s",
        [model_account_move, (model_account_invoice_id, model_account_voucher_id)],
    )
    cr.execute(
        "UPDATE ir_act_server SET crud_model_id= %s WHERE crud_model_id in %s",
        [model_account_move, (model_account_invoice_id, model_account_voucher_id)],
    )
    cr.execute(
        "UPDATE ir_act_server SET model_id= %s WHERE model_id in %s",
        [model_account_move, (model_account_invoice_id, model_account_voucher_id)],
    )

    # =======================================================================================
    # Migrate columns
    # =======================================================================================

    # ==== account_move_line ====
    util.create_column(cr, "account_move_line", "account_internal_type", "varchar")
    util.create_column(cr, "account_move_line", "sequence", "int4")  # computed in post
    util.create_column(cr, "account_move_line", "discount", "numeric")  # computed in post
    util.create_column(cr, "account_move_line", "price_unit", "numeric")  # computed in post
    util.create_column(cr, "account_move_line", "display_type", "varchar")  # computed in post
    util.create_column(cr, "account_move_line", "price_subtotal", "numeric")  # computed in post
    util.create_column(cr, "account_move_line", "price_total", "numeric")  # computed in post
    util.create_column(cr, "account_move_line", "exclude_from_invoice_tab", "boolean")
    util.create_column(cr, "account_move_line", "is_rounding_line", "boolean")  # No way to set this field correctly.

    util.remove_field(cr, "account_move_line", "invoice_id")

    cr.execute(
        """
        UPDATE account_move_line aml
        SET account_internal_type = account.internal_type
        FROM account_account account
        WHERE aml.account_id = account.id
    """
    )

    # ==== account_move ====
    util.create_column(cr, "account_move", "message_main_attachment_id", "int4")  # computed in post

    util.create_column(cr, "account_move", "amount_residual", "numeric")  # computed in post using orm
    util.create_column(cr, "account_move", "amount_residual_signed", "numeric")  # computed in post using orm
    util.create_column(cr, "account_move", "amount_tax", "numeric")  # computed in post using orm
    util.create_column(cr, "account_move", "amount_tax_signed", "numeric")  # computed in post using orm
    util.create_column(cr, "account_move", "amount_total_signed", "numeric")  # computed in post using orm
    util.create_column(cr, "account_move", "amount_untaxed", "numeric")  # computed in post using orm
    util.create_column(cr, "account_move", "amount_untaxed_signed", "numeric")  # computed in post using orm
    util.create_column(cr, "account_move", "type", "varchar")
    util.create_column(cr, "account_move", "commercial_partner_id", "int4")
    util.create_column(cr, "account_move", "company_currency_id", "int4")
    util.create_column(cr, "account_move", "fiscal_position_id", "int4")
    util.create_column(cr, "account_move", "invoice_cash_rounding_id", "int4")
    util.create_column(cr, "account_move", "invoice_date", "date")
    util.create_column(cr, "account_move", "invoice_date_due", "date")
    util.create_column(cr, "account_move", "invoice_incoterm_id", "int4")
    util.create_column(cr, "account_move", "invoice_origin", "varchar")
    util.create_column(cr, "account_move", "invoice_partner_bank_id", "int4")
    util.create_column(cr, "account_move", "invoice_payment_ref", "varchar")
    util.create_column(cr, "account_move", "invoice_payment_state", "varchar")
    util.create_column(cr, "account_move", "invoice_payment_term_id", "int4")
    util.create_column(cr, "account_move", "invoice_sent", "boolean")
    util.create_column(cr, "account_move", "invoice_source_email", "varchar")
    util.create_column(cr, "account_move", "invoice_user_id", "int4")
    util.create_column(cr, "account_move", "invoice_vendor_display_name", "varchar")

    util.rename_field(cr, "account_move", "amount", "amount_total")
    util.rename_field(cr, "account_move", "reverse_entry_id", "reversed_entry_id")

    util.remove_field(cr, "account_move", "matched_percentage")

    # Some previously migrated databases already had this field with wrong values
    cr.execute("UPDATE account_move SET type = NULL")
    # Update account_move from existing account_invoice.
    cr.execute(
        """
        UPDATE account_move am
        SET type = inv.type,
            currency_id = inv.currency_id,
            commercial_partner_id = inv.commercial_partner_id,
            company_currency_id = comp.currency_id,
            fiscal_position_id = inv.fiscal_position_id,
            invoice_cash_rounding_id = inv.cash_rounding_id,
            invoice_date = inv.date_invoice,
            invoice_date_due = inv.date_due,
            invoice_incoterm_id = inv.incoterm_id,
            invoice_origin = inv.origin,
            invoice_partner_bank_id = inv.partner_bank_id,
            invoice_payment_ref = inv.reference,
            invoice_payment_term_id = inv.payment_term_id,
            invoice_sent = inv.sent,
            invoice_source_email = inv.source_email,
            invoice_user_id = inv.user_id,
            invoice_vendor_display_name = inv.vendor_display_name
        FROM account_invoice inv
        JOIN res_company comp ON comp.id = inv.company_id
        WHERE am.id = inv.move_id
    """
    )

    if is_account_voucher_installed:
        # Update account_move from existing account_voucher.
        cr.execute(
            """
            UPDATE account_move am
            SET type = CASE WHEN inv.voucher_type = 'sale' THEN 'out_receipt' ELSE 'in_receipt' END,
                commercial_partner_id = part.commercial_partner_id,
                company_currency_id = comp.currency_id,
                invoice_date = inv.date,
                invoice_date_due = inv.date_due,
                invoice_payment_ref = inv.name
            FROM account_voucher inv
            JOIN res_company comp ON comp.id = inv.company_id
            JOIN res_partner part ON part.id = inv.partner_id
            WHERE move_id IS NOT NULL
            AND am.id = inv.move_id
        """
        )

    # Fix exclude_from_invoice_tab.
    cr.execute(
        """
        UPDATE account_move_line aml
           SET exclude_from_invoice_tab = 't'
          FROM account_move am
         WHERE am.type in ('in_invoice', 'out_invoice', 'in_refund', 'out_refund', 'out_receipt', 'in_receipt')
           AND aml.move_id = am.id
           AND (aml.tax_line_id IS NOT NULL OR aml.account_internal_type IN ('receivable', 'payable'))
        """
    )

    # Fix quantity / price_unit / price_total / price_subtotal on tax lines.
    util.parallel_execute(
        cr,
        [
            """
        -- single-currency
        UPDATE account_move_line aml
           SET quantity = 1,
               price_unit = aml.balance * -1,
               price_subtotal = aml.balance * -1,
               price_total = aml.balance * -1
          FROM account_move am
         WHERE am.type in ('out_invoice', 'in_refund', 'out_receipt')
           AND aml.move_id = am.id
           AND am.currency_id = am.company_currency_id
           AND aml.tax_line_id IS NOT NULL
        """,
            """
        UPDATE account_move_line aml
           SET quantity = 1,
               price_unit = aml.balance,
               price_subtotal = aml.balance,
               price_total = aml.balance
          FROM account_move am
         WHERE am.type in ('in_invoice', 'out_refund', 'in_receipt')
           AND aml.move_id = am.id
           AND am.currency_id = am.company_currency_id
           AND aml.tax_line_id IS NOT NULL
        """,
            """
        -- multi-currencies
        UPDATE account_move_line aml
           SET quantity = 1,
               price_unit = aml.amount_currency * -1,
               price_subtotal = aml.amount_currency * -1,
               price_total = aml.amount_currency * -1
          FROM account_move am
         WHERE am.type in ('out_invoice', 'in_refund', 'out_receipt')
           AND aml.move_id = am.id
           AND am.currency_id != am.company_currency_id
           AND aml.tax_line_id IS NOT NULL
        """,
            """
        UPDATE account_move_line aml
           SET quantity = 1,
               price_unit = aml.amount_currency,
               price_subtotal = aml.amount_currency,
               price_total = aml.amount_currency
          FROM account_move am
         WHERE am.type in ('in_invoice', 'out_refund', 'in_receipt')
           AND aml.move_id = am.id
           AND am.currency_id != am.company_currency_id
           AND aml.tax_line_id IS NOT NULL
        """,
        ],
    )

    # ==== others ====
    util.remove_field(cr, "account.journal", "group_invoice_lines")

    # =======================================================================================
    # Fix account_moves
    # =======================================================================================

    # Inverse relation of reverse_entry_id => reversed_entry_id
    # cr.execute("SELECT id, reversed_entry_id FROM account_move WHERE reversed_entry_id IS NOT NULL")
    # for id, reversed_entry_id in cr.fetchall():
    #     cr.execute("UPDATE account_move SET reversed_entry_id = %s WHERE id = %s", (id, reversed_entry_id))
    cr.execute(
        """
        UPDATE account_move am
           SET reversed_entry_id=amr.id
          FROM account_move amr
         WHERE am.id=amr.reversed_entry_id
    """
    )

    # Fix the many2many crosstable account_invoice_payment_rel that was between account_payment & account_invoice,
    # not between account_payment & account_move.
    cr.execute("ALTER TABLE account_invoice_payment_rel RENAME TO account_invoice_payment_rel_old")
    util.fixup_m2m(cr, "account_invoice_payment_rel_old", "account_invoice", "account_payment", "invoice_id", "payment_id")

    util.create_m2m(cr, "account_invoice_payment_rel", "account_move", "account_payment", "invoice_id", "payment_id")

    cr.execute(
        """
        INSERT INTO account_invoice_payment_rel(invoice_id, payment_id)
             SELECT inv.move_id, old.payment_id
               FROM account_invoice_payment_rel_old old
          LEFT JOIN account_invoice inv ON inv.id = old.invoice_id
              WHERE inv.move_id IS NOT NULL;
        """
    )

    cr.execute("DROP TABLE account_invoice_payment_rel_old")

    # Fix xml_ids
    util.rename_xmlid(cr, "account.model_account_invoice_action_share", "account.model_account_move_action_share")

    # Fix email_template_edi_invoice inside a noupdate block.
    util.force_noupdate(cr, "account.email_template_edi_invoice", noupdate=False)
