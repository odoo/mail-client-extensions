# -*- coding: utf-8 -*-
import logging


def optimize_rules(cr, _logger):
    cr.execute(
        """
        UPDATE ir_rule
           SET domain_force = '[(''company_id'', ''in'', company_ids + [False])]'
         WHERE domain_force ~ %s
            OR domain_force ~ %s
     RETURNING id
        """,
        [
            r"\['\|',\s*\('company_id',\s*'in',\s*company_ids\),\s*\('company_id',\s*'=',\s*False\)\]",
            r"\['\|',\s*\('company_id',\s*'=',\s*False\),\s*\('company_id',\s*'in',\s*company_ids\)\]",
        ],
    )
    if cr.rowcount:
        _logger.info("Optimized %s multi-company rules", cr.rowcount)


def prepare_migration(cr):
    optimize_rules(cr, logging.getLogger(__name__))
