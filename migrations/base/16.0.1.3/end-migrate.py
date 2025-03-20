import collections
import logging

from odoo.modules.db import has_trigram, has_unaccent
from odoo.tools.translate import _get_translation_upgrade_queries

from odoo.upgrade import util

_logger = logging.getLogger("odoo.upgrade.16.0.1.3." + __name__)


def migrate_custom_fields(cr, done, skip_models):
    cr.execute(
        """
        SELECT model,
               array_agg(name)
          FROM ir_model_fields
         WHERE store
           AND translate
           AND (model, name) NOT IN %s
           AND model != ALL(%s)
         GROUP BY model
        """,
        [tuple(done) or ("_", "_"), skip_models],
    )
    custom_fields = collections.defaultdict(list)
    for model_name, field_names in cr.fetchall():
        table = util.table_of_model(cr, model_name)
        if not util.table_exists(cr, table):
            continue
        for field in field_names:
            if util.column_type(cr, table, field) not in ("varchar", "text"):
                continue
            custom_fields[model_name].append(field)
            if util.on_CI():
                _logger.error("Attempting to modify translations for the standard field %s.%s", model_name, field)
                continue
            util.convert_field_to_translatable(cr, model_name, field)

    if not custom_fields:
        return
    msg = """
    <details>
        <summary>
        In Odoo 16 translations are stored as JSON column. Please verify the upgraded translations for custom fields.
        Since the custom code is not available during the upgrade some translations may be wrong, you should correct
        them. Below the list of affected fields by model.
        </summary>
        <ul>
            {}
        </ul>
    </details>
    """.format("\n".join("<li>{}: {}</li>".format(model, ",".join(fields)) for model, fields in custom_fields.items()))
    util.add_to_migration_reports(msg, category="Translations", format="html")


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
            indexes_to_delete = util.ColumnList.from_unquoted(cr, [index_name for (index_name,) in cr.fetchall()])
            if indexes_to_delete:
                cr.execute(util.format_query(cr, "DROP INDEX {}", indexes_to_delete))
                _logger.info(
                    "Drop %d unusable trigram indexes (missing unaccent) and try to recreate it with unaccent",
                    len(indexes_to_delete),
                )
                env.registry.check_indexes(cr, list(env))

    # backup ir_translation
    cr.execute("ALTER TABLE ir_translation RENAME TO _ir_translation")

    # upgrade translations
    cleanup_queries = []
    done = []
    skip_models = []
    for Model in env.registry.values():
        if Model._auto and not Model._abstract:
            for field in Model._fields.values():
                if field.store and field.translate:
                    done.append((Model._name, field.name))
                    if field.manual:
                        util.convert_field_to_translatable(cr, Model._name, field.name)
                    migrate, cleanup = _get_translation_upgrade_queries(cr, field)
                    # don't parallelize data migration queries from different
                    # fields, as it may cause serialization errors
                    util.parallel_execute(cr, migrate)
                    cleanup_queries.extend(cleanup)
        else:
            skip_models.append(Model._name)

    migrate_custom_fields(cr, done, skip_models)

    # remove translations; leftovers should be migrated manually
    cleanup_queries.append("DELETE FROM _ir_translation WHERE type = 'code'")
    util.parallel_execute(cr, cleanup_queries)

    util.remove_model(cr, "ir.translation")
    # avoid future FK issues
    cr.execute("ALTER TABLE _ir_translation DROP CONSTRAINT IF EXISTS ir_translation_lang_fkey_res_lang")
