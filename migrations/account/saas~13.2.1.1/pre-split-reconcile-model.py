# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        CREATE TABLE account_reconcile_model_line(
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,

            model_id integer,
            sequence integer,
            account_id integer,
            journal_id integer,
            label varchar,
            amount_type varchar,
            force_tax_included boolean,
            amount numeric,
            amount_string varchar,
            analytic_account_id integer
        )
    """
    )
    util.create_m2m(cr, "account_reconcile_model_line_account_tax_rel", "account_reconcile_model_line", "account_tax")
    cr.execute(
        "ALTER TABLE account_reconcile_model_analytic_tag_rel RENAME TO old_account_reconcile_model_analytic_tag_rel"
    )
    # yeah. badly named m2m relation :(
    util.create_m2m(
        cr, "account_reconcile_model_analytic_tag_rel", "account_reconcile_model_line", "account_analytic_tag"
    )

    cr.execute(
        """
        INSERT INTO account_reconcile_model_line(
            create_uid, create_date, write_uid, write_date,
            model_id, sequence, account_id, journal_id,
            label, amount_type, force_tax_included,
            amount, amount_string,
            analytic_account_id
        )
        SELECT create_uid, create_date, write_uid, write_date,
               id, 1, account_id, journal_id,
               label, amount_type, force_tax_included,
               amount, CASE amount_type WHEN 'regex' THEN amount_from_label_regex
                                        WHEN 'percentage' THEN '100'
                        END,
               analytic_account_id
          FROM account_reconcile_model
         WHERE account_id IS NOT NULL
         UNION
        SELECT create_uid, create_date, write_uid, write_date,
               id, 2, second_account_id, second_journal_id,
               second_label, second_amount_type, force_second_tax_included,
               second_amount, CASE second_amount_type WHEN 'regex' THEN second_amount_from_label_regex
                                                      WHEN 'percentage' THEN '100'
                               END,
               second_analytic_account_id
          FROM account_reconcile_model
         WHERE has_second_line = true
           AND second_account_id IS NOT NULL
    """
    )

    cr.execute(
        """
        INSERT INTO account_reconcile_model_line_account_tax_rel(account_reconcile_model_line_id, account_tax_id)
             SELECT l.id, r.account_tax_id
               FROM account_reconcile_model_account_tax_rel r
               JOIN account_reconcile_model_line l ON r.account_reconcile_model_id = l.model_id
              WHERE l.sequence = 1
    """
    )
    cr.execute(
        """
        INSERT INTO account_reconcile_model_line_account_tax_rel(account_reconcile_model_line_id, account_tax_id)
             SELECT l.id, r.account_tax_id
               FROM account_reconcile_model_account_tax_bis_rel r
               JOIN account_reconcile_model_line l ON r.account_reconcile_model_id = l.model_id
              WHERE l.sequence = 2
    """
    )

    cr.execute(
        """
        INSERT INTO account_reconcile_model_analytic_tag_rel(account_reconcile_model_line_id, "account_analytic_tag_id")
             SELECT l.id, r.account_analytic_tag_id
               FROM old_account_reconcile_model_analytic_tag_rel r
               JOIN account_reconcile_model_line l ON r.account_reconcile_model_id = l.model_id
              WHERE l.sequence = 1
    """
    )
    cr.execute(
        """
        INSERT INTO account_reconcile_model_analytic_tag_rel(account_reconcile_model_line_id, "account_analytic_tag_id")
             SELECT l.id, r.account_analytic_tag_id
               FROM account_reconcile_model_second_analytic_tag_rel r
               JOIN account_reconcile_model_line l ON r.account_reconcile_model_id = l.model_id
              WHERE l.sequence = 2
    """
    )

    # And the same for the template
    cr.execute(
        """
        CREATE TABLE account_reconcile_model_line_template(
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,

            model_id integer,
            sequence integer,
            account_id integer,
            label varchar,
            amount_type varchar,
            amount_string varchar,
            force_tax_included boolean
        )
    """
    )
    util.create_m2m(
        cr,
        "account_reconcile_model_line_template_account_tax_template_rel",
        "account_reconcile_model_line_template",
        "account_tax_template",
    )

    cr.execute(
        """
        INSERT INTO account_reconcile_model_line_template(
            create_uid, create_date, write_uid, write_date,
            model_id, sequence, account_id,
            label, amount_type, force_tax_included,
            amount_string
        )
        SELECT create_uid, create_date, write_uid, write_date,
               id, 1, account_id,
               label, amount_type, force_tax_included,
               amount
          FROM account_reconcile_model_template
         UNION
        SELECT create_uid, create_date, write_uid, write_date,
               id, 2, second_account_id,
               second_label, second_amount_type, force_second_tax_included,
               second_amount
          FROM account_reconcile_model_template
         WHERE has_second_line = true
    """
    )
    cr.execute(
        """
        INSERT INTO account_reconcile_model_line_template_account_tax_template_rel(
                        account_reconcile_model_line_template_id, account_tax_template_id)
             SELECT l.id, r.account_tax_template_id
               FROM account_reconcile_model_template_account_tax_template_rel r
               JOIN account_reconcile_model_line_template l ON r.account_reconcile_model_template_id = l.model_id
              WHERE l.sequence = 1
    """
    )
    cr.execute(
        """
        INSERT INTO account_reconcile_model_line_template_account_tax_template_rel(
                        account_reconcile_model_line_template_id, account_tax_template_id)
             SELECT l.id, r.account_tax_template_id
               FROM account_reconcile_model_tmpl_account_tax_bis_rel r
               JOIN account_reconcile_model_line l ON r.account_reconcile_model_template_id = l.model_id
              WHERE l.sequence = 2
    """
    )

    # create xmlid for line.template created
    # NOTE: for now, only line 1 are defined in l10n_ data files
    cr.execute(
        """
        INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
             SELECT x.module,
                    CASE x.module WHEN 'l10n_be' THEN regexp_replace(x.name, '_template$', '_line_template')
                                  WHEN 'l10n_lu' THEN regexp_replace(x.name, '_template$', '_line_template')
                                  WHEN 'l10n_fr' THEN regexp_replace(x.name, '$', '_line')
                                  WHEN 'l10n_de_skr03' THEN regexp_replace(x.name, '$', '_line')
                                  WHEN 'l10n_de_skr04' THEN regexp_replace(x.name, '$', '_line')
                     END,
                    'account.reconcile.model.line.template',
                    l.id,
                    false
               FROM account_reconcile_model_line_template l
               JOIN ir_model_data x ON x.model = 'account.reconcile.model.template' AND x.res_id = l.model_id
              WHERE l.sequence = 1
                AND x.module IN ('l10n_be', 'l10n_lu', 'l10n_fr', 'l10n_de_skr03', 'l10n_de_skr04')
    """
    )

    # Now remove old fields and m2m tables
    gone_fields = util.splitlines(
        """
        {}account_id
        {}journal_id
        {}label
        {}amount_type

        show_{}force_tax_included
        force_{}tax_included

        {}amount
        {}amount_from_label_regex

        {}tax_ids
        {}analytic_account_id
    """
    )
    for field in gone_fields:
        for prefix in ["", "second_"]:
            util.remove_field(cr, "account.reconcile.model", field.format(prefix))
            util.remove_field(cr, "account.reconcile.model.template", field.format(prefix))

    util.remove_field(cr, "account.reconcile.model", "analytic_tag_ids", drop_column=False)
    cr.execute("DROP TABLE old_account_reconcile_model_analytic_tag_rel")
    util.remove_field(cr, "account.reconcile.model.template", "analytic_tag_ids")
    util.remove_field(cr, "account.reconcile.model", "second_analytic_tag_ids")
    util.remove_field(cr, "account.reconcile.model.template", "second_analytic_tag_ids")

    util.remove_field(cr, "account.reconcile.model", "has_second_line")
    util.remove_field(cr, "account.reconcile.model.template", "has_second_line")
