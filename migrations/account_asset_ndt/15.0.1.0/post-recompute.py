import contextlib
import logging
import os
from textwrap import dedent

from odoo.upgrade import util

_logger = logging.getLogger(__name__)

ODOO_UPG_UNLINK_CREDIT_LINES_FROM_ASSETS = util.str2bool(os.getenv("ODOO_UPG_UNLINK_CREDIT_LINES_FROM_ASSETS", "0"))


@contextlib.contextmanager
def post_moves(cr):
    # Draft assets linked to a (draft) vendor bill with posted deprecation entries
    # are wrong, to avoid issues with the compute below we temporarily mark them
    # as posted. See also migrations/account_asset/15.0.1.0/pre-migrate.py
    cr.execute("ALTER TABLE account_move ADD COLUMN _upg_old_state varchar")
    util.explode_execute(
        cr,
        """
        UPDATE account_move vendor_bill
           SET _upg_old_state = vendor_bill.state,
               state = 'posted'
          FROM asset_move_line_rel rel
          JOIN account_move_line line
            ON line.id = rel.line_id
          JOIN account_asset a
            ON a.id = rel.asset_id
         WHERE vendor_bill.id = line.move_id
           AND vendor_bill.state != 'posted'
        """,
        table="account_asset",
        alias="a",
    )
    yield
    util.explode_execute(
        cr,
        """
        UPDATE account_move
           SET state = _upg_old_state
         WHERE _upg_old_state IS NOT NULL
        """,
        table="account_move",
        bucket_size=50000,
    )
    cr.execute("ALTER TABLE account_move DROP COLUMN _upg_old_state")


def migrate(cr, version):
    cr.execute(
        """
        SELECT asset.id AS asset_id,
               asset.name AS asset_name,
               array_agg(ml.id ORDER BY ml.id) FILTER (WHERE ml.credit != 0) AS credit_line_ids,
               array_agg(ml.name ORDER BY ml.id) FILTER (WHERE ml.credit != 0) AS credit_line_names
          FROM account_asset AS asset
          JOIN asset_move_line_rel AS mlr
            ON mlr.asset_id = asset.id
          JOIN account_move_line AS ml
            ON ml.id = mlr.line_id
      GROUP BY asset.id
        HAVING (sum(ml.credit) != 0 AND sum(ml.debit) != 0)
            OR sum(ml.credit + ml.debit) = 0
         """
    )
    asset_move_line_ids = cr.fetchall()
    credit_line_ids = []
    for res in asset_move_line_ids:
        credit_line_ids.extend(res[2])
    if credit_line_ids:
        if ODOO_UPG_UNLINK_CREDIT_LINES_FROM_ASSETS:
            cr.execute(
                "DELETE FROM asset_move_line_rel rel WHERE line_id IN %s",
                [tuple(credit_line_ids)],
            )
            util.add_to_migration_reports(
                """
                  <details>
                      <summary>
                          Some assets have linked journal items with positive credit.
                          Standard assets cannot be linked to journal items containing
                          credit and debit on the account or with a null amount.
                          The journal entries have been automatically unlinked from the assets.
                          Here is the list of affected records.
                      </summary>
                      <ul>{}</ul>
                      <p>
                      This automatic fix was triggered by the environment variable
                      ODOO_UPG_UNLINK_CREDIT_LINES_FROM_ASSETS=1
                      <p>
                  </details>
                """.format(
                    " ".join(
                        "<li>The asset {} was unlinked from the journal item {}</li>".format(
                            util.get_anchor_link_to_record("account.asset", asset_id, asset_name),
                            ", ".join(
                                util.get_anchor_link_to_record("account.move.line", line_id, line_name)
                                for line_id, line_name in zip(line_ids, line_names)
                            ),
                        )
                        for asset_id, asset_name, line_ids, line_names in asset_move_line_ids
                    )
                ),
                category="Assets",
                format="html",
            )
        else:
            msg = dedent("""
            Some assets have linked journal items with positive credit.
            Standard assets cannot be linked to journal items containing
            credit and debit on the account or with a null amount.
            In order to avoid the issue set the environment variable
            * ODOO_UPG_UNLINK_CREDIT_LINES_FROM_ASSETS to 1
            When this variable is set the journal entries will be unlinked
            from the assets, without removing any record.
            Here is the list of affected records:
            * {}
            """).format(
                "\n * ".join(
                    "The asset (id={}, name=`{}`) is linked to the journal item (id={}, name=`{}`).".format(
                        asset_id,
                        asset_name,
                        line_id,
                        line_name,
                    )
                    for asset_id, asset_name, line_id, line_name in asset_move_line_ids
                ),
            )
            _logger.warning("\n%s\n", msg)

    with post_moves(cr):
        util.recompute_fields(cr, "account.asset", ["non_deductible_tax_val"])
