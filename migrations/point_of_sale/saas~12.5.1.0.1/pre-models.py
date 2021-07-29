# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    util.create_column(cr, "account_bank_statement_cashbox", "is_a_template", "boolean")
    util.create_column(cr, "pos_config", "default_cashbox_id", "int4")
    cr.execute(
        """
        SELECT default_pos_id, array_agg(id)
          FROM account_cashbox_line
         WHERE default_pos_id IS NOT NULL
      GROUP BY default_pos_id
    """
    )

    for pos_config_id, ids in cr.fetchall():
        cr.execute("INSERT INTO account_bank_statement_cashbox(is_a_template) VALUES(true) RETURNING id")
        (cid,) = cr.fetchone()
        cr.execute(
            """
            INSERT INTO account_cashbox_line(coin_value, number, cashbox_id)
                 SELECT coin_value, number, %s
                   FROM account_cashbox_line
                  WHERE id IN %s
        """,
            [cid, tuple(ids)],
        )
        cr.execute("UPDATE pos_config SET default_cashbox_id = %s WHERE id = %s", [cid, pos_config_id])

    util.remove_field(cr, "account.cashbox.line", "default_pos_id")
    util.remove_field(cr, "pos.config", "default_cashbox_lines_ids")

    util.create_column(cr, "pos_config", "amount_authorized_diff", "float8")
    cr.execute(
        """
        WITH diff AS (
            SELECT r.pos_config_id, min(COALESCE(j.amount_authorized_diff, 0)) diff
              FROM pos_config_journal_rel r
              JOIN account_journal j ON j.id = r.journal_id
              GROUP BY pos_config_id
        )
        UPDATE pos_config c
           SET amount_authorized_diff = diff.diff
          FROM diff
         WHERE diff.pos_config_id = c.id
    """
    )

    mercury = util.module_installed(cr, "pos_mercury")

    # create pos.payment.method from journals
    cr.execute(
        """
        CREATE TABLE pos_payment_method (
            id SERIAL NOT NULL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            name varchar NOT NULL,
            receivable_account_id int4, -- NOT NULL,
            is_cash_count boolean,
            cash_journal_id int4,
            split_transactions boolean,
            company_id int4,
            use_payment_terminal varchar
            {}
        )
    """.format(
            ", pos_mercury_config_id int4" if mercury else ""
        )
    )

    util.create_m2m(cr, "pos_config_pos_payment_method_rel", "pos_config", "pos_payment_method")

    # NOTE: reuse `create_uid` to store the original journal_id
    cr.execute(
        """
        INSERT INTO pos_payment_method(create_uid, create_date, name,
                                       receivable_account_id, is_cash_count, cash_journal_id,
                                       split_transactions, company_id {0})
    SELECT DISTINCT j.id, now() at time zone 'UTC', j.name,
                    c.account_default_pos_receivable_account_id,
                    (j.type = 'cash'), CASE j.type WHEN 'cash' THEN j.id ELSE NULL END,
                    false, c.id {1}
               FROM pos_config_journal_rel r
               JOIN account_journal j ON j.id = r.journal_id
               JOIN res_company c ON c.id = j.company_id
    """.format(
            ", pos_mercury_config_id" if mercury else "", ", j.pos_mercury_config_id" if mercury else ""
        )
    )
    cr.execute(
        """
        INSERT INTO pos_config_pos_payment_method_rel(pos_config_id, pos_payment_method_id)
             SELECT r.pos_config_id, m.id
               FROM pos_config_journal_rel r
               JOIN pos_payment_method m ON r.journal_id = m.create_uid
    """
    )

    util.remove_field(cr, "pos.config", "iface_payment_terminal")
    util.remove_field(cr, "pos.config", "group_by")
    util.remove_column(cr, "pos_config", "customer_facing_display_html")

    util.create_column(cr, "pos_config", "other_devices", "boolean")

    util.remove_field(cr, "pos.order", "statement_ids")
    util.create_column(cr, "pos_order", "to_invoice", "boolean")

    # create pos.payment from statements
    mercury_fields = (
        set() if not mercury else {"card_number", "card_brand", "card_owner_name", "ref_no", "record_no", "invoice_no"}
    )
    cr.execute(
        """
        CREATE TABLE pos_payment (
            id SERIAL NOT NULL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            name varchar,
            pos_order_id int4 NOT NULL,
            amount numeric NOT NULL,
            payment_method_id int4 NOT NULL,
            payment_date timestamp without time zone NOT NULL,
            session_id int4,
            card_type varchar,
            transaction_id varchar
            {}
        )
    """.format(
            "".join(", mercury_{} varchar".format(f) for f in mercury_fields)
        )
    )
    cr.execute(
        """
        INSERT INTO pos_payment(create_uid, create_date, name, pos_order_id, amount,
                                payment_method_id, payment_date, session_id, transaction_id {0})
             SELECT s.create_uid, s.create_date, s.name, o.id, s.amount,
                    m.id, s.date, o.session_id, s.ref {1}
               FROM account_bank_statement_line s
               JOIN pos_order o ON o.id = s.pos_statement_id
               JOIN pos_payment_method m ON m.create_uid = s.journal_id
    """.format(
            "".join(", mercury_" + f for f in mercury_fields), "".join(", s.mercury_" + f for f in mercury_fields)
        )
    )

    cr.execute("UPDATE pos_payment_method SET create_uid = 1")

    util.create_column(cr, "pos_session", "move_id", "int4")

    util.remove_field(cr, "pos.config", "journal_ids")
    util.remove_field(cr, "pos.session", "journal_ids")

    util.remove_field(cr, "res.config.settings", "pos_sales_price")
    util.remove_field(cr, "res.config.settings", "pos_pricelist_setting")
    cr.execute(
        """
        DELETE FROM ir_config_parameter
              WHERE key IN ('point_of_sale.pos_sales_price', 'point_of_sale.pos_pricelist_setting')
    """
    )

    # Wizard
    util.remove_model(cr, "pos.open.statement")
    util.remove_field(cr, "pos.make.payment", "session_id")
    util.remove_field(cr, "pos.make.payment", "journal_id")
    util.create_column(cr, "pos_make_payment", "config_id", "int4")
    util.create_column(cr, "pos_make_payment", "payment_method_id", "int4")
    cr.execute("ALTER TABLE pos_make_payment ALTER COLUMN payment_date TYPE timestamp without time zone")

    util.remove_field(cr, "account.journal", "journal_user")
    util.remove_field(cr, "account.journal", "amount_authorized_diff")
