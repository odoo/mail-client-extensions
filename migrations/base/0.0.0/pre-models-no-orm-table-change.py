import logging
import os
from textwrap import dedent

from odoo.fields import Field

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.util.pg import _normalize_pg_type

_logger = logging.getLogger("odoo.upgrade")
MIN_VERSION = "17.0"
MAX_VERSION = "18.0"

CI = util.on_CI()
util.ENVIRON["CI_IGNORE_NO_ORM_TABLE_CHANGE"] = set()

IGNORED_MODULES = {
    exc[7:].partition(":")[0]
    for exc in os.getenv("suppress_upgrade_warnings", "").split(",")  # noqa: SIM112
    if exc.startswith("module:")
}


def migrate(cr, version):
    # NOTE: Always defined, so modules than extend this set won't have to verify the version
    util.ENVIRON["_no_orm_table_change"] = {
        "res.partner",
        "res.users",
        "ir.attachment",
    }

    if not util.version_between(MIN_VERSION, MAX_VERSION):
        return  # nosemgrep: no-early-return

    orig_update_db = Field.update_db

    def update_db(self, model, columns):
        cr = model.env.cr
        no_orm_table_change = model._name in util.ENVIRON["_no_orm_table_change"]

        col = columns.get(self.name)
        existing_type = col["udt_name"] if col else None
        if existing_type == "varchar" and col.get("character_maximum_length"):
            existing_type = "varchar({})".format(col["character_maximum_length"])
        defined_type = _normalize_pg_type(self.column_type[1].lower()) if self.column_type else None

        CRITICAL = logging.CRITICAL
        WARNING = logging.WARNING
        if CI and self._module in IGNORED_MODULES:
            CRITICAL = WARNING = util.NEARLYWARN

        if not defined_type:
            # not stored column; ignore.
            pass
        elif CI and no_orm_table_change and (model._name, self.name) in util.ENVIRON["CI_IGNORE_NO_ORM_TABLE_CHANGE"]:
            # ignored on CI
            pass
        elif existing_type:
            if existing_type != defined_type:
                if self.translate and existing_type != "jsonb":
                    func = 'convert_field_to_translatable(cr, "{}", "{}")'.format(model._name, self.name)
                elif not self.translate and existing_type == "jsonb":
                    func = 'convert_field_to_untranslatable(cr, "{}", "{}", "{}")'.format(
                        model._name, self.name, defined_type
                    )
                else:
                    func = 'alter_column_type(cr, "{}", "{}", "{}")'.format(model._table, self.name, defined_type)

                hint = dedent("""\
                    Use `util.{}` in a `pre-` upgrade script.

                    More info: https://www.odoo.com/r/upgrade-no-orm
                """).format(func)

                if no_orm_table_change:
                    _logger.log(
                        CRITICAL,
                        "Don't let the ORM change the column type of `%s.%s`.\n%s",
                        model._table,
                        self.name,
                        hint,
                    )
                else:
                    cr.execute(util.format_query(cr, "SELECT count(*) FROM {}", model._table))
                    count = cr.fetchone()[0]
                    if count > util.BIG_TABLE_THRESHOLD:
                        _logger.log(
                            WARNING,
                            "The column `%s.%s` changed type. As there are %s rows, consider writing an upgrade script.\n%s",
                            model._table,
                            self.name,
                            count,
                            hint,
                        )

        elif self.store:  # XXX can it be False if this function is called?
            # new column to create
            if self.compute:
                hint = dedent("""\
                    In a `pre-` script, use `util.create_column(cr, "{0}", "{1}", "{2}")` then
                        (1) Fill the value in SQL using `util.explode_execute(cr, query)`
                        (2) Alternatively, you can, in a `post-` or `end-` script, use `util.recompute_fields(cr, "{3}", ["{1}"])`

                    More info: https://www.odoo.com/r/upgrade-no-orm
                """).format(model._table, self.name, defined_type, model._name)

                if no_orm_table_change:
                    _logger.log(
                        CRITICAL,
                        "New computed-stored field %s/%s should be computed using an upgrade script.\n%s",
                        model._name,
                        self.name,
                        hint,
                    )
                else:
                    cr.execute(util.format_query(cr, "SELECT count(*) FROM {}", model._table))
                    count = cr.fetchone()[0]
                    if count > util.BIG_TABLE_THRESHOLD:
                        _logger.log(
                            WARNING,
                            "New computed-stored field %s/%s computed on %s records. Please consider writing an upgrade script.\n%s",
                            model._name,
                            self.name,
                            count,
                            hint,
                        )

            elif self.default:
                default = self.default
                if callable(default) and default.__qualname__ in [
                    "Field._setup_attrs.<locals>.<lambda>",
                    "Field._setup_attrs__.<locals>.<lambda>",
                ]:
                    # unwrap static value
                    default = default(model)
                def_arg = fill_sql = ""
                if callable(default):
                    fill_sql = "\nThen fill the value using a SQL query."
                else:
                    def_arg = ", default={!r}".format(default)
                hint = dedent("""\
                    Create the column in a `pre-` upgrade script using `util.create_column(cr, "{0}", "{1}", "{2}"{3})`.{4}

                    More info: https://www.odoo.com/r/upgrade-no-orm
                """).format(model._table, self.name, defined_type, def_arg, fill_sql)

                if no_orm_table_change:
                    _logger.log(
                        CRITICAL,
                        "New stored field %s/%s with default value should be handled by an upgrade script.\n%s",
                        model._name,
                        self.name,
                        hint,
                    )
                else:
                    cr.execute(util.format_query(cr, "SELECT count(*) FROM {}", model._table))
                    count = cr.fetchone()[0]
                    if count > util.BIG_TABLE_THRESHOLD:
                        _logger.log(
                            WARNING,
                            "New stored field %s/%s with default value on %s records. Please consider writing an upgrade script.\n%s",
                            model._name,
                            self.name,
                            count,
                            hint,
                        )

        return orig_update_db(self, model, columns)

    Field.update_db = update_db
