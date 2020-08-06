# -*- coding: utf-8 -*-


def migrate(cr, version):

    # ===========================================================
    # account_edi + refactoring l10n_mx_edi (PR: 52407 & 12226)
    # ===========================================================

    # Sql version of `_compute_edi_state` in account_edi/models/account_move.py

    cr.execute('''
        WITH state_per_move AS (
            SELECT
                move_id,
                ARRAY_AGG(DISTINCT state) AS states
            FROM account_edi_document
            GROUP BY move_id
        )
        UPDATE account_move
        SET edi_state = CASE 
            WHEN state_per_move.states::VARCHAR[] @> '{to_send}'::VARCHAR[] THEN 'to_send'
            WHEN state_per_move.states::VARCHAR[] @> '{to_cancel}'::VARCHAR[] THEN 'to_cancel'
            WHEN state_per_move.states::VARCHAR[] = '{sent}'::VARCHAR[] THEN 'sent'
            WHEN state_per_move.states::VARCHAR[] = '{cancelled}'::VARCHAR[] THEN 'cancelled'
            ELSE NULL END
        FROM state_per_move
        WHERE state_per_move.move_id = account_move.id
    ''')
