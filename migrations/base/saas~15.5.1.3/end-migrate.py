# -*- coding: utf-8 -*-
import logging

from odoo.modules.db import has_trigram, has_unaccent
from odoo.tools.translate import _get_translation_upgrade_queries

from odoo.upgrade import util

_logger = logging.getLogger("odoo.upgrade.saas-15.5.1.3." + __name__)


def migrate(cr, version):
    trigram = has_trigram(cr)
    unaccent = has_unaccent(cr)
    env = util.env(cr)

    if trigram and unaccent:
        # Fix trigram index to use
        expected = [
            (
                f"{Model._table}_{field.name}_index",
                Model._table,
                field.name,
                field.index,
                getattr(field, "unaccent", False),
            )
            for Model in env.values()
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

    # backup ir_translation
    cr.execute("ALTER TABLE ir_translation RENAME TO _ir_translation")

    # upgrade translations
    cleanup_queries = []
    for Model in env.registry.values():
        if Model._auto and not Model._abstract:
            for field in Model._fields.values():
                if field.store and field.translate:
                    migrate, cleanup = _get_translation_upgrade_queries(cr, field)
                    # don't parallelize data migration queries from different
                    # fields, as it may cause serialization errors
                    util.parallel_execute(cr, migrate)
                    cleanup_queries.extend(cleanup)

    # remove translations; leftovers should be migrated manually
    cleanup_queries.append("DELETE FROM _ir_translation WHERE type = 'code'")
    util.parallel_execute(cr, cleanup_queries)

    util.remove_model(cr, "ir.translation")
