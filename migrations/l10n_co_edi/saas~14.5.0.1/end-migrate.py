# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Sql version of `_compute_edi_state` in account_edi/models/account_move.py
    cr.execute(
        """
        WITH state_per_move AS (
            SELECT
                move_id,
                ARRAY_AGG(DISTINCT state)::text[] AS states
            FROM account_edi_document
            GROUP BY move_id
        )
        UPDATE account_move
        SET edi_state = CASE
            WHEN 'to_send' = ANY(state_per_move.states) THEN 'to_send'
            WHEN 'to_cancel' = ANY(state_per_move.states) THEN 'to_cancel'
            WHEN state_per_move.states = ARRAY['sent'] THEN 'sent'
            WHEN state_per_move.states = ARRAY['cancelled'] THEN 'cancelled' END
        FROM state_per_move
        WHERE state_per_move.move_id = account_move.id
    """
    )
