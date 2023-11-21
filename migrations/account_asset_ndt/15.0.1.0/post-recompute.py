# -*- coding: utf-8 -*-
import contextlib

from odoo.upgrade import util


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
    with post_moves(cr):
        util.recompute_fields(cr, "account.asset", ["non_deductible_tax_val"])
