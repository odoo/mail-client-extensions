# -*- coding: utf-8 -*-
import logging

from odoo.modules.db import has_trigram, has_unaccent

from odoo.upgrade import util

_logger = logging.getLogger("odoo.upgrade.saas-15.5.1.3." + __name__)


def migrate(cr, version):
    trigram = has_trigram(cr)
    unaccent = has_unaccent(cr)

    if trigram and unaccent:
        # Fix trigram index to use
        env = util.env(cr)
        expected = [
            (
                f"{Model._table}_{field.name}_index",
                Model._table,
                field.name,
                field.index,
                getattr(field, "unaccent", False),
            )
            for Model in env
            if Model._auto and not Model._abstract
            for field in Model._fields.values()
            if field.column_type and field.store and field.index == "trigram"
        ]
        if expected:
            cr.execute(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE indexname IN %s
                      AND indexdef NOT ILIKE '%%unaccent(%%'
                      AND indexdef ILIKE '%%gin_trgm_ops%%'
                """,
                [tuple(row[0] for row in expected)],
            )
            indexes_to_delete = [f'"{index_name}"' for index_name, in cr.fetchall()]
            if indexes_to_delete:
                cr.execute(f"DROP INDEX {', '.join(indexes_to_delete)}")
                _logger.info(
                    "Drop %d unusable trigram indexes (missing unaccent) and try to recreate it with unaccent",
                    len(indexes_to_delete),
                )
                env.registry.check_indexes(cr, list(env))
