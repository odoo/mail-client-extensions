# -*- coding: utf-8 -*-
import logging
import os

from odoo import fields

from odoo.upgrade import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.l10n_mx_reports_closing.16.0.1.0." + __name__)


def _redate_moves_to_dec_31(cr, move_ids_to_redate):
    """Re-date moves to December 31 of their year."""
    cr.execute(
        """ UPDATE account_move
            SET date = DATE_TRUNC('year', date) + INTERVAL '1 year' - INTERVAL '1 day'
            WHERE id IN %(move_ids_to_redate)s;

            UPDATE account_move_line aml
            SET date = move.date
            FROM account_move move
            WHERE aml.move_id = move.id
            AND aml.move_id IN %(move_ids_to_redate)s;
        """,
        {"move_ids_to_redate": tuple(move_ids_to_redate)},
    )


def migrate(cr, version):
    """By default, unmark any Month 13 closing entries that are not dated December 31st,
    then apply the constraint that closing entries must be dated December 31st.

    If the environment variable ODOO_MIG_L10N_MX_REDATE_MONTH_13_CLOSING_MOVES is set to 1,
    instead re-date any wrongly-dated Month 13 closing entries to December 31st of their fiscal year,
    then apply the constraint that closing entries must be dated December 31st.
    """
    util.remove_model(cr, "l10n_mx.trial.closing.report")

    # Get a list of all Month 13 closing entries not dated December 31.
    cr.execute(
        """ SELECT id, name, date, company_id
            FROM account_move
            WHERE l10n_mx_closing_move = TRUE
                AND (
                    DATE_PART('month', date) != 12
                    OR DATE_PART('day', date) != 31
                )
        """
    )
    closing_moves_not_on_dec_31 = cr.fetchall()

    if closing_moves_not_on_dec_31:
        closing_moves_not_on_dec_31_ids = tuple(closing_move[0] for closing_move in closing_moves_not_on_dec_31)
        if util.str2bool(os.getenv("ODOO_MIG_L10N_MX_REDATE_MONTH_13_CLOSING_MOVES", "false")):
            # Redate these moves to December 31 of their fiscal year.
            _redate_moves_to_dec_31(cr, move_ids_to_redate=closing_moves_not_on_dec_31_ids)

            _logger.info(
                "Re-dated the following Month 13 closing entries to December 31st of their fiscal year: account.move%s",
                closing_moves_not_on_dec_31_ids,
            )

            message = """
            <details>
            <summary>
                The Month 13 Trial Balance report now requires all Month 13 closing entries to be dated December 31st.
                Each Month 13 closing entries that was not dated December 31st has been re-dated to
                December 31st of its fiscal year.
            </summary>
            Note: this action was activated with the environment variable
                  ODOO_MIG_L10N_MX_REDATE_MONTH_13_CLOSING_MOVES.
            List of re-dated Journal Entries:
            <ul>
                {}
            </ul>
            </details>
            """.format(
                "\n".join(
                    f"""<li>
                            {util.get_anchor_link_to_record("account.move", id, name)}
                            previously dated {fields.Date.to_string(date)}
                        </li>"""
                    for id, name, date, company_id in closing_moves_not_on_dec_31
                )
            )
            util.add_to_migration_reports(message=message, category="Accounting", format="html")

        else:
            # Un-mark these moves as closing moves.
            cr.execute(
                """ UPDATE account_move
                    SET l10n_mx_closing_move = FALSE
                    WHERE id in %(move_ids_to_unmark)s
                """,
                {"move_ids_to_unmark": closing_moves_not_on_dec_31_ids},
            )

            _logger.info(
                "Unmarked the following Month 13 closing entries: account.move%s",
                closing_moves_not_on_dec_31_ids,
            )

            message = """
            <details>
            <summary>
                The Month 13 Trial Balance report now requires all Month 13 closing entries to be dated December 31st.
                Each Month 13 closing entries that was not dated December 31st has been un-marked as a closing entry.

                If, instead of un-marking those entries, you would prefer to have this script automatically re-date them
                to December 31 for you, you can set the environment variable
                  ODOO_MIG_L10N_MX_REDATE_MONTH_13_CLOSING_MOVES to 1.
            </summary>
            List of un-marked Journal Entries:
            <ul>
                {}
            </ul>
            </details>
            """.format(
                "\n".join(
                    f"""<li>
                            {util.get_anchor_link_to_record("account.move", id, name)}
                            dated {fields.Date.to_string(date)}
                        </li>"""
                    for id, name, date, company_id in closing_moves_not_on_dec_31
                )
            )
            util.add_to_migration_reports(message=message, category="Accounting", format="html")

    # Add constraint that Month 13 closing entries are dated December 31.
    cr.execute(
        """ ALTER TABLE account_move
            ADD CONSTRAINT l10n_mx_closing_move_on_dec_31
            CHECK(
                DATE_PART('month', date) = 12
                AND DATE_PART('day', date) = 31
                OR l10n_mx_closing_move = FALSE
            )
        """
    )
