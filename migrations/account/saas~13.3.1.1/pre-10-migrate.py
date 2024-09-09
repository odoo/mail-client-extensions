from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.fixup_m2m(
        cr,
        "account_journal_account_print_journal_rel",
        "account_journal",
        "account_print_journal",
    )

    # ===========================================================
    # QR codes (PR:44839)
    # ===========================================================
    util.create_column(cr, "account_move", "qr_code_method", "varchar")

    # ===========================================================
    # Incoterms (PR:43883)
    # ===========================================================

    util.rename_field(cr, "account.move", "type", "move_type")
    util.rename_field(cr, "account.invoice.report", "type", "move_type")
    util.rename_field(cr, "account.move.line", "tag_ids", "tax_tag_ids")

    # ===========================================================
    # Internal Transfer (PR:45812 & 8595)
    # ===========================================================

    util.remove_field(cr, "account.payment", "destination_journal_id")
    util.create_column(cr, "account_payment", "is_internal_transfer", "boolean")
    util.explode_execute(
        cr,
        """
        UPDATE account_payment
           SET is_internal_transfer = (payment_type = 'transfer')
        """,
        table="account_payment",
    )
    # change payment_type from 'transfer' to 'inbound', update partner_id & move_name
    cr.commit()
    util.explode_execute(
        cr,
        """
        UPDATE account_payment pay
           SET payment_type = 'outbound',
               partner_id = comp.partner_id,
               move_name = split_part(pay.move_name, '§§', 1)
          FROM account_journal journal
          JOIN res_company comp ON comp.id = journal.company_id
         WHERE journal.id = pay.journal_id
           AND pay.payment_type = 'transfer'
        """,
        table="account_payment",
        alias="pay",
    )

    # ===========================================================
    # Account Security (PR:46586 & 8986)
    # ===========================================================

    # Add new company_id stored related fields.

    util.create_column(cr, "account_reconcile_model_line", "company_id", "int4")
    cr.execute(
        """
        UPDATE account_reconcile_model_line line
        SET company_id = model.company_id
        FROM account_reconcile_model model
        WHERE model.id = line.model_id
    """
    )

    util.create_column(cr, "account_fiscal_position_tax", "company_id", "int4")
    cr.execute(
        """
         UPDATE account_fiscal_position_tax fpos_tax
         SET company_id = fpos.company_id
         FROM account_fiscal_position fpos
         WHERE fpos.id = fpos_tax.position_id
    """
    )

    util.create_column(cr, "account_fiscal_position_account", "company_id", "int4")
    cr.execute(
        """
         UPDATE account_fiscal_position_account fpos_account
         SET company_id = fpos.company_id
         FROM account_fiscal_position fpos
         WHERE fpos.id = fpos_account.position_id
    """
    )

    util.create_column(cr, "account_payment", "company_id", "int4")
    cr.commit()
    util.explode_execute(
        cr,
        """
        UPDATE account_payment pay
        SET company_id = journal.company_id
        FROM account_journal journal
        WHERE journal.id = pay.journal_id
        """,
        table="account_payment",
        alias="pay",
    )

    util.convert_field_to_property(
        cr,
        "account.cash.rounding",
        "profit_account_id",
        "many2one",
        target_model="account.account",
        company_field="NULL",
    )
    if util.column_exists(cr, "account_cash_rounding", "loss_account_id"):
        # field was in `point_of_sale` before `saas~13.1`
        util.convert_field_to_property(
            cr,
            "account.cash.rounding",
            "loss_account_id",
            "many2one",
            target_model="account.account",
            company_field="NULL",
        )

    util.create_column(cr, "account_tax_repartition_line", "use_in_tax_closing", "bool")
    util.create_column(cr, "account_tax_repartition_line_template", "use_in_tax_closing", "bool")

    cr.execute(
        """
         UPDATE account_tax_repartition_line
            SET use_in_tax_closing = TRUE
           FROM account_account
          WHERE account_tax_repartition_line.account_id = account_account.id
            AND account_account.internal_group NOT IN ('income', 'expense')
        """
    )
    cr.execute(
        """
         UPDATE account_tax_repartition_line
            SET use_in_tax_closing = FALSE
          WHERE use_in_tax_closing IS NULL
        """
    )

    util.create_column(cr, "account_move_reversal", "company_id", "int4")
    util.create_column(cr, "account_move_reversal", "date_mode", "varchar")
    cr.execute("UPDATE account_move_reversal SET date_mode = 'custom' WHERE date_mode IS NULL")

    util.move_field_to_module(cr, "res.config.settings", "country_code", "account_check_printing", "account")

    # data
    util.remove_view(cr, "account.partner_view_short_extra")

    incoterm_codes = "DAF,DES,DEQ,DDU,DAT".split(",")
    for code in incoterm_codes:
        util.force_noupdate(cr, f"account.incoterm_{code}")

    cr.execute(
        "UPDATE account_incoterms SET active = 'f' WHERE id IN %s",
        [tuple(util.ref(cr, f"account.incoterm_{code}") for code in incoterm_codes)],
    )
