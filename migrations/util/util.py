# -*- coding: utf-8 -*-
# Utility functions for migration scripts

import base64
import collections
import json
import logging
import os
import re
import sys
from contextlib import contextmanager
from inspect import currentframe
from operator import itemgetter

import lxml
import psycopg2

from .. import inherit
from .const import ENVIRON, NEARLYWARN
from .exceptions import SleepyDeveloperError
from .helpers import (
    _dashboard_actions,
    _ir_values_value,
    _validate_model,
    _validate_table,
    model_of_table,
    table_of_model,
)
from .misc import SelfPrintEvalContext, chunks, log_progress, version_gte
from .orm import env
from .pg import (
    _get_unique_indexes_with,
    column_exists,
    column_type,
    column_updatable,
    explode_query_range,
    get_columns,
    get_fk,
    parallel_execute,
    remove_column,
    remove_constraint,
    savepoint,
    table_exists,
    view_exists,
)
from .report import add_to_migration_reports

try:
    import odoo
    from odoo import release
except ImportError:
    import openerp as odoo
    from openerp import release


try:
    from odoo.modules.module import load_information_from_description_file
    from odoo.osv import expression
    from odoo.sql_db import db_connect
    from odoo.tools.convert import xml_import
    from odoo.tools.func import frame_codeinfo
    from odoo.tools.misc import file_open, mute_logger
    from odoo.tools.parse_version import parse_version
    from odoo.tools.safe_eval import safe_eval
except ImportError:
    from openerp.modules.module import load_information_from_description_file
    from openerp.osv import expression
    from openerp.sql_db import db_connect
    from openerp.tools.convert import xml_import
    from openerp.tools.func import frame_codeinfo
    from openerp.tools.misc import file_open, mute_logger
    from openerp.tools.parse_version import parse_version
    from openerp.tools.safe_eval import safe_eval

try:
    from odoo.api import Environment

    manage_env = Environment.manage
except ImportError:
    try:
        from openerp.api import Environment

        manage_env = Environment.manage
    except ImportError:

        @contextmanager
        def manage_env():
            yield


_logger = logging.getLogger(__name__.rpartition(".")[0])

_INSTALLED_MODULE_STATES = ("installed", "to install", "to upgrade")


# python3 shims
try:
    basestring
except NameError:
    basestring = unicode = str


def main(func, version=None):
    """a main() function for scripts"""
    # NOTE: this is not recommanded when the func callback use the ORM as the addon-path is
    # incomplete. Please pipe your script into `odoo shell`.
    # Do not forget to commit the cursor at the end.
    if len(sys.argv) != 2:
        sys.exit("Usage: %s <dbname>" % (sys.argv[0],))
    dbname = sys.argv[1]
    with db_connect(dbname).cursor() as cr, manage_env():
        func(cr, version)


def is_saas(cr):
    """Return whether the current installation has saas modules installed or not"""
    # this is shitty, I know - but the one above me is as shitty so ¯\_(ツ)_/¯
    cr.execute("SELECT true FROM ir_module_module WHERE name like 'saas_%' AND state='installed'")
    return bool(cr.fetchone())


def dbuuid(cr):
    cr.execute(
        """
        SELECT value
          FROM ir_config_parameter
         WHERE key IN ('database.uuid', 'origin.database.uuid')
      ORDER BY key DESC
         LIMIT 1
    """
    )
    return cr.fetchone()[0]


def dispatch_by_dbuuid(cr, version, callbacks):
    """
    Allow to execute a migration script for a specific database only, base on its dbuuid.
    Example:

    >>> def db_yellowbird(cr, version):
            cr.execute("DELETE FROM ir_ui_view WHERE id=837")

    >>> dispatch_by_dbuuid(cr, version, {
            'ef81c07aa90936a89f4e7878e2ebc634a24fcd66': db_yellowbird,
        })
    """
    uuid = dbuuid(cr)
    if uuid in callbacks:
        func = callbacks[uuid]
        _logger.info("calling dbuuid-specific function `%s`", func.__name__)
        func(cr, version)


IMD_FIELD_PATTERN = "field_%s__%s" if version_gte("saas~11.2") else "field_%s_%s"


def remove_view(cr, xml_id=None, view_id=None, silent=False, key=None):
    """
    Recursively delete the given view and its inherited views, as long as they
    are part of a module. Will crash as soon as a custom view exists anywhere
    in the hierarchy.

    Also handle multi-website COWed views.
    """
    assert bool(xml_id) ^ bool(view_id)
    if xml_id:
        view_id = ref(cr, xml_id)
        if view_id:
            module, _, name = xml_id.partition(".")
            cr.execute("SELECT model FROM ir_model_data WHERE module=%s AND name=%s", [module, name])

            [model] = cr.fetchone()
            if model != "ir.ui.view":
                raise ValueError("%r should point to a 'ir.ui.view', not a %r" % (xml_id, model))
    else:
        # search matching xmlid for logging or renaming of custom views
        xml_id = "?"
        if not key:
            cr.execute("SELECT module, name FROM ir_model_data WHERE model='ir.ui.view' AND res_id=%s", [view_id])
            if cr.rowcount:
                xml_id = "%s.%s" % cr.fetchone()

    # From given or determined xml_id, the views duplicated in a multi-website
    # context are to be found and removed.
    if xml_id != "?" and column_exists(cr, "ir_ui_view", "key"):
        cr.execute("SELECT id FROM ir_ui_view WHERE key = %s AND id != %s", [xml_id, view_id])
        for [v_id] in cr.fetchall():
            remove_view(cr, view_id=v_id, silent=silent, key=xml_id)

    if not view_id:
        return

    cr.execute(
        """
        SELECT v.id, x.module || '.' || x.name, v.name
        FROM ir_ui_view v LEFT JOIN
           ir_model_data x ON (v.id = x.res_id AND x.model = 'ir.ui.view' AND x.module !~ '^_')
        WHERE v.inherit_id = %s;
    """,
        [view_id],
    )
    for child_id, child_xml_id, child_name in cr.fetchall():
        if child_xml_id:
            if not silent:
                _logger.info(
                    "remove deprecated built-in view %s (ID %s) as parent view %s (ID %s) is going to be removed",
                    child_xml_id,
                    child_id,
                    xml_id,
                    view_id,
                )
            remove_view(cr, child_xml_id, silent=True)
        else:
            if not silent:
                _logger.warning(
                    "deactivate deprecated custom view with ID %s as parent view %s (ID %s) is going to be removed",
                    child_id,
                    xml_id,
                    view_id,
                )
            disable_view_query = """
                UPDATE ir_ui_view
                SET name = (name || ' - old view, inherited from ' || %%s),
                    model = (model || '.disabled'),
                    inherit_id = NULL
                    %s
                    WHERE id = %%s
            """
            # In 8.0, disabling requires setting mode to 'primary'
            extra_set_sql = ""
            if column_exists(cr, "ir_ui_view", "mode"):
                extra_set_sql = ",  mode = 'primary' "

            disable_view_query = disable_view_query % extra_set_sql
            cr.execute(disable_view_query, (key or xml_id, child_id))
            add_to_migration_reports(
                {"id": child_id, "name": child_name},
                "Disabled views",
            )
    if not silent:
        _logger.info("remove deprecated %s view %s (ID %s)", key and "COWed" or "built-in", key or xml_id, view_id)

    _remove_records(cr, "ir.ui.view", [view_id])


@contextmanager
def edit_view(cr, xmlid=None, view_id=None, skip_if_not_noupdate=True):
    """Contextmanager that may yield etree arch of a view.
    As it may not yield, you must use `skippable_cm`

        with util.skippable_cm(), util.edit_view(cr, 'xml.id') as arch:
            arch.attrib['string'] = 'My Form'
    """
    assert bool(xmlid) ^ bool(view_id), "You Must specify either xmlid or view_id"
    noupdate = True
    if xmlid:
        if "." not in xmlid:
            raise ValueError("Please use fully qualified name <module>.<name>")

        module, _, name = xmlid.partition(".")
        cr.execute(
            """
                SELECT res_id, noupdate
                  FROM ir_model_data
                 WHERE module = %s
                   AND name = %s
        """,
            [module, name],
        )
        data = cr.fetchone()
        if data:
            view_id, noupdate = data

    if view_id and not (skip_if_not_noupdate and not noupdate):
        arch_col = "arch_db" if column_exists(cr, "ir_ui_view", "arch_db") else "arch"
        cr.execute(
            """
                SELECT {arch}
                  FROM ir_ui_view
                 WHERE id=%s
            """.format(
                arch=arch_col
            ),
            [view_id],
        )
        [arch] = cr.fetchone() or [None]
        if arch:
            if isinstance(arch, unicode):
                arch = arch.encode("utf-8")
            arch = lxml.etree.fromstring(arch)
            yield arch
            cr.execute(
                "UPDATE ir_ui_view SET {arch}=%s WHERE id=%s".format(arch=arch_col),
                [lxml.etree.tostring(arch, encoding="unicode"), view_id],
            )


def add_view(cr, name, model, view_type, arch_db, inherit_xml_id=None, priority=16):
    inherit_id = False
    if inherit_xml_id:
        inherit_id = ref(cr, inherit_xml_id)
        if not inherit_id:
            raise ValueError(
                "Unable to add view '%s' because its inherited view '%s' cannot be found!" % (name, inherit_xml_id)
            )
    arch_col = "arch_db" if column_exists(cr, "ir_ui_view", "arch_db") else "arch"
    cr.execute(
        """
        INSERT INTO ir_ui_view(name, "type",  model, inherit_id, mode, active, priority, %s)
        VALUES(%%(name)s, %%(view_type)s, %%(model)s, %%(inherit_id)s, %%(mode)s, 't', %%(priority)s, %%(arch_db)s)
    """
        % arch_col,
        {
            "name": name,
            "view_type": view_type,
            "model": model,
            "inherit_id": inherit_id,
            "mode": "extension" if inherit_id else "primary",
            "priority": priority,
            "arch_db": arch_db,
        },
    )


# fmt:off
if version_gte("saas~14.3"):
    def remove_asset(cr, name):
        cr.execute("SELECT id FROM ir_asset WHERE bundle = %s", [name])
        if cr.rowcount:
            _remove_records(cr, "ir.asset", [aid for aid, in cr.fetchall()])
else:
    def remove_asset(cr, name):
        remove_view(cr, name, silent=True)
# fmt:on


def remove_record(cr, name, deactivate=False, active_field="active"):
    if isinstance(name, basestring):
        if "." not in name:
            raise ValueError("Please use fully qualified name <module>.<name>")
        module, _, name = name.partition(".")
        cr.execute(
            """
                DELETE
                  FROM ir_model_data
                 WHERE module = %s
                   AND name = %s
             RETURNING model, res_id
        """,
            [module, name],
        )
        data = cr.fetchone()
        if not data:
            return
        model, res_id = data
    elif isinstance(name, tuple):
        if len(name) != 2:
            raise ValueError("Please use a 2-tuple (<model>, <res_id>)")
        model, res_id = name
    else:
        raise ValueError("Either use a fully qualified xmlid string <module>.<name> or a 2-tuple (<model>, <res_id>)")

    # deleguate to the right method
    if model == "ir.ui.view":
        _logger.log(NEARLYWARN, "Removing view %r", name)
        return remove_view(cr, view_id=res_id)

    if model == "ir.ui.menu":
        _logger.log(NEARLYWARN, "Removing menu %r", name)
        return remove_menus(cr, [res_id])

    return _remove_records(cr, model, [res_id], deactivate=deactivate, active_field=active_field)


def _remove_records(cr, model, ids, deactivate=False, active_field="active"):
    if not ids:
        return

    ids = tuple(ids)

    for inh in _for_each_inherit(cr, model, skip=()):
        if inh.via:
            table = table_of_model(cr, inh.model)
            if not column_exists(cr, table, inh.via):
                # column may not exists in case of a partially unintalled module that left only *magic columns* in tables
                continue
            cr.execute('SELECT id FROM "{}" WHERE "{}" IN %s'.format(table, inh.via), [ids])
            if inh.model == "ir.ui.menu":
                remove_menus(cr, [menu_id for menu_id, in cr.fetchall()])
            elif inh.model == "ir.ui.view":
                for (view_id,) in cr.fetchall():
                    remove_view(cr, view_id=view_id)
            else:
                _remove_records(cr, inh.model, [rid for rid, in cr.fetchall()])

    table = table_of_model(cr, model)
    try:
        with savepoint(cr):
            cr.execute('DELETE FROM "{}" WHERE id IN %s'.format(table), [ids])
    except Exception:
        if not deactivate or not active_field:
            raise
        cr.execute('UPDATE "{}" SET "{}" = false WHERE id IN %s'.format(table, active_field), [ids])
    else:
        for ir in indirect_references(cr, bound_only=True):
            query = 'DELETE FROM "{}" WHERE {} AND "{}" IN %s'.format(ir.table, ir.model_filter(), ir.res_id)
            cr.execute(query, [model, ids])
        _rm_refs(cr, model, ids)

    if model == "res.groups":
        # A group is gone, the auto-generated view `base.user_groups_view` is outdated.
        # Create a shim. It will be re-generated later by creating/updating groups or
        # explicitly in `base/0.0.0/end-user_groups_view.py`.
        arch_col = "arch_db" if column_exists(cr, "ir_ui_view", "arch_db") else "arch"
        cr.execute(
            "UPDATE ir_ui_view SET {} = '<form/>' WHERE id = %s".format(arch_col), [ref(cr, "base.user_groups_view")]
        )


def if_unchanged(cr, xmlid, callback, interval="1 minute"):
    assert "." in xmlid
    module, _, name = xmlid.partition(".")
    cr.execute("SELECT model, res_id FROM ir_model_data WHERE module=%s AND name=%s", [module, name])
    data = cr.fetchone()
    if not data:
        return
    model, res_id = data
    table = table_of_model(cr, model)
    cr.execute(
        """
        SELECT 1
          FROM {}
         WHERE id = %s
           -- Note: use a negative search to handle the case of NULL values in write/create_date
           AND write_date - create_date > interval %s
    """.format(
            table
        ),
        [res_id, interval],
    )
    if not cr.rowcount:
        callback(cr, xmlid)


def remove_menus(cr, menu_ids):
    if not menu_ids:
        return
    cr.execute(
        """
        WITH RECURSIVE tree(id) AS (
            SELECT id
              FROM ir_ui_menu
             WHERE id IN %s
             UNION
            SELECT m.id
              FROM ir_ui_menu m
              JOIN tree t ON (m.parent_id = t.id)
        )
        DELETE FROM ir_ui_menu m
              USING tree t
              WHERE m.id = t.id
          RETURNING m.id
    """,
        [tuple(menu_ids)],
    )
    ids = tuple(x[0] for x in cr.fetchall())
    if ids:
        cr.execute("DELETE FROM ir_model_data WHERE model='ir.ui.menu' AND res_id IN %s", [ids])


def rename_xmlid(cr, old, new, noupdate=None):
    if "." not in old or "." not in new:
        raise ValueError("Please use fully qualified name <module>.<name>")

    old_module, _, old_name = old.partition(".")
    new_module, _, new_name = new.partition(".")
    nu = "" if noupdate is None else (", noupdate=" + str(bool(noupdate)).lower())
    cr.execute(
        """UPDATE ir_model_data
                     SET module=%s, name=%s
                         {}
                   WHERE module=%s AND name=%s
               RETURNING model, res_id
               """.format(
            nu
        ),
        (new_module, new_name, old_module, old_name),
    )
    data = cr.fetchone()
    if data:
        model, rid = data
        if model == "ir.ui.view" and column_exists(cr, "ir_ui_view", "key"):
            cr.execute("UPDATE ir_ui_view SET key=%s WHERE id=%s AND key=%s", [new, rid, old])
            if cr.rowcount:
                # iif the key has been updated for this view, also update it for all other cowed views.
                # Don't change the view keys inconditionally to avoid changing unrelated views.
                cr.execute("UPDATE ir_ui_view SET key = %s WHERE key = %s", [new, old])
        return rid
    return None


def ref(cr, xmlid):
    if "." not in xmlid:
        raise ValueError("Please use fully qualified name <module>.<name>")

    module, _, name = xmlid.partition(".")
    cr.execute(
        """
            SELECT res_id
              FROM ir_model_data
             WHERE module = %s
               AND name = %s
    """,
        [module, name],
    )
    data = cr.fetchone()
    if data:
        return data[0]
    return None


def force_noupdate(cr, xmlid, noupdate=True, warn=False):
    if "." not in xmlid:
        raise ValueError("Please use fully qualified name <module>.<name>")

    module, _, name = xmlid.partition(".")
    cr.execute(
        """
            UPDATE ir_model_data
               SET noupdate = %s
             WHERE module = %s
               AND name = %s
               AND noupdate != %s
    """,
        [noupdate, module, name, noupdate],
    )
    if noupdate is False and cr.rowcount and warn:
        _logger.warning("Customizations on `%s` might be lost!", xmlid)
    return cr.rowcount


def ensure_xmlid_match_record(cr, xmlid, model, values):
    if "." not in xmlid:
        raise ValueError("Please use fully qualified name <module>.<name>")

    module, _, name = xmlid.partition(".")
    cr.execute(
        """
            SELECT id, res_id
              FROM ir_model_data
             WHERE module = %s
               AND name = %s
    """,
        [module, name],
    )

    table = table_of_model(cr, model)
    data = cr.fetchone()
    if data:
        data_id, res_id = data
        # check that record still exists
        cr.execute("SELECT id FROM %s WHERE id=%%s" % table, (res_id,))
        if cr.fetchone():
            return res_id
    else:
        data_id = None

    # search for existing record marching values
    where = []
    data = ()
    for k, v in values.items():
        if v:
            where += ["%s = %%s" % (k,)]
            data += (v,)
        else:
            where += ["%s IS NULL" % (k,)]
            data += ()

    query = ("SELECT id FROM %s WHERE " % table) + " AND ".join(where)
    cr.execute(query, data)
    record = cr.fetchone()
    if not record:
        return None

    res_id = record[0]

    if data_id:
        cr.execute(
            """
                UPDATE ir_model_data
                   SET res_id=%s
                 WHERE id=%s
        """,
            [res_id, data_id],
        )
    else:
        cr.execute(
            """
                INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
                     VALUES (%s, %s, %s, %s, %s)
        """,
            [module, name, model, res_id, True],
        )

    return res_id


def update_record_from_xml(cr, xmlid, reset_write_metadata=True, force_create=False, from_module=None):
    # Force update of a record from xml file to bypass the noupdate flag
    if "." not in xmlid:
        raise ValueError("Please use fully qualified name <module>.<name>")

    module, _, name = xmlid.partition(".")

    cr.execute(
        """
        UPDATE ir_model_data d
           SET noupdate = false
          FROM ir_model_data o
         WHERE o.id = d.id
           AND d.module = %s
           AND d.name = %s
     RETURNING d.model, d.res_id, o.noupdate
    """,
        [module, name],
    )
    if cr.rowcount:
        model, res_id, noupdate = cr.fetchone()
    elif not force_create:
        return
    else:
        # The xmlid doesn't already exists, nothing to reset
        reset_write_metadata = noupdate = False

    write_data = None
    if reset_write_metadata:
        table = table_of_model(cr, model)
        cr.execute("SELECT write_uid, write_date, id FROM {} WHERE id=%s".format(table), [res_id])
        write_data = cr.fetchone()

    xpath = "//*[@id='{module}.{name}' or @id='{name}']".format(module=module, name=name)
    # use a data tag inside openerp tag to be compatible with all supported versions
    new_root = lxml.etree.fromstring("<openerp><data/></openerp>")

    from_module = from_module or module
    manifest = load_information_from_description_file(from_module)
    for f in manifest.get("data", []):
        if not f.endswith(".xml"):
            continue
        with file_open(os.path.join(from_module, f)) as fp:
            doc = lxml.etree.parse(fp)
            for node in doc.xpath(xpath):
                new_root[0].append(node)

    importer = xml_import(cr, from_module, idref={}, mode="update")
    kw = dict(mode="update") if parse_version("8.0") <= parse_version(release.series) <= parse_version("12.0") else {}
    importer.parse(new_root, **kw)

    if noupdate:
        force_noupdate(cr, xmlid, True)
    if reset_write_metadata and write_data:
        cr.execute("UPDATE {} SET write_uid=%s, write_date=%s WHERE id=%s".format(table), write_data)


def ensure_m2o_func_field_data(cr, src_table, column, dst_table):
    """
    Fix broken m2o relations.
    If any `column` not present in `dst_table`, remove column from `src_table` in
    order to force recomputation of the function field

    WARN: only call this method on m2o function/related fields!!
    """
    if not column_exists(cr, src_table, column):
        return
    cr.execute(
        """
            SELECT count(1)
              FROM "{src_table}"
             WHERE "{column}" NOT IN (SELECT id FROM "{dst_table}")
        """.format(
            src_table=src_table, column=column, dst_table=dst_table
        )
    )
    if cr.fetchone()[0]:
        remove_column(cr, src_table, column, cascade=True)


def uniq_tags(cr, model, uniq_column="name", order="id"):
    """
    Deduplicated "tag" models entries.
    In standard, should only be referenced as many2many
    But with a customization, could be referenced as many2one

    By using `uniq_column=lower(name)` and `order=name`
    you can prioritize tags in CamelCase/UPPERCASE.
    """
    table = table_of_model(cr, model)
    upds = []
    for ft, fc, _, da in get_fk(cr, table):
        cols = get_columns(cr, ft, ignore=(fc,))[0]
        is_many2one = False
        is_many2many = da == "c" and len(cols) == 1  # if ondelete=cascade fk and only 2 columns, it's a m2m
        if not is_many2many:
            cr.execute("SELECT count(*) FROM ir_model_fields WHERE ttype = 'many2many' AND relation_table = %s", [ft])
            [is_many2many] = cr.fetchone()
        if not is_many2many:
            model = model_of_table(cr, ft)
            if model:
                cr.execute(
                    """
                        SELECT count(*)
                          FROM ir_model_fields
                         WHERE model = %s
                           AND name = %s
                           AND ttype = 'many2one'
                    """,
                    [model, fc],
                )
                [is_many2one] = cr.fetchone()
        assert (
            is_many2many or is_many2one
        ), "Can't determine if column `%s` of table `%s` is a many2one or many2many" % (fc, ft)
        if is_many2many:
            upds.append(
                """
                INSERT INTO {rel}({c1}, {c2})
                     SELECT r.{c1}, d.id
                       FROM {rel} r
                       JOIN dups d ON (r.{c2} = ANY(d.others))
                     EXCEPT
                     SELECT r.{c1}, r.{c2}
                       FROM {rel} r
                       JOIN dups d ON (r.{c2} = d.id)
            """.format(
                    rel=ft, c1=cols[0], c2=fc
                )
            )
        else:
            upds.append(
                """
                    UPDATE {rel} r
                       SET {c} = d.id
                      FROM dups d
                     WHERE r.{c} = ANY(d.others)
                """.format(
                    rel=ft, c=fc
                )
            )

    assert upds  # if not m2m found, there is something wrong...

    updates = ",".join("_upd_%s AS (%s)" % x for x in enumerate(upds))
    query = """
        WITH dups AS (
            SELECT (array_agg(id order by {order}))[1] as id,
                   (array_agg(id order by {order}))[2:array_length(array_agg(id), 1)] as others
              FROM {table}
          GROUP BY {uniq_column}
            HAVING count(id) > 1
        ),
        _upd_imd AS (
            UPDATE ir_model_data x
               SET res_id = d.id
              FROM dups d
             WHERE x.model = %s
               AND x.res_id = ANY(d.others)
        ),
        {updates}
        DELETE FROM {table} WHERE id IN (SELECT unnest(others) FROM dups)
    """.format(
        **locals()
    )

    cr.execute(query, [model])


def delete_unused(cr, *xmlids):
    select_xids = " UNION ".join(
        [
            cr.mogrify("SELECT %s::varchar as module, %s::varchar as name", [module, name]).decode()
            for xmlid in xmlids
            for module, _, name in [xmlid.partition(".")]
        ]
    )

    cr.execute(
        """
       WITH xids AS (
         {}
       ),
       _upd AS (
            UPDATE ir_model_data d
               SET noupdate = true
              FROM xids x
             WHERE d.module = x.module
               AND d.name = x.name
         RETURNING d.id, d.model, d.res_id, d.module || '.' || d.name as xmlid
       )
       SELECT model, array_agg(res_id ORDER BY id), array_agg(xmlid ORDER BY id)
         FROM _upd
     GROUP BY model
    """.format(
            select_xids
        )
    )

    deleted = []
    for model, ids, xmlids in cr.fetchall():
        table = table_of_model(cr, model)
        res_id_to_xmlid = dict(zip(ids, xmlids))

        sub = " UNION ".join(
            [
                'SELECT 1 FROM "{}" x WHERE x."{}" = t.id'.format(fk_tbl, fk_col)
                for fk_tbl, fk_col, _, fk_act in get_fk(cr, table, quote_ident=False)
                # ignore "on delete cascade" fk (they are indirect dependencies (lines or m2m))
                if fk_act != "c"
                # ignore children records unless the deletion is restricted
                if not (fk_tbl == table and fk_act != "r")
            ]
        )
        if sub:
            cr.execute(
                """
                SELECT id
                  FROM "{}" t
                 WHERE id = ANY(%s)
                   AND NOT EXISTS({})
            """.format(
                    table, sub
                ),
                [list(ids)],
            )
            ids = map(itemgetter(0), cr.fetchall())

        ids = list(ids)
        if model == "res.lang":
            cr.execute(
                """
                DELETE FROM ir_translation t
                      USING res_lang l
                      WHERE t.lang = l.code
                        AND l.id = ANY(%s)
                 """,
                [ids],
            )
        for tid in ids:
            remove_record(cr, (model, tid))
            deleted.append(res_id_to_xmlid[tid])

    return deleted


def modules_installed(cr, *modules):
    """return True if all `modules` are (about to be) installed"""
    assert modules
    cr.execute(
        """
            SELECT count(1)
              FROM ir_module_module
             WHERE name IN %s
               AND state IN %s
    """,
        [modules, _INSTALLED_MODULE_STATES],
    )
    return cr.fetchone()[0] == len(modules)


def module_installed(cr, module):
    return modules_installed(cr, module)


def uninstall_module(cr, module):

    cr.execute("SELECT id FROM ir_module_module WHERE name=%s", (module,))
    (mod_id,) = cr.fetchone() or [None]
    if not mod_id:
        return

    # delete constraints only owned by this module
    cr.execute(
        """
            SELECT name
              FROM ir_model_constraint
          GROUP BY name
            HAVING array_agg(module) = %s
    """,
        ([mod_id],),
    )

    constraints = tuple(map(itemgetter(0), cr.fetchall()))
    if constraints:
        cr.execute(
            """
                SELECT table_name, constraint_name
                  FROM information_schema.table_constraints
                 WHERE constraint_name IN %s
        """,
            [constraints],
        )
        for table, constraint in cr.fetchall():
            cr.execute('ALTER TABLE "%s" DROP CONSTRAINT "%s"' % (table, constraint))

    cr.execute(
        """
            DELETE
              FROM ir_model_constraint
             WHERE module = %s
    """,
        [mod_id],
    )

    # delete data
    model_ids, field_ids, menu_ids = [], [], []
    cr.execute(
        """
            SELECT model, res_id
              FROM ir_model_data d
             WHERE NOT EXISTS (SELECT 1
                                 FROM ir_model_data
                                WHERE id != d.id
                                  AND res_id = d.res_id
                                  AND model = d.model
                                  AND module != d.module)
               AND module = %s
               AND model != 'ir.module.module'
          ORDER BY id DESC
    """,
        [module],
    )
    for model, res_id in cr.fetchall():
        if model == "ir.model":
            model_ids.append(res_id)
        elif model == "ir.model.fields":
            field_ids.append(res_id)
        elif model == "ir.ui.menu":
            menu_ids.append(res_id)
        elif model == "ir.ui.view":
            remove_view(cr, view_id=res_id, silent=True)
        else:
            remove_record(cr, (model, res_id))

    if menu_ids:
        remove_menus(cr, menu_ids)

    # remove relations
    cr.execute(
        """
            SELECT name
              FROM ir_model_relation
          GROUP BY name
            HAVING array_agg(module) = %s
    """,
        ([mod_id],),
    )
    relations = tuple(map(itemgetter(0), cr.fetchall()))
    cr.execute("DELETE FROM ir_model_relation WHERE module=%s", (mod_id,))
    if relations:
        cr.execute("SELECT table_name FROM information_schema.tables WHERE table_name IN %s", (relations,))
        for (rel,) in cr.fetchall():
            cr.execute('DROP TABLE "%s" CASCADE' % (rel,))

    if model_ids:
        cr.execute("SELECT model FROM ir_model WHERE id IN %s", [tuple(model_ids)])
        for (model,) in cr.fetchall():
            delete_model(cr, model)

    if field_ids:
        cr.execute("SELECT model, name FROM ir_model_fields WHERE id IN %s", [tuple(field_ids)])
        for model, name in cr.fetchall():
            remove_field(cr, model, name)

    cr.execute("DELETE FROM ir_model_data WHERE model='ir.module.module' AND res_id=%s", [mod_id])
    cr.execute("DELETE FROM ir_model_data WHERE module=%s", (module,))
    cr.execute("DELETE FROM ir_translation WHERE module=%s", [module])
    cr.execute("UPDATE ir_module_module SET state='uninstalled' WHERE name=%s", (module,))


def uninstall_theme(cr, theme, base_theme=None):
    """Uninstalls a theme module (see uninstall_module) and removes it from the
    related websites.
    Beware that this utility function can only be called in post-* scripts.
    """
    cr.execute("SELECT id FROM ir_module_module WHERE name=%s AND state in %s", [theme, _INSTALLED_MODULE_STATES])
    (theme_id,) = cr.fetchone() or [None]
    if not theme_id:
        return

    env_ = env(cr)
    IrModuleModule = env_["ir.module.module"]
    if base_theme:
        cr.execute("SELECT id FROM ir_module_module WHERE name=%s", (base_theme,))
        (website_theme_id,) = cr.fetchone() or [None]
        theme_extension = IrModuleModule.browse(theme_id)
        for website in env_["website"].search([("theme_id", "=", website_theme_id)]):
            theme_extension._theme_unload(website)
    else:
        websites = env_["website"].search([("theme_id", "=", theme_id)])
        for website in websites:
            IrModuleModule._theme_remove(website)
    env_["base"].flush()
    uninstall_module(cr, theme)


def remove_module(cr, module):
    """Uninstall the module and delete references to it
    Ensure to reassign records before calling this method
    """
    # NOTE: we cannot use the uninstall of module because the given
    # module need to be currently installed and running as deletions
    # are made using orm.

    uninstall_module(cr, module)
    cr.execute("DELETE FROM ir_module_module WHERE name=%s", (module,))
    cr.execute("DELETE FROM ir_module_module_dependency WHERE name=%s", (module,))


def remove_theme(cr, theme, base_theme=None):
    """See remove_module. Beware that removing a theme must be done in post-*
    scripts.
    """
    uninstall_theme(cr, theme, base_theme=base_theme)
    cr.execute("DELETE FROM ir_module_module WHERE name=%s", (theme,))
    cr.execute("DELETE FROM ir_module_module_dependency WHERE name=%s", (theme,))


def _update_view_key(cr, old, new):
    # update view key for renamed & merged modules
    if not column_exists(cr, "ir_ui_view", "key"):
        return
    cr.execute(
        """
        UPDATE ir_ui_view v
           SET key = CONCAT(%s, '.', x.name)
          FROM ir_model_data x
         WHERE x.model = 'ir.ui.view'
           AND x.res_id = v.id
           AND x.module = %s
           AND v.key = CONCAT(x.module, '.', x.name)
    """,
        [new, old],
    )


def rename_module(cr, old, new):
    cr.execute("UPDATE ir_module_module SET name=%s WHERE name=%s", (new, old))
    cr.execute("UPDATE ir_module_module_dependency SET name=%s WHERE name=%s", (new, old))
    _update_view_key(cr, old, new)
    cr.execute("UPDATE ir_model_data SET module=%s WHERE module=%s", (new, old))
    cr.execute("UPDATE ir_translation SET module=%s WHERE module=%s", [new, old])

    mod_old = "module_" + old
    mod_new = "module_" + new
    cr.execute(
        """
            UPDATE ir_model_data
               SET name = %s
             WHERE name = %s
               AND module = %s
               AND model = %s
    """,
        [mod_new, mod_old, "base", "ir.module.module"],
    )


def merge_module(cr, old, into, without_deps=False):
    """Move all references of module `old` into module `into`"""
    cr.execute("SELECT name, id FROM ir_module_module WHERE name IN %s", [(old, into)])
    mod_ids = dict(cr.fetchall())

    if old not in mod_ids:
        # this can happen in case of temp modules added after a release if the database does not
        # know about this module, i.e: account_full_reconcile in 9.0
        # `into` should be know. Let it crash if not
        _logger.log(NEARLYWARN, "Unknow module %s. Skip merge into %s.", old, into)
        return

    def _up(table, old, new):
        cr.execute(
            """
                UPDATE ir_model_{0} x
                   SET module=%s
                 WHERE module=%s
                   AND NOT EXISTS(SELECT 1
                                    FROM ir_model_{0} y
                                   WHERE y.name = x.name
                                     AND y.module = %s)
        """.format(
                table
            ),
            [new, old, new],
        )

        if table == "data":
            cr.execute(
                """
                SELECT model, array_agg(res_id)
                  FROM ir_model_data
                 WHERE module=%s
                   AND model NOT LIKE 'ir.model%%'
                   AND model NOT LIKE 'ir.module.module%%'
              GROUP BY model
            """,
                [old],
            )
            for model, res_ids in cr.fetchall():
                if model == "ir.ui.view":
                    for v in res_ids:
                        remove_view(cr, view_id=v, silent=True)
                elif model == "ir.ui.menu":
                    remove_menus(cr, tuple(res_ids))
                else:
                    for r in res_ids:
                        remove_record(cr, (model, r))

        cr.execute("DELETE FROM ir_model_{0} WHERE module=%s".format(table), [old])

    _up("constraint", mod_ids[old], mod_ids[into])
    _up("relation", mod_ids[old], mod_ids[into])
    _update_view_key(cr, old, into)
    _up("data", old, into)
    cr.execute("UPDATE ir_translation SET module=%s WHERE module=%s", [into, old])

    # update dependencies
    if not without_deps:
        cr.execute(
            """
            INSERT INTO ir_module_module_dependency(module_id, name)
            SELECT module_id, %s
              FROM ir_module_module_dependency d
             WHERE name=%s
               AND NOT EXISTS(SELECT 1
                                FROM ir_module_module_dependency o
                               WHERE o.module_id = d.module_id
                                 AND o.name=%s)
        """,
            [into, old, into],
        )

    cr.execute("DELETE FROM ir_module_module WHERE name=%s RETURNING state", [old])
    [state] = cr.fetchone()
    cr.execute("DELETE FROM ir_module_module_dependency WHERE name=%s", [old])
    cr.execute("DELETE FROM ir_model_data WHERE model='ir.module.module' AND res_id=%s", [mod_ids[old]])
    if state in _INSTALLED_MODULE_STATES:
        force_install_module(cr, into)


def force_install_module(cr, module, if_installed=None):
    subquery = ""
    subparams = ()
    if if_installed:
        subquery = """AND EXISTS(SELECT 1 FROM ir_module_module
                                  WHERE name IN %s
                                    AND state IN %s)"""
        subparams = (tuple(if_installed), _INSTALLED_MODULE_STATES)

    cr.execute(
        """
        WITH RECURSIVE deps (mod_id, dep_name) AS (
              SELECT m.id, d.name from ir_module_module_dependency d
              JOIN ir_module_module m on (d.module_id = m.id)
              WHERE m.name = %s
            UNION
              SELECT m.id, d.name from ir_module_module m
              JOIN deps ON deps.dep_name = m.name
              JOIN ir_module_module_dependency d on (d.module_id = m.id)
        )
        UPDATE ir_module_module m
           SET state = CASE WHEN state = 'to remove' THEN 'to upgrade'
                            WHEN state = 'uninstalled' THEN 'to install'
                            ELSE state
                       END,
               demo=(select demo from ir_module_module where name='base')
          FROM deps d
         WHERE m.id = d.mod_id
           {0}
     RETURNING m.name, m.state
    """.format(
            subquery
        ),
        (module,) + subparams,
    )

    states = dict(cr.fetchall())
    # auto_install modules...
    toinstall = [m for m in states if states[m] == "to install"]
    if toinstall:
        # Same algo as ir.module.module.button_install(): https://git.io/fhCKd
        dep_match = ""
        if column_exists(cr, "ir_module_module_dependency", "auto_install_required"):
            dep_match = "AND d.auto_install_required = TRUE AND e.auto_install_required = TRUE"

        cr.execute(
            """
            SELECT on_me.name
              FROM ir_module_module_dependency d
              JOIN ir_module_module on_me ON on_me.id = d.module_id
              JOIN ir_module_module_dependency e ON e.module_id = on_me.id
              JOIN ir_module_module its_deps ON its_deps.name = e.name
             WHERE d.name = ANY(%s)
               AND on_me.state = 'uninstalled'
               AND on_me.auto_install = TRUE
               {}
          GROUP BY on_me.name
            HAVING
                   -- are all dependencies (to be) installed?
                   array_agg(its_deps.state)::text[] <@ %s
        """.format(
                dep_match
            ),
            [toinstall, list(_INSTALLED_MODULE_STATES)],
        )
        for (mod,) in cr.fetchall():
            _logger.debug("auto install module %r due to module %r being force installed", mod, module)
            force_install_module(cr, mod)

    # TODO handle module exclusions

    return states.get(module)


def _assert_modules_exists(cr, *modules):
    assert modules
    cr.execute("SELECT name FROM ir_module_module WHERE name IN %s", [modules])
    existing_modules = {m[0] for m in cr.fetchall()}
    unexisting_modules = set(modules) - existing_modules
    if unexisting_modules:
        raise AssertionError("Unexisting modules: {}".format(", ".join(unexisting_modules)))


def new_module_dep(cr, module, new_dep):
    assert isinstance(new_dep, basestring)
    _assert_modules_exists(cr, module, new_dep)
    # One new dep at a time
    cr.execute(
        """
            INSERT INTO ir_module_module_dependency(name, module_id)
                       SELECT %s, id
                         FROM ir_module_module m
                        WHERE name=%s
                          AND NOT EXISTS(SELECT 1
                                           FROM ir_module_module_dependency
                                          WHERE module_id = m.id
                                            AND name=%s)
    """,
        [new_dep, module, new_dep],
    )

    # Update new_dep state depending on module state
    cr.execute("SELECT state FROM ir_module_module WHERE name = %s", [module])
    mod_state = (cr.fetchone() or ["n/a"])[0]
    if mod_state in _INSTALLED_MODULE_STATES:
        # Module was installed, need to install all its deps, recursively,
        # to make sure the new dep is installed
        force_install_module(cr, module)


def remove_module_deps(cr, module, old_deps):
    assert isinstance(old_deps, (collections.Sequence, collections.Set)) and not isinstance(old_deps, basestring)
    # As the goal is to have dependencies removed, the objective is reached even when they don't exist.
    # Therefore, we don't need to assert their existence (at the cost of missing typos).
    cr.execute(
        """
            DELETE
              FROM ir_module_module_dependency
             WHERE module_id = (SELECT id
                                  FROM ir_module_module
                                 WHERE name = %s)
               AND name IN %s
    """,
        [module, tuple(old_deps)],
    )


def module_deps_diff(cr, module, plus=(), minus=()):
    for new_dep in plus:
        new_module_dep(cr, module, new_dep)
    if minus:
        remove_module_deps(cr, module, tuple(minus))


def module_auto_install(cr, module, auto_install):
    if column_exists(cr, "ir_module_module_dependency", "auto_install_required"):
        params = []
        if auto_install is True:
            value = "TRUE"
        elif auto_install:
            value = "(name = ANY(%s))"
            params = [list(auto_install)]
        else:
            value = "FALSE"

        cr.execute(
            """
            UPDATE ir_module_module_dependency
               SET auto_install_required = {}
             WHERE module_id = (SELECT id
                                  FROM ir_module_module
                                 WHERE name = %s)
        """.format(
                value
            ),
            params + [module],
        )

    cr.execute("UPDATE ir_module_module SET auto_install = %s WHERE name = %s", [auto_install is not False, module])


def new_module(cr, module, deps=(), auto_install=False):
    if deps:
        _assert_modules_exists(cr, *deps)

    cr.execute("SELECT count(1) FROM ir_module_module WHERE name = %s", [module])
    if cr.fetchone()[0]:
        # Avoid duplicate entries for module which is already installed,
        # even before it has become standard module in new version
        # Also happen for modules added afterward, which should be added by multiple series.
        return

    if deps and auto_install and not module.startswith("test_"):
        to_check = deps if auto_install is True else auto_install
        state = "to install" if modules_installed(cr, *to_check) else "uninstalled"
    else:
        state = "uninstalled"
    cr.execute(
        """
        INSERT INTO ir_module_module (name, state, demo)
             VALUES (%s, %s, (SELECT demo FROM ir_module_module WHERE name='base'))
          RETURNING id
    """,
        [module, state],
    )
    (new_id,) = cr.fetchone()

    cr.execute(
        """
        INSERT INTO ir_model_data (name, module, noupdate, model, res_id)
             VALUES ('module_'||%s, 'base', 't', 'ir.module.module', %s)
    """,
        [module, new_id],
    )

    for dep in deps:
        new_module_dep(cr, module, dep)

    module_auto_install(cr, module, auto_install)


def force_migration_of_fresh_module(cr, module, init=True):
    """It may appear that new (or forced installed) modules need a migration script to grab data
    form other module. (we cannot add a pre-init hook on the fly)

    Being in init mode may make sens in some situations (when?) but has the nasty side effect
    of not respecting noupdate flags (in xml file nor in ir_model_data) which can be quite
    problematic
    """
    filename, _ = frame_codeinfo(currentframe(), 1)
    version = ".".join(filename.split(os.path.sep)[-2].split(".")[:2])

    # Force module state to be in `to upgrade`.
    # Needed for migration script execution. See http://git.io/vnF7f
    cr.execute(
        """
            UPDATE ir_module_module
               SET state='to upgrade',
                   latest_version=%s
             WHERE name=%s
               AND state='to install'
         RETURNING id
    """,
        [version, module],
    )
    if init and cr.rowcount:
        # Force module in `init` mode beside its state is forced to `to upgrade`
        # See http://git.io/vnF7O
        odoo.tools.config["init"][module] = "oh yeah!"


def _get_base_version(cr):
    # base_version is normaly computed in `base/0.0.0/pre-base_version.py` (and symlinks)
    # However, if theses scripts are used to upgrade custom modules afterward (like the P.S. do),
    # as the `base` module not being updated, the *base_version* MUST be set as an environment variable.
    bv = ENVIRON.get("__base_version")
    if bv:
        return bv
    # trust env variable if set
    bv = os.getenv("ODOO_BASE_VERSION")
    if bv:
        bv = ENVIRON["__base_version"] = parse_version(bv)
    else:
        cr.execute("SELECT latest_version FROM ir_module_module WHERE name='base' AND state='to upgrade'")
        # Let it fail if called outside update of `base` module.
        bv = ENVIRON["__base_version"] = parse_version(cr.fetchone()[0])
    return bv


def _for_each_inherit(cr, model, skip):
    if skip == "*":
        return
    base_version = _get_base_version(cr)
    for inh in inherit.inheritance_data.get(model, []):
        if inh.model in skip:
            continue
        if inh.born <= base_version:
            if inh.dead is None or base_version < inh.dead:
                yield inh


def remove_field(cr, model, fieldname, cascade=False, drop_column=True, skip_inherit=()):
    _validate_model(model)
    if fieldname == "id":
        # called by `remove_module`. May happen when a model defined in a removed module was
        # overwritten by another module in previous version.
        return remove_model(cr, model)

    ENVIRON["__renamed_fields"][model].add(fieldname)

    keys_to_clean = (
        "group_by",
        "pivot_measures",
        "pivot_column_groupby",
        "pivot_row_groupby",
        "graph_groupbys",
        "orderedBy",
    )

    def filter_value(key, value):
        if key == "orderedBy" and isinstance(value, dict):
            res = {k: (filter_value(None, v) if k == "name" else v) for k, v in value.items()}
            if "name" not in res or res["name"] is not None:
                # return if name didn't match fieldname
                return res
        elif not isinstance(value, basestring):
            # if not a string, ignore it
            return value
        elif value.split(":")[0] != fieldname:
            # only return if not matching fieldname
            return value

    def clean_context(context):
        changed = False
        context = safe_eval(context, SelfPrintEvalContext(), nocopy=True)
        if not isinstance(context, dict):
            return context, changed
        for key in keys_to_clean:
            if context.get(key):
                context_part = [filter_value(key, e) for e in context[key]]
                changed |= context_part != context[key]
                context[key] = [e for e in context_part if e is not None]
        return context, changed

    # clean dashboard's contexts
    for id_, action in _dashboard_actions(cr, r"\y{}\y".format(fieldname), model):
        context, changed = clean_context(action.get("context", "{}"))
        action.set("context", unicode(context))
        if changed:
            add_to_migration_reports(
                ("ir.ui.view.custom", id_, action.get("string", "ir.ui.view.custom")), "Filters/Dashboards"
            )

    # clean filter's contexts
    cr.execute(
        "SELECT id, name, context FROM ir_filters WHERE model_id = %s AND context ~ %s",
        [model, r"\y{}\y".format(fieldname)],
    )
    for id_, name, context in cr.fetchall():
        context, changed = clean_context(context or "{}")
        cr.execute("UPDATE ir_filters SET context = %s WHERE id = %s", [unicode(context), id_])
        if changed:
            add_to_migration_reports(("ir.filters", id_, name), "Filters/Dashboards")

    def adapter(leaf, is_or, negated):
        # replace by TRUE_LEAF, unless negated or in a OR operation but not negated
        if is_or ^ negated:
            return [expression.FALSE_LEAF]
        return [expression.TRUE_LEAF]

    # clean domains
    adapt_domains(cr, model, fieldname, "ignored", adapter=adapter, skip_inherit=skip_inherit)

    cr.execute(
        """
        DELETE FROM ir_server_object_lines
              WHERE col1 IN (SELECT id
                               FROM ir_model_fields
                              WHERE model = %s
                                AND name = %s)
    """,
        [model, fieldname],
    )
    cr.execute("DELETE FROM ir_model_fields WHERE model=%s AND name=%s RETURNING id", (model, fieldname))
    fids = tuple(map(itemgetter(0), cr.fetchall()))
    if fids:
        cr.execute("DELETE FROM ir_model_data WHERE model=%s AND res_id IN %s", ("ir.model.fields", fids))

    # cleanup translations
    cr.execute(
        """
       DELETE FROM ir_translation
        WHERE name=%s
          AND type in ('field', 'help', 'model', 'model_terms', 'selection')   -- ignore wizard_* translations
    """,
        ["%s,%s" % (model, fieldname)],
    )

    # remove default values set for aliases
    if column_exists(cr, "mail_alias", "alias_defaults"):
        cr.execute(
            """
            SELECT a.id, a.alias_defaults
              FROM mail_alias a
              JOIN ir_model m ON m.id = a.alias_model_id
             WHERE m.model = %s
               AND a.alias_defaults ~ %s
        """,
            [model, r"\y%s\y" % (fieldname,)],
        )
        for alias_id, defaults in cr.fetchall():
            try:
                defaults = dict(safe_eval(defaults))  # XXX literal_eval should works.
            except Exception:
                continue
            defaults.pop(fieldname, None)
            cr.execute("UPDATE mail_alias SET alias_defaults = %s WHERE id = %s", [repr(defaults), alias_id])

    # if field was a binary field stored as attachment, clean them...
    if column_exists(cr, "ir_attachment", "res_field"):
        parallel_execute(
            cr,
            explode_query_range(
                cr,
                cr.mogrify(
                    "DELETE FROM ir_attachment WHERE res_model = %s AND res_field = %s", [model, fieldname]
                ).decode(),
                table="ir_attachment",
            ),
        )

    table = table_of_model(cr, model)
    # NOTE table_exists is needed to avoid altering views
    if drop_column and table_exists(cr, table) and column_exists(cr, table, fieldname):
        remove_column(cr, table, fieldname, cascade=cascade)

    # remove field on inherits
    for inh in _for_each_inherit(cr, model, skip_inherit):
        remove_field(cr, inh.model, fieldname, cascade=cascade, drop_column=drop_column, skip_inherit=skip_inherit)


def remove_field_metadata(cr, model, fieldname, skip_inherit=()):
    """
    Due to a bug of the ORM [1], mixins doesn't create/register xmlids for fields created in children models
    Thus, when a field is no more defined in a child model, their xmlids should be removed explicitly to
    avoid the fields to be considered as missing and being removed at the end of the upgrade.

    [1] https://github.com/odoo/odoo/issues/49354
    """
    _validate_model(model)

    cr.execute(
        """
            DELETE FROM ir_model_data
                  WHERE model = 'ir.model.fields'
                    AND res_id IN (SELECT id FROM ir_model_fields WHERE model=%s AND name=%s)
        """,
        [model, fieldname],
    )
    for inh in _for_each_inherit(cr, model, skip_inherit):
        remove_field_metadata(cr, inh.model, fieldname, skip_inherit=skip_inherit)


def move_field_to_module(cr, model, fieldname, old_module, new_module, skip_inherit=()):
    _validate_model(model)
    name = IMD_FIELD_PATTERN % (model.replace(".", "_"), fieldname)
    try:
        with savepoint(cr), mute_logger("openerp.sql_db", "odoo.sql_db"):
            cr.execute(
                """
                   UPDATE ir_model_data
                      SET module = %s
                    WHERE model = 'ir.model.fields'
                      AND name = %s
                      AND module = %s
            """,
                [new_module, name, old_module],
            )
    except psycopg2.IntegrityError:
        cr.execute(
            "DELETE FROM ir_model_data WHERE model = 'ir.model.fields' AND name = %s AND module = %s",
            [name, old_module],
        )
    # move field on inherits
    for inh in _for_each_inherit(cr, model, skip_inherit):
        move_field_to_module(cr, inh.model, fieldname, old_module, new_module, skip_inherit=skip_inherit)


def rename_field(cr, model, old, new, update_references=True, domain_adapter=None, skip_inherit=()):
    _validate_model(model)
    rf = ENVIRON["__renamed_fields"].get(model)
    if rf and old in rf:
        rf.discard(old)
        rf.add(new)

    try:
        with savepoint(cr):
            cr.execute("UPDATE ir_model_fields SET name=%s WHERE model=%s AND name=%s RETURNING id", (new, model, old))
            [fid] = cr.fetchone() or [None]
    except psycopg2.IntegrityError:
        # If a field with the same name already exists for this model (e.g. due to a custom module),
        # rename it to avoid clashing and warn the customer
        custom_name = new + "_custom"
        rename_field(cr, model, new, custom_name, update_references, domain_adapter=None, skip_inherit=skip_inherit)
        cr.execute("UPDATE ir_model_fields SET name=%s WHERE model=%s AND name=%s RETURNING id", (new, model, old))
        [fid] = cr.fetchone() or [None]
        msg = (
            "The field %r from the model %r is now a standard Odoo field, but it already existed in the database "
            "(coming from a non-standard module) and thus has been renamed to %r" % (new, model, custom_name)
        )
        add_to_migration_reports(msg, "Non-standard fields")

    if fid:
        name = IMD_FIELD_PATTERN % (model.replace(".", "_"), new)
        # In some cases the same field may be present on ir_model_data with both the double __ and single _ name
        # version. To avoid conflicts (module, name) on the UPDATE below we keep only the double __ version
        cr.execute(
            """
             DELETE FROM ir_model_data
                   WHERE id IN (SELECT unnest((array_agg(id ORDER BY id))[2:count(id)])
                                  FROM ir_model_data
                                 WHERE model = 'ir.model.fields'
                                   AND res_id = %s
                                 GROUP BY module)
            """,
            [fid],
        )
        try:
            with savepoint(cr):
                cr.execute("UPDATE ir_model_data SET name=%s WHERE model='ir.model.fields' AND res_id=%s", [name, fid])
        except psycopg2.IntegrityError:
            # duplicate key. May happen du to conflict between
            # some_model.sub_id and some_model_sub.id
            # (before saas~11.2, where pattern changed)
            name = "%s_%s" % (name, fid)
            cr.execute("UPDATE ir_model_data SET name=%s WHERE model='ir.model.fields' AND res_id=%s", [name, fid])
        cr.execute("UPDATE ir_property SET name=%s WHERE fields_id=%s", [new, fid])

    cr.execute(
        """
       UPDATE ir_translation
          SET name=%s
        WHERE name=%s
          AND type in ('field', 'help', 'model', 'model_terms', 'selection')   -- ignore wizard_* translations
    """,
        ["%s,%s" % (model, new), "%s,%s" % (model, old)],
    )

    if column_exists(cr, "ir_attachment", "res_field"):
        cr.execute(
            """
            UPDATE ir_attachment
               SET res_field = %s
             WHERE res_model = %s
               AND res_field = %s
        """,
            [new, model, old],
        )

    if table_exists(cr, "ir_values"):
        cr.execute(
            """
            UPDATE ir_values
               SET name = %s
             WHERE model = %s
               AND name = %s
               AND key = 'default'
        """,
            [new, model, old],
        )

    if column_type(cr, "mail_tracking_value", "field") == "varchar":
        # From saas~13.1, column `field` is a m2o to the `ir.model.fields`
        cr.execute(
            """
            UPDATE mail_tracking_value v
               SET field = %s
              FROM mail_message m
             WHERE v.mail_message_id = m.id
               AND m.model = %s
               AND v.field = %s
          """,
            [new, model, old],
        )

    table = table_of_model(cr, model)
    # NOTE table_exists is needed to avoid altering views
    if table_exists(cr, table) and column_exists(cr, table, old):
        cr.execute('ALTER TABLE "{0}" RENAME COLUMN "{1}" TO "{2}"'.format(table, old, new))
        # Rename corresponding index
        cr.execute('ALTER INDEX IF EXISTS "{0}_{1}_index" RENAME TO "{2}_{3}_index"'.format(table, old, table, new))

    if update_references:
        # skip all inherit, they will be handled by the resursive call
        update_field_references(cr, old, new, only_models=(model,), domain_adapter=domain_adapter, skip_inherit="*")

    # rename field on inherits
    for inh in _for_each_inherit(cr, model, skip_inherit):
        rename_field(cr, inh.model, old, new, update_references=update_references, skip_inherit=skip_inherit)


def convert_field_to_property(
    cr, model, field, type, target_model=None, default_value=None, default_value_ref=None, company_field="company_id"
):
    """
    Notes:
        `target_model` is only use when `type` is "many2one".
        The `company_field` can be an sql expression.
            You may use `t` to refer the model's table.
    """
    _validate_model(model)
    if target_model:
        _validate_model(target_model)
    type2field = {
        "char": "value_text",
        "float": "value_float",
        "boolean": "value_integer",
        "integer": "value_integer",
        "text": "value_text",
        "binary": "value_binary",
        "many2one": "value_reference",
        "date": "value_datetime",
        "datetime": "value_datetime",
        "selection": "value_text",
    }

    assert type in type2field
    value_field = type2field[type]

    table = table_of_model(cr, model)

    cr.execute("SELECT id FROM ir_model_fields WHERE model=%s AND name=%s", (model, field))
    if not cr.rowcount:
        # no ir_model_fields, no ir_property
        remove_column(cr, table, field, cascade=True)
        return
    [fields_id] = cr.fetchone()

    if default_value is None:
        where_clause = "{field} IS NOT NULL".format(field=field)
    else:
        where_clause = "{field} != %(default_value)s".format(field=field)

    if type == "boolean":
        value_select = "%s::integer" % field
    elif type != "many2one":
        value_select = field
    else:
        # for m2o, the store value is a refrence field, so in format `model,id`
        value_select = "CONCAT('{target_model},', {field})".format(**locals())

    if is_field_anonymized(cr, model, field):
        # if field is anonymized, we need to create a property for each record
        where_clause = "true"
        # and we need to unanonymize its values
        ano_default_value = cr.mogrify("%s", [default_value])
        if type != "many2one":
            ano_value_select = "%(value)s"
        else:
            ano_value_select = "CONCAT('{0},', %(value)s)".format(target_model)

        register_unanonymization_query(
            cr,
            model,
            field,
            """
            UPDATE ir_property
               SET {value_field} = CASE WHEN %(value)s IS NULL THEN {ano_default_value}
                                        ELSE {ano_value_select} END
             WHERE res_id = CONCAT('{model},', %(id)s)
               AND name='{field}'
               AND type='{type}'
               AND fields_id={fields_id}
            """.format(
                **locals()
            ),
        )

    cr.execute(
        """
        WITH cte AS (
            SELECT CONCAT('{model},', id) as res_id, {value_select} as value,
                   ({company_field})::integer as company
              FROM {table} t
             WHERE {where_clause}
        )
        INSERT INTO ir_property(name, type, fields_id, company_id, res_id, {value_field})
            SELECT %(field)s, %(type)s, %(fields_id)s, cte.company, cte.res_id, cte.value
              FROM cte
             WHERE NOT EXISTS(SELECT 1
                                FROM ir_property
                               WHERE fields_id=%(fields_id)s
                                 AND company_id IS NOT DISTINCT FROM cte.company
                                 AND res_id=cte.res_id)
    """.format(
            **locals()
        ),
        locals(),
    )
    # default property
    if default_value:
        cr.execute(
            """
                INSERT INTO ir_property(name, type, fields_id, {value_field})
                     VALUES (%s, %s, %s, %s)
                  RETURNING id
            """.format(
                value_field=value_field
            ),
            (field, type, fields_id, default_value),
        )
        [prop_id] = cr.fetchone()
        if default_value_ref:
            module, _, xid = default_value_ref.partition(".")
            cr.execute(
                """
                    INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
                         VALUES (%s, %s, %s, %s, %s)
            """,
                [module, xid, "ir.property", prop_id, True],
            )

    remove_column(cr, table, field, cascade=True)


# alias with a name related to the new API to declare property fields (company_dependent=True attribute)
make_field_company_dependent = convert_field_to_property


def convert_binary_field_to_attachment(cr, model, field, encoded=True, name_field=None):
    _validate_model(model)
    table = table_of_model(cr, model)
    if not column_exists(cr, table, field):
        return
    name_query = "COALESCE({0}, '{1}('|| id || ').{2}')".format(
        "NULL" if not name_field else name_field,
        model.title().replace(".", ""),
        field,
    )

    A = env(cr)["ir.attachment"]
    iter_cur = cr._cnx.cursor("fetch_binary")
    iter_cur.itersize = 1
    iter_cur.execute('SELECT id, "{field}", {name_query} FROM {table} WHERE "{field}" IS NOT NULL'.format(**locals()))
    for rid, data, name in iter_cur:
        # we can't save create the attachment with res_model & res_id as it will fail computing
        # `res_name` field for non-loaded models. Store it naked and change it via SQL after.
        data = bytes(data)
        if re.match(br"^\d+ (bytes|[KMG]b)$", data, re.I):
            # badly saved data, no need to create an attachment.
            continue
        if not encoded:
            data = base64.b64encode(data)
        att = A.create({"name": name, "datas": data, "type": "binary"})
        cr.execute(
            """
               UPDATE ir_attachment
                  SET res_model = %s,
                      res_id = %s,
                      res_field = %s
                WHERE id = %s
            """,
            [model, rid, field, att.id],
        )

    iter_cur.close()
    # free PG space
    remove_column(cr, table, field)


def change_field_selection_values(cr, model, field, mapping, skip_inherit=()):
    _validate_model(model)
    if not mapping:
        return
    table = table_of_model(cr, model)

    if column_exists(cr, table, field):
        query = "UPDATE {table} SET {field}= %s::json->>{field} WHERE {field} IN %s".format(table=table, field=field)
        queries = [
            cr.mogrify(q, [json.dumps(mapping), tuple(mapping)]).decode()
            for q in explode_query_range(cr, query, table=table)
        ]
        parallel_execute(cr, queries)

    cr.execute(
        """
        DELETE FROM ir_model_fields_selection s
              USING ir_model_fields f
              WHERE f.id = s.field_id
                AND f.model = %s
                AND f.name = %s
                AND s.value IN %s
        """,
        [model, field, tuple(mapping)],
    )

    def adapter(leaf, _or, _neg):
        left, op, right = leaf
        if isinstance(right, (tuple, list)):
            right = [mapping.get(r, r) for r in right]
        else:
            right = mapping.get(right, right)
        return [(left, op, right)]

    # skip all inherit, they will be handled by the resursive call
    adapt_domains(cr, model, field, field, adapter=adapter, skip_inherit="*")

    # rename field on inherits
    for inh in _for_each_inherit(cr, model, skip_inherit):
        change_field_selection_values(cr, inh.model, field, mapping=mapping, skip_inherit=skip_inherit)


def is_field_anonymized(cr, model, field):
    _validate_model(model)
    if not module_installed(cr, "anonymization"):
        return False
    cr.execute(
        """
            SELECT id
              FROM ir_model_fields_anonymization
             WHERE model_name = %s
               AND field_name = %s
               AND state = 'anonymized'
    """,
        [model, field],
    )
    return bool(cr.rowcount)


def register_unanonymization_query(cr, model, field, query, query_type="sql", sequence=10):
    _validate_model(model)
    cr.execute(
        """
            INSERT INTO ir_model_fields_anonymization_migration_fix(
                    target_version, sequence, query_type, model_name, field_name, query
            ) VALUES (%s, %s, %s, %s, %s, %s)
    """,
        [release.major_version, sequence, query_type, model, field, query],
    )


class IndirectReference(collections.namedtuple("IndirectReference", "table res_model res_id res_model_id set_unknown")):
    def model_filter(self, prefix="", placeholder="%s"):
        if prefix and prefix[-1] != ".":
            prefix += "."
        if self.res_model_id:
            placeholder = "(SELECT id FROM ir_model WHERE model={})".format(placeholder)
            column = self.res_model_id
        else:
            column = self.res_model

        return '{}"{}"={}'.format(prefix, column, placeholder)


# By default, there is no `res_id`, no `res_model_id` and it is deleted when the linked model is removed
IndirectReference.__new__.__defaults__ = (None, None, False)  # https://stackoverflow.com/a/18348004


def indirect_references(cr, bound_only=False):
    IR = IndirectReference
    each = [
        IR("ir_attachment", "res_model", "res_id"),
        IR("ir_cron", "model", None, set_unknown=True),
        IR("ir_act_report_xml", "model", None, set_unknown=True),
        IR("ir_act_window", "res_model", "res_id"),
        IR("ir_act_window", "src_model", None),
        IR("ir_act_server", "wkf_model_name", None),
        IR("ir_act_server", "crud_model_name", None),
        IR("ir_act_server", "model_name", None, "model_id", set_unknown=True),
        IR("ir_act_client", "res_model", None, set_unknown=True),
        IR("ir_model", "model", None),
        IR("ir_model_fields", "model", None),
        IR("ir_model_fields", "relation", None),  # destination of a relation field
        IR("ir_model_data", "model", "res_id"),
        IR("ir_filters", "model_id", None, set_unknown=True),  # YUCK!, not an id
        IR("ir_exports", "resource", None, set_unknown=True),
        IR("ir_ui_view", "model", None, set_unknown=True),
        IR("ir_values", "model", "res_id"),
        IR("wkf_transition", "trigger_model", None),
        IR("wkf_triggers", "model", None),
        IR("ir_model_fields_anonymization", "model_name", None),
        IR("ir_model_fields_anonymization_migration_fix", "model_name", None),
        IR("base_import_import", "res_model", None),
        IR("calendar_event", "res_model", "res_id"),  # new in saas~18
        IR("documents_document", "res_model", "res_id"),
        IR("email_template", "model", None, set_unknown=True),  # stored related
        IR("mail_template", "model", None, set_unknown=True),  # model renamed in saas~6
        IR("mail_activity", "res_model", "res_id", "res_model_id"),
        IR("mail_alias", None, "alias_force_thread_id", "alias_model_id"),
        IR("mail_alias", None, "alias_parent_thread_id", "alias_parent_model_id"),
        IR("mail_followers", "res_model", "res_id"),
        IR("mail_message_subtype", "res_model", None),
        IR("mail_message", "model", "res_id"),
        IR("mail_compose_message", "model", "res_id"),
        IR("mail_wizard_invite", "res_model", "res_id"),
        IR("mail_mail_statistics", "model", "res_id"),
        IR("mailing_trace", "model", "res_id"),
        IR("mail_mass_mailing", "mailing_model", None, "mailing_model_id", set_unknown=True),
        IR("mailing_mailing", None, None, "mailing_model_id", set_unknown=True),
        IR("project_project", "alias_model", None, set_unknown=True),
        IR("rating_rating", "res_model", "res_id", "res_model_id"),
        IR("rating_rating", "parent_res_model", "parent_res_id", "parent_res_model_id"),
        IR("timer_timer", "res_model", "res_id"),
    ]

    for ir in each:
        if bound_only and not ir.res_id:
            continue
        if ir.res_id and not column_exists(cr, ir.table, ir.res_id):
            continue

        # some `res_model/res_model_id` combination may change between
        # versions (i.e. rating_rating.res_model_id was added in saas~15).
        # we need to verify existance of columns before using them.
        if ir.res_model and not column_exists(cr, ir.table, ir.res_model):
            ir = ir._replace(res_model=None)
        if ir.res_model_id and not column_exists(cr, ir.table, ir.res_model_id):
            ir = ir._replace(res_model_id=None)
        if not ir.res_model and not ir.res_model_id:
            continue

        yield ir


def generate_indirect_reference_cleaning_queries(cr, ir):
    """Generator that yield queries to clean an `IndirectReference`"""

    if ir.res_model:
        query = """
            SELECT {ir.res_model}
              FROM {ir.table}
             WHERE {ir.res_model} IS NOT NULL
          GROUP BY {ir.res_model}
        """
    else:
        query = """
            SELECT m.model
              FROM {ir.table} t
              JOIN ir_model m ON m.id = t.{ir.res_model_id}
          GROUP BY m.model
        """
    cr.execute(query.format(ir=ir))
    for (model,) in cr.fetchall():
        res_table = table_of_model(cr, model)
        if table_exists(cr, res_table):
            cond = "NOT EXISTS (SELECT 1 FROM {res_table} r WHERE r.id = t.{ir.res_id})".format(**locals())
        else:
            cond = "true"

        model_filter = ir.model_filter()
        yield cr.mogrify(
            "DELETE FROM {ir.table} t WHERE {model_filter} AND {cond}".format(**locals()), [model]
        ).decode()


def res_model_res_id(cr, filtered=True):
    for ir in indirect_references(cr):
        if ir.res_model:
            yield model_of_table(cr, ir.table), ir.res_model, ir.res_id


def _unknown_model_id(cr):
    result = getattr(_unknown_model_id, "result", None)
    if result is None:
        cr.execute(
            """
                INSERT INTO ir_model(name, model)
                     SELECT 'Unknown', '_unknown'
                      WHERE NOT EXISTS (SELECT 1 FROM ir_model WHERE model = '_unknown')
            """
        )
        cr.execute("SELECT id FROM ir_model WHERE model = '_unknown'")
        _unknown_model_id.result = result = cr.fetchone()[0]
    return result


def _rm_refs(cr, model, ids=None):
    if ids is None:
        match = "like %s"
        needle = model + ",%"
    else:
        if not ids:
            return
        match = "in %s"
        needle = tuple("{0},{1}".format(model, i) for i in ids)

    # "model-comma" fields
    cr.execute(
        """
        SELECT model, name
          FROM ir_model_fields
         WHERE ttype='reference'
         UNION
        SELECT 'ir.translation', 'name'
    """
    )

    for ref_model, ref_column in cr.fetchall():
        table = table_of_model(cr, ref_model)
        if column_updatable(cr, table, ref_column):
            query_tail = ' FROM "{0}" WHERE "{1}" {2}'.format(table, ref_column, match)
            if ref_model == "ir.ui.view":
                cr.execute("SELECT id" + query_tail, [needle])
                for (view_id,) in cr.fetchall():
                    remove_view(cr, view_id=view_id, silent=True)
            elif ref_model == "ir.ui.menu":
                cr.execute("SELECT id" + query_tail, [needle])
                menu_ids = tuple(m[0] for m in cr.fetchall())
                remove_menus(cr, menu_ids)
            else:
                cr.execute("SELECT id" + query_tail, [needle])
                for (record_id,) in cr.fetchall():
                    remove_record(cr, (ref_model, record_id))

    if table_exists(cr, "ir_values"):
        column, _ = _ir_values_value(cr)
        query = "DELETE FROM ir_values WHERE {0} {1}".format(column, match)
        cr.execute(query, [needle])

    if ids is None:
        cr.execute(
            """
            DELETE FROM ir_translation
             WHERE name=%s
               AND type IN ('constraint', 'sql_constraint', 'view', 'report', 'rml', 'xsl')
        """,
            [model],
        )


def remove_model(cr, model, drop_table=True):
    _validate_model(model)
    model_underscore = model.replace(".", "_")
    chunk_size = 1000
    notify = False
    unk_id = _unknown_model_id(cr)

    # remove references
    for ir in indirect_references(cr):
        if ir.table in ("ir_model", "ir_model_fields", "ir_model_data"):
            continue

        query = """
            WITH _ as (
                SELECT r.id, bool_or(COALESCE(d.module, '') NOT IN ('', '__export__')) AS from_module
                  FROM "{}" r
             LEFT JOIN ir_model_data d ON d.model = %s AND d.res_id = r.id
                 WHERE {}
             GROUP BY r.id
            )
            SELECT from_module, array_agg(id) FROM _ GROUP BY from_module
        """
        ref_model = model_of_table(cr, ir.table)
        cr.execute(query.format(ir.table, ir.model_filter(prefix="r.")), [ref_model, model])
        for from_module, ids in cr.fetchall():
            if from_module or not ir.set_unknown:
                if ir.table == "ir_ui_view":
                    for view_id in ids:
                        remove_view(cr, view_id=view_id, silent=True)
                else:
                    # remove in batch
                    size = (len(ids) + chunk_size - 1) / chunk_size
                    it = chunks(ids, chunk_size, fmt=tuple)
                    for sub_ids in log_progress(it, _logger, qualifier=ir.table, size=size):
                        _remove_records(cr, ref_model, sub_ids)
                        _rm_refs(cr, ref_model, sub_ids)
            else:
                # link to `_unknown` model
                sets, args = zip(
                    *[
                        ('"{}" = %s'.format(c), v)
                        for c, v in [(ir.res_model, "_unknown"), (ir.res_model_id, unk_id)]
                        if c
                    ]
                )

                query = 'UPDATE "{}" SET {} WHERE id IN %s'.format(ir.table, ",".join(sets))
                cr.execute(query, args + (tuple(ids),))
                notify = notify or bool(cr.rowcount)

    _rm_refs(cr, model)

    cr.execute("SELECT id, name FROM ir_model WHERE model=%s", (model,))
    [mod_id, mod_label] = cr.fetchone() or [None, model]
    if mod_id:
        # some required fk are in "ON DELETE SET NULL/RESTRICT".
        for tbl in "base_action_rule base_automation google_drive_config".split():
            if column_exists(cr, tbl, "model_id"):
                cr.execute("DELETE FROM {0} WHERE model_id=%s".format(tbl), [mod_id])
        cr.execute("DELETE FROM ir_model_relation WHERE model=%s", (mod_id,))
        cr.execute("DELETE FROM ir_model_constraint WHERE model=%s RETURNING id", (mod_id,))
        if cr.rowcount:
            ids = tuple(c for c, in cr.fetchall())
            cr.execute("DELETE FROM ir_model_data WHERE model = 'ir.model.constraint' AND res_id IN %s", [ids])

        # Drop XML IDs of ir.rule and ir.model.access records that will be cascade-dropped,
        # when the ir.model record is dropped - just in case they need to be re-created
        cr.execute(
            """
                DELETE
                  FROM ir_model_data x
                 USING ir_rule a
                 WHERE x.res_id = a.id
                   AND x.model = 'ir.rule'
                   AND a.model_id = %s
        """,
            [mod_id],
        )
        cr.execute(
            """
                DELETE
                  FROM ir_model_data x
                 USING ir_model_access a
                 WHERE x.res_id = a.id
                   AND x.model = 'ir.model.access'
                   AND a.model_id = %s
        """,
            [mod_id],
        )

        cr.execute("DELETE FROM ir_model WHERE id=%s", (mod_id,))

    cr.execute("DELETE FROM ir_model_data WHERE model=%s AND name=%s", ("ir.model", "model_%s" % model_underscore))
    cr.execute(
        "DELETE FROM ir_model_data WHERE model='ir.model.fields' AND name LIKE %s",
        [(IMD_FIELD_PATTERN % (model_underscore, "%")).replace("_", r"\_")],
    )
    cr.execute("DELETE FROM ir_model_data WHERE model = %s", [model])

    table = table_of_model(cr, model)
    if drop_table:
        if table_exists(cr, table):
            cr.execute('DROP TABLE "{0}" CASCADE'.format(table))
        elif view_exists(cr, table):
            cr.execute('DROP VIEW "{0}" CASCADE'.format(table))

    if notify:
        add_to_migration_reports(
            message="The model {model} ({label}) has been removed. "
            "The linked records (crons, mail templates, automated actions...)"
            " have also been removed (standard) or linked to the '_unknown' model (custom).".format(
                model=model, label=mod_label
            ),
            category="Removed Models",
        )


# compat layer...
delete_model = remove_model


def move_model(cr, model, from_module, to_module, move_data=False):
    """
    move model `model` from `from_module` to `to_module`.
    if `to_module` is not installed, delete the model.
    """
    _validate_model(model)
    if not module_installed(cr, to_module):
        delete_model(cr, model)
        return

    def update_imd(model, name=None, from_module=from_module, to_module=to_module):
        where = "true"
        if name:
            where = "d.name {} %(name)s".format("LIKE" if "%" in name else "=")

        query = """
            WITH dups AS (
                SELECT d.id
                  FROM ir_model_data d, ir_model_data t
                 WHERE d.name = t.name
                   AND d.module = %(from_module)s
                   AND t.module = %(to_module)s
                   AND d.model = %(model)s
                   AND {}
            )
            DELETE FROM ir_model_data d
                  USING dups
                 WHERE dups.id = d.id
        """
        cr.execute(query.format(where), locals())

        query = """
            UPDATE ir_model_data d
               SET module = %(to_module)s
             WHERE module = %(from_module)s
               AND model = %(model)s
               AND {}
        """
        cr.execute(query.format(where), locals())

    model_u = model.replace(".", "_")

    update_imd("ir.model", "model_%s" % model_u)
    update_imd("ir.model.fields", (IMD_FIELD_PATTERN % (model_u, "%")).replace("_", r"\_"))
    update_imd("ir.model.constraint", ("constraint_%s_%%" % (model_u,)).replace("_", r"\_"))
    if move_data:
        update_imd(model)
    return


def rename_model(cr, old, new, rename_table=True):
    _validate_model(old)
    _validate_model(new)
    if old in ENVIRON["__renamed_fields"]:
        ENVIRON["__renamed_fields"][new] = ENVIRON["__renamed_fields"].pop(old)
    if rename_table:
        old_table = table_of_model(cr, old)
        new_table = table_of_model(cr, new)
        cr.execute('ALTER TABLE "{0}" RENAME TO "{1}"'.format(old_table, new_table))
        cr.execute('ALTER SEQUENCE "{0}_id_seq" RENAME TO "{1}_id_seq"'.format(old_table, new_table))

        # update moved0 references
        ENVIRON["moved0"] = {(new_table if t == old_table else t, c) for t, c in ENVIRON.get("moved0", ())}

        # find & rename primary key, may still use an old name from a former migration
        cr.execute(
            """
            SELECT conname
              FROM pg_index, pg_constraint
             WHERE indrelid = %s::regclass
               AND indisprimary
               AND conrelid = indrelid
               AND conindid = indexrelid
               AND confrelid = 0
        """,
            [new_table],
        )
        (primary_key,) = cr.fetchone()
        cr.execute('ALTER INDEX "{0}" RENAME TO "{1}_pkey"'.format(primary_key, new_table))

        # DELETE all constraints and indexes (ignore the PK), ORM will recreate them.
        cr.execute(
            """
                SELECT constraint_name
                  FROM information_schema.table_constraints
                 WHERE table_name = %s
                   AND constraint_type != %s
                   AND constraint_name !~ '^[0-9_]+_not_null$'
        """,
            [new_table, "PRIMARY KEY"],
        )
        for (const,) in cr.fetchall():
            remove_constraint(cr, new_table, const)

        # Rename indexes
        cr.execute(
            """
            SELECT concat(%(old_table)s, '_', column_name, '_index') as old_index,
                   concat(%(new_table)s, '_', column_name, '_index') as new_index
              FROM information_schema.columns
             WHERE table_name = %(new_table)s
            """,
            {"old_table": old_table, "new_table": new_table},
        )
        for old_idx, new_idx in cr.fetchall():
            cr.execute('ALTER INDEX IF EXISTS "{0}" RENAME TO "{1}"'.format(old_idx, new_idx))

    updates = [("wkf", "osv")] if table_exists(cr, "wkf") else []
    updates += [(ir.table, ir.res_model) for ir in indirect_references(cr) if ir.res_model]

    for table, column in updates:
        query = "UPDATE {t} SET {c}=%s WHERE {c}=%s".format(t=table, c=column)
        cr.execute(query, (new, old))

    # "model-comma" fields
    cr.execute(
        """
        SELECT model, name
          FROM ir_model_fields
         WHERE ttype='reference'
    """
    )
    for model, column in cr.fetchall():
        table = table_of_model(cr, model)
        if column_updatable(cr, table, column):
            cr.execute(
                """
                    UPDATE "{table}"
                       SET "{column}"='{new}' || substring("{column}" FROM '%#",%#"' FOR '#')
                     WHERE "{column}" LIKE '{old},%'
            """.format(
                    table=table, column=column, new=new, old=old
                )
            )

    # translations
    cr.execute(
        """
        WITH renames AS (
            SELECT id, type, lang, res_id, src, '{new}' || substring(name FROM '%#",%#"' FOR '#') as new
              FROM ir_translation
             WHERE name LIKE '{old},%'
        )
        UPDATE ir_translation t
           SET name = r.new
          FROM renames r
     LEFT JOIN ir_translation e ON (
            e.type = r.type
        AND e.lang = r.lang
        AND e.name = r.new
        AND CASE WHEN e.type = 'model' THEN e.res_id IS NOT DISTINCT FROM r.res_id
                 WHEN e.type = 'selection' THEN e.src IS NOT DISTINCT FROM r.src
                 ELSE e.res_id IS NOT DISTINCT FROM r.res_id AND e.src IS NOT DISTINCT FROM r.src
             END
     )
         WHERE t.id = r.id
           AND e.id IS NULL
    """.format(
            new=new, old=old
        )
    )
    cr.execute("DELETE FROM ir_translation WHERE name LIKE '{},%'".format(old))

    if table_exists(cr, "ir_values"):
        column_read, cast_write = _ir_values_value(cr)
        query = """
            UPDATE ir_values
               SET value = {cast[0]}'{new}' || substring({column} FROM '%#",%#"' FOR '#'){cast[2]}
             WHERE {column} LIKE '{old},%'
        """.format(
            column=column_read, new=new, old=old, cast=cast_write.partition("%s")
        )
        cr.execute(query)

    cr.execute(
        """
        UPDATE ir_translation
           SET name=%s
         WHERE name=%s
           AND type IN ('constraint', 'sql_constraint', 'view', 'report', 'rml', 'xsl')
    """,
        [new, old],
    )
    old_u = old.replace(".", "_")
    new_u = new.replace(".", "_")

    cr.execute(
        "UPDATE ir_model_data SET name=%s WHERE model=%s AND name=%s",
        ("model_%s" % new_u, "ir.model", "model_%s" % old_u),
    )

    cr.execute(
        """
            UPDATE ir_model_data
               SET name=%s || substring(name from %s)
             WHERE model='ir.model.fields'
               AND name LIKE %s
    """,
        ["field_%s" % new_u, len(old_u) + 7, (IMD_FIELD_PATTERN % (old_u, "%")).replace("_", r"\_")],
    )

    col_prefix = ""
    if not column_exists(cr, "ir_act_server", "condition"):
        col_prefix = "--"  # sql comment the line

    cr.execute(
        r"""
        UPDATE ir_act_server
           SET {col_prefix} condition=regexp_replace(condition, '([''"]){old}\1', '\1{new}\1', 'g'),
               code=regexp_replace(code, '([''"]){old}\1', '\1{new}\1', 'g')
    """.format(
            col_prefix=col_prefix, old=old.replace(".", r"\."), new=new
        )
    )


def merge_model(cr, source, target, drop_table=True, fields_mapping=None):
    _validate_model(source)
    _validate_model(target)
    cr.execute("SELECT model, id FROM ir_model WHERE model in %s", ((source, target),))
    model_ids = dict(cr.fetchall())
    mapping = {model_ids[source]: model_ids[target]}
    ignores = ["ir_model", "ir_model_fields", "ir_model_constraint", "ir_model_relation"]
    replace_record_references_batch(cr, mapping, "ir.model", replace_xmlid=False, ignores=ignores)

    # remap the fields on ir_model_fields
    cr.execute(
        """
        SELECT mf1.id,
               mf2.id
          FROM ir_model_fields mf1
          JOIN ir_model_fields mf2
            ON mf1.model=%s
           AND mf2.model=%s
           AND mf1.name=mf2.name
        """,
        [source, target],
    )
    field_ids_mapping = dict(cr.fetchall())
    if fields_mapping:
        cr.execute(
            """
            SELECT mf1.id,
                   mf2.id
              FROM ir_model_fields mf1
              JOIN ir_model_fields mf2
                ON mf1.model=%s
               AND mf2.model=%s
               AND mf2.name=('{jmap}'::json ->> mf1.name::varchar)::varchar
            """.format(
                jmap=json.dumps(fields_mapping)
            ),
            [source, target],
        )
        field_ids_mapping.update(dict(cr.fetchall()))

    if field_ids_mapping:
        ignores = ["ir_model_fields_group_rel", "ir_model_fields_selection"]
        replace_record_references_batch(cr, field_ids_mapping, "ir.model.fields", replace_xmlid=False, ignores=ignores)

    for ir in indirect_references(cr):
        if ir.res_model and not ir.res_id and ir.table not in ignores:
            # only update unbound references, other ones have been updated by the call to
            # `replace_record_references_batch`
            wheres = []
            for _, uniqs in _get_unique_indexes_with(cr, ir.table, ir.res_model):
                sub_where = " AND ".join("o.{0} = t.{0}".format(a) for a in uniqs if a != ir.res_model) or "true"
                wheres.append(
                    "NOT EXISTS(SELECT 1 FROM {t} o WHERE {w} AND o.{c}=%(new)s)".format(
                        t=ir.table, c=ir.res_model, w=sub_where
                    )
                )
            where = " AND ".join(wheres) or "true"
            query = "UPDATE {t} t SET {c}=%(new)s WHERE {w} AND {c}=%(old)s".format(t=ir.table, c=ir.res_model, w=where)
            cr.execute(query, dict(new=target, old=source))

    remove_model(cr, source, drop_table=drop_table)


def remove_inherit_from_model(cr, model, inherit, keep=()):
    _validate_model(model)
    _validate_model(inherit)
    cr.execute(
        """
        SELECT name, ttype, relation, store
          FROM ir_model_fields
         WHERE model = %s
           AND name NOT IN ('id',
                            'create_uid', 'write_uid',
                            'create_date', 'write_date',
                            '__last_update', 'display_name')
           AND name != ALL(%s)
    """,
        [inherit, list(keep)],
    )
    for field, ftype, relation, store in cr.fetchall():
        if ftype.endswith("2many") and store:
            # for mixin, x2many are filtered by their model.
            # for "classic" inheritance, the caller is responsible to drop the underlying m2m table
            # (or keeping the field)
            table = table_of_model(cr, relation)
            irs = [ir for ir in indirect_references(cr) if ir.table == table]
            for ir in irs:
                query = 'DELETE FROM "{}" WHERE {}'.format(ir.table, ir.model_filter())
                cr.execute(query, [model])
        remove_field(cr, model, field)


def replace_record_references(cr, old, new, replace_xmlid=True):
    """replace all (in)direct references of a record by another"""
    # TODO update workflow instances?
    assert isinstance(old, tuple) and len(old) == 2
    assert isinstance(new, tuple) and len(new) == 2

    if not old[1]:
        return

    return replace_record_references_batch(cr, {old[1]: new[1]}, old[0], new[0], replace_xmlid)


def replace_record_references_batch(cr, id_mapping, model_src, model_dst=None, replace_xmlid=True, ignores=()):
    assert id_mapping
    assert all(isinstance(v, int) and isinstance(k, int) for k, v in id_mapping.items())

    _validate_model(model_src)
    if model_dst is None:
        model_dst = model_src
    else:
        _validate_model(model_dst)

    ignores = [_validate_table(table) for table in ignores]
    if not replace_xmlid:
        ignores.append("ir_model_data")

    old = tuple(id_mapping.keys())
    new = tuple(id_mapping.values())
    jmap = json.dumps(id_mapping)

    def genmap(fmt_k, fmt_v=None):
        # generate map using given format
        fmt_v = fmt_k if fmt_v is None else fmt_v
        m = {fmt_k % k: fmt_v % v for k, v in id_mapping.items()}
        return json.dumps(m), tuple(m.keys())

    if model_src == model_dst:
        pmap, pmap_keys = genmap("I%d\n.")  # 7 time faster than using pickle.dumps
        smap, smap_keys = genmap("%d")

        column_read, cast_write = _ir_values_value(cr)

        for table, fk, _, _ in get_fk(cr, table_of_model(cr, model_src)):
            if table in ignores:
                continue
            query = """
                UPDATE {table} t
                   SET {fk} = ('{jmap}'::json->>{fk}::varchar)::int4
                 WHERE {fk} IN %(old)s
            """

            col2 = None
            if not column_exists(cr, table, "id"):
                # seems to be a m2m table. Avoid duplicated entries
                cols = get_columns(cr, table, ignore=(fk,))[0]
                assert len(cols) == 1  # it's a m2, should have only 2 columns
                col2 = cols[0]
                query = (
                    """
                    WITH _existing AS (
                        SELECT {col2} FROM {table} WHERE {fk} IN %%(new)s
                    )
                    %s
                    AND NOT EXISTS(SELECT 1 FROM _existing WHERE {col2}=t.{col2});
                    DELETE FROM {table} WHERE {fk} IN %%(old)s;
                """
                    % query
                )

            cr.execute(query.format(table=table, fk=fk, jmap=jmap, col2=col2), dict(new=new, old=old))

            if not col2:  # it's a model
                # update default values
                # TODO? update all defaults using 1 query (using `WHERE (model, name) IN ...`)
                model = model_of_table(cr, table)
                if table_exists(cr, "ir_values"):
                    query = """
                         UPDATE ir_values
                            SET value = {cast[0]} '{pmap}'::json->>({col}) {cast[2]}
                          WHERE key='default'
                            AND model=%s
                            AND name=%s
                            AND {col} IN %s
                    """.format(
                        col=column_read, cast=cast_write.partition("%s"), pmap=pmap
                    )
                    cr.execute(query, [model, fk, pmap_keys])
                else:
                    cr.execute(
                        """
                        UPDATE ir_default d
                           SET json_value = '{smap}'::json->>json_value
                          FROM ir_model_fields f
                         WHERE f.id = d.field_id
                           AND f.model = %s
                           AND f.name = %s
                           AND d.json_value IN %s
                    """.format(
                            smap=smap
                        ),
                        [model, fk, smap_keys],
                    )

    # indirect references
    for ir in indirect_references(cr, bound_only=True):
        if ir.table in ignores:
            continue
        upd = ""
        if ir.res_model:
            upd += '"{ir.res_model}" = %(model_dst)s,'
        if ir.res_model_id:
            upd += '"{ir.res_model_id}" = (SELECT id FROM ir_model WHERE model=%(model_dst)s),'
        upd = upd.format(ir=ir)
        whr = ir.model_filter(placeholder="%(model_src)s")

        query = """
            UPDATE "{ir.table}"
               SET {upd}
                   "{ir.res_id}" = ('{jmap}'::json->>{ir.res_id}::varchar)::int4
             WHERE {whr}
               AND {ir.res_id} IN %(old)s
        """.format(
            **locals()
        )

        cr.execute(query, locals())

    # reference fields
    cmap, cmap_keys = genmap("%s,%%d" % model_src, "%s,%%d" % model_dst)
    cr.execute("SELECT model, name FROM ir_model_fields WHERE ttype='reference'")
    for model, column in cr.fetchall():
        table = table_of_model(cr, model)
        if table not in ignores and column_updatable(cr, table, column):
            cr.execute(
                """
                    UPDATE "{table}"
                       SET "{column}" = '{cmap}'::json->>"{column}"
                     WHERE "{column}" IN %s
            """.format(
                    table=table, column=column, cmap=cmap
                ),
                [cmap_keys],
            )


def update_field_references(cr, old, new, only_models=None, domain_adapter=None, skip_inherit=()):
    """
    Replace all references to field `old` to `new` in:
        - ir_filters
        - ir_exports_line
        - ir_act_server
        - mail_alias
        - ir_ui_view_custom (dashboard)
    """
    if only_models:
        for model in only_models:
            _validate_model(model)

    p = {
        "old": r"\y%s\y" % (old,),
        "new": new,
        "def_old": r"\ydefault_%s\y" % (old,),
        "def_new": "default_%s" % (new,),
        "models": tuple(only_models) if only_models else (),
    }

    col_prefix = ""
    if not column_exists(cr, "ir_filters", "sort"):
        col_prefix = "--"  # sql comment the line
    q = """
        UPDATE ir_filters
           SET {col_prefix} sort = regexp_replace(sort, %(old)s, %(new)s, 'g'),
               context = regexp_replace(regexp_replace(context,
                                                       %(old)s, %(new)s, 'g'),
                                                       %(def_old)s, %(def_new)s, 'g')
    """

    if only_models:
        q += " WHERE model_id IN %(models)s AND "
    else:
        q += " WHERE "
    q += """
        (
            context ~ %(old)s
            OR context ~ %(def_old)s
            {col_prefix} OR sort ~ %(old)s
        )
    """
    cr.execute(q.format(col_prefix=col_prefix), p)

    # ir.exports.line
    q = """
        UPDATE ir_exports_line l
           SET name = regexp_replace(l.name, %(old)s, %(new)s, 'g')
    """
    if only_models:
        q += """
          FROM ir_exports e
         WHERE e.id = l.export_id
           AND e.resource IN %(models)s
           AND
        """
    else:
        q += "WHERE "
    q += "l.name ~ %(old)s"
    cr.execute(q, p)

    # ir.action.server
    col_prefix = ""
    if not column_exists(cr, "ir_act_server", "condition"):
        col_prefix = "--"  # sql comment the line
    q = """
        UPDATE ir_act_server s
           SET {col_prefix} condition = regexp_replace(condition, %(old)s, %(new)s, 'g'),
               code = regexp_replace(code, %(old)s, %(new)s, 'g')
    """
    if only_models:
        q += """
          FROM ir_model m
         WHERE m.id = s.model_id
           AND m.model IN %(models)s
           AND
        """
    else:
        q += " WHERE "

    q += """s.state = 'code'
           AND (
              s.code ~ %(old)s
              {col_prefix} OR s.condition ~ %(old)s
           )
    """
    cr.execute(q.format(col_prefix=col_prefix), p)

    # mail.alias
    if column_exists(cr, "mail_alias", "alias_defaults"):
        q = """
            UPDATE mail_alias a
               SET alias_defaults = regexp_replace(a.alias_defaults, %(old)s, %(new)s, 'g')
        """
        if only_models:
            q += """
              FROM ir_model m
             WHERE m.id = a.alias_model_id
               AND m.model IN %(models)s
               AND
            """
        else:
            q += "WHERE "
        q += "a.alias_defaults ~ %(old)s"
        cr.execute(q, p)

    # ir.ui.view.custom
    # adapt the context. The domain will be done by `adapt_domain`
    eval_context = SelfPrintEvalContext()
    def_old = "default_{}".format(old)
    def_new = "default_{}".format(new)
    match = "{0[old]}|{0[def_old]}".format(p)

    def adapt_value(key, value):
        if key == "orderedBy" and isinstance(value, dict):
            # only adapt the "name" key
            return {k: (adapt_value(None, v) if k == "name" else v) for k, v in value.items()}

        if not isinstance(value, basestring):
            # ignore if not a string
            return value

        parts = value.split(":", 1)
        if parts[0] != old:
            # if not match old, leave it
            return value
        # change to new, and return it
        parts[0] = new
        return ":".join(parts)

    keys_to_clean = (
        "group_by",
        "pivot_measures",
        "pivot_column_groupby",
        "pivot_row_groupby",
        "graph_groupbys",
        "orderedBy",
    )
    for _, act in _dashboard_actions(cr, match, def_old, *only_models or ()):
        context = safe_eval(act.get("context", "{}"), eval_context, nocopy=True)
        for key in keys_to_clean:
            if context.get(key):
                context[key] = [adapt_value(key, e) for e in context[key]]

        if def_old in context:
            context[def_new] = context.pop(def_old)
        act.set("context", unicode(context))

    if only_models:
        for model in only_models:
            # skip all inherit, they will be handled by the resursive call
            adapt_domains(cr, model, old, new, adapter=domain_adapter, skip_inherit="*")
            adapt_related(cr, model, old, new, skip_inherit="*")

        inherited_models = tuple(
            inh.model for model in only_models for inh in _for_each_inherit(cr, model, skip_inherit)
        )
        if inherited_models:
            update_field_references(
                cr, old, new, only_models=inherited_models, domain_adapter=domain_adapter, skip_inherit=skip_inherit
            )


DomainField = collections.namedtuple("DomainField", "table domain_column model_select")


def _get_domain_fields(cr):
    # haaa, if only we had a `fields.Domain`, we would just have to get all the domains from `ir_model_fields`
    # Meanwile, we have to enumerate them explicitly
    # false friends: the `domain` fields on `website` and `amazon.marketplace` are actually domain names.
    # NOTE: domains on transient models have been ignored
    mmm = []
    if column_exists(cr, "mail_mass_mailing", "mailing_model_id"):
        # >= saas~18
        mmm = [
            DomainField(
                "mail_mass_mailing", "mailing_domain", "(SELECT model FROM ir_model m WHERE m.id = t.mailing_model_id)"
            )
        ]
    elif column_exists(cr, "mail_mass_mailing", "mailing_model"):
        # >= saas~4
        mmm = [DomainField("mail_mass_mailing", "mailing_domain", "mailing_model")]
    else:
        mail_template = "mail_template" if table_exists(cr, "mail_template") else "email_template"
        mmm = [
            DomainField(
                "mail_mass_mailing",
                "mailing_domain",
                "(SELECT model FROM {} m WHERE m.id = t.template_id)".format(mail_template),
            )
        ]

    documents_domains_target = "'documents.document'" if table_exists(cr, "documents_document") else "'ir.attachment'"

    result = mmm + [
        DomainField("ir_model_fields", "domain", "model"),
        DomainField("ir_act_window", "domain", "res_model"),
        DomainField("ir_filters", "domain", "model_id"),  # model_id is a varchar
        DomainField("ir_rule", "domain_force", "(SELECT model FROM ir_model m WHERE m.id = t.model_id)"),
        DomainField("document_directory", "domain", "(SELECT model FROM ir_model m WHERE m.id = t.ressource_type_id)"),
        DomainField(
            "mailing_mailing", "mailing_domain", "(SELECT model FROM ir_model m WHERE m.id = t.mailing_model_id)"
        ),
        DomainField("base_action_rule", "filter_domain", "(SELECT model FROM ir_model m WHERE m.id = t.model_id)"),
        DomainField("base_action_rule", "filter_pre_domain", "(SELECT model FROM ir_model m WHERE m.id = t.model_id)"),
        DomainField(
            "base_automation", "filter_domain", "(SELECT model_name FROM ir_act_server WHERE id = t.action_server_id)"
        ),
        DomainField(
            "base_automation",
            "filter_pre_domain",
            "(SELECT model_name FROM ir_act_server WHERE id = t.action_server_id)",
        ),
        DomainField("gamification_goal_definition", "domain", "(SELECT model FROM ir_model m WHERE m.id = t.model_id)"),
        DomainField("marketing_campaign", "domain", "model_name"),
        DomainField(
            "marketing_activity", "domain", "(SELECT model_name FROM marketing_campaign WHERE id = t.campaign_id)"
        ),
        DomainField(
            "marketing_activity",
            "activity_domain",
            "(SELECT model_name FROM marketing_campaign WHERE id = t.campaign_id)",
        ),
        DomainField("data_merge_model", "domain", "res_model_name"),
        # static target model
        DomainField("account_financial_html_report_line", "domain", "'account.move.line'"),
        DomainField("gamification_challenge", "user_domain", "'res.users'"),
        DomainField("pos_cache", "product_domain", "'product.product'"),
        DomainField("sale_coupon_rule", "rule_partners_domain", "'res.partner'"),
        DomainField("sale_coupon_rule", "rule_products_domain", "'product.product'"),
        DomainField("sale_subscription_template", "good_health_domain", "'sale.subscription'"),
        DomainField("sale_subscription_template", "bad_health_domain", "'sale.subscription'"),
        DomainField("website_crm_score", "domain", "'crm.lead'"),
        DomainField("team_user", "team_user_domain", "'crm.lead'"),
        DomainField("crm_team", "score_team_domain", "'crm.lead'"),
        DomainField("social_post", "visitor_domain", "'website.visitor'"),
        DomainField("documents_share", "domain", documents_domains_target),
        DomainField("documents_workflow_rule", "domain", documents_domains_target),
        DomainField("loyalty_rule", "rule_domain", "'product.product'"),
    ]

    for df in result:
        if column_exists(cr, df.table, df.domain_column):
            yield df


def _adapt_one_domain(cr, target_model, old, new, model, domain, adapter=None):
    if not adapter:
        adapter = lambda leaf, _, __: [leaf]

    evaluation_context = SelfPrintEvalContext()

    # pre-check domain
    if isinstance(domain, basestring):
        try:
            eval_dom = expression.normalize_domain(safe_eval(domain, evaluation_context, nocopy=True))
        except Exception as e:
            oops = odoo.tools.ustr(e)
            _logger.log(NEARLYWARN, "Cannot evaluate %r domain: %r: %s", model, domain, oops)
            return None
    else:
        try:
            eval_dom = expression.normalize_domain(domain)
        except Exception as e:
            oops = odoo.tools.ustr(e)
            _logger.log(NEARLYWARN, "Invalid %r domain: %r: %s", model, domain, oops)
            return None

    def valid_path_to(cr, path, from_, to):
        model = from_
        while path:
            field = path.pop(0)
            cr.execute(
                """
                SELECT relation
                  FROM ir_model_fields
                 WHERE model = %s
                   AND name = %s
            """,
                [model, field],
            )
            if not cr.rowcount:
                # unknown field. Maybe an old domain. Cannot validate it.
                return False
            [model] = cr.fetchone()

        return model == to

    def clean_path(left):
        path = left.split(".")
        for idx in range(1, len(path) + 1):
            if path[-idx] == old and valid_path_to(cr, path[:-idx], model, target_model):
                path[-idx] = new
        return ".".join(path)

    def clean_term(term):
        if isinstance(term, basestring) or not isinstance(term[0], basestring):
            return term
        return (clean_path(term[0]), term[1], term[2])

    final_dom = []
    changed = False
    op_arity = {expression.NOT_OPERATOR: 1, expression.AND_OPERATOR: 2, expression.OR_OPERATOR: 2}
    op_stack = []  # (operator, number of terms missing)
    for element in eval_dom:
        while op_stack and op_stack[-1][1] == 0:
            op_stack.pop()  # found all terms current operator was expecting, pop it
            op_stack[-1][1] -= 1  # previous operator now got one more term

        if isinstance(element, basestring):
            if element not in op_arity:
                _logger.log(NEARLYWARN, "Invalid domain on %r: %s", model, domain)
                return None
            op_stack.append([element, op_arity[element]])
            final_dom.append(element)
            continue

        if not expression.is_leaf(element):
            _logger.log(NEARLYWARN, "Invalid domain on %r: %s", model, domain)
            return None

        if op_stack:
            op_stack[-1][1] -= 1  # previous operator got a term

        if tuple(element) in [expression.TRUE_LEAF, expression.FALSE_LEAF]:
            final_dom.append(element)
            continue

        is_or = False
        neg = False
        for op, _ in reversed(op_stack):
            if op != expression.NOT_OPERATOR:
                is_or = op == expression.OR_OPERATOR
                break
            neg = not neg

        leaf = expression.normalize_leaf(element)
        path = leaf[0].split(".")
        if path[-1] == old and valid_path_to(cr, path[:-1], model, target_model):
            # adapt only when {old} field is the last part of left path
            dom = [clean_term(term) for term in adapter(leaf, is_or, neg)]
        else:
            dom = [clean_term(leaf)]

        if dom != [leaf]:
            changed = True

        final_dom.extend(dom)

    if not changed:
        return None

    _logger.debug("%s: %r -> %r", model, domain, final_dom)
    return final_dom


def adapt_domains(cr, model, old, new, adapter=None, skip_inherit=()):
    """
    Replace {old} by {new} in all domains for model {model} using an adapter callback.

    {adapter} is to adapt leafs. It is a function that takes three arguments and
    returns a domain that substitutes the original leaf:
    (leaf: Tuple[str,str,Any], in_or: bool, negated: bool) -> List[Union[str,Tuple[str,str,Any]]]

    The parameter {in_or} signals that the leaf is part of an or ("|") domain, otherwise
    it is part of an and ("&") domain. The other parameter signals if the leaf is
    {negated} ("!").

    Note that the {adapter} is called ony on leafs that use the {old} field of {model}.
    """
    _validate_model(model)
    target_model = model

    match_old = r"\y{}\y".format(old)
    for df in _get_domain_fields(cr):
        cr.execute(
            """
            SELECT id, {df.model_select}, {df.domain_column}
              FROM {df.table} t
             WHERE {df.domain_column} ~ %s
        """.format(
                df=df
            ),
            [match_old],
        )
        for id_, model, domain in cr.fetchall():
            domain = _adapt_one_domain(cr, target_model, old, new, model, domain, adapter=adapter)
            if domain:
                cr.execute(
                    "UPDATE {df.table} SET {df.domain_column} = %s WHERE id = %s".format(df=df), [unicode(domain), id_]
                )

    # adapt domain in dashboards.
    # NOTE: does not filter on model at dashboard selection for handle dotted domains
    for _, act in _dashboard_actions(cr, match_old):
        if act.get("domain"):
            try:
                act_id = int(act.get("name", "FAIL"))
            except ValueError:
                continue

            cr.execute("SELECT res_model FROM ir_act_window WHERE id = %s", [act_id])
            if not cr.rowcount:
                continue
            [act_model] = cr.fetchone()
            domain = _adapt_one_domain(cr, target_model, old, new, act_model, act.get("domain"), adapter=adapter)
            if domain:
                act.set("domain", unicode(domain))

    # down on inherits
    for inh in _for_each_inherit(cr, target_model, skip_inherit):
        adapt_domains(cr, inh.model, old, new, adapter, skip_inherit=skip_inherit)


def adapt_related(cr, model, old, new, skip_inherit=()):
    _validate_model(model)

    if not column_exists(cr, "ir_model_fields", "related"):
        # this field only appears in 9.0
        return

    target_model = model

    match_old = r"\y{}\y".format(old)
    cr.execute(
        """
        SELECT id, model, related
          FROM ir_model_fields
         WHERE related ~ %s
        """,
        [match_old],
    )
    for id_, model, related in cr.fetchall():
        domain = _adapt_one_domain(cr, target_model, old, new, model, [(related, "=", "related")])
        if domain:
            related = domain[0][0]
            cr.execute("UPDATE ir_model_fields SET related = %s WHERE id = %s", [related, id_])

    # TODO adapt paths in email templates?

    # down on inherits
    for inh in _for_each_inherit(cr, target_model, skip_inherit):
        adapt_related(cr, inh.model, old, new, skip_inherit=skip_inherit)


def update_server_actions_fields(cr, src_model, dst_model=None, fields_mapping=None):
    """
    When some fields of `src_model` have ben copied to `dst_model` and/or have
    been copied to fields with another name, some references have to be moved.

    For server actions, this function starts by updating `ir_server_object_lines`
    to refer to new fields. If no `fields_mapping` is provided, all references to
    fields that exist in both models (source and destination) are moved. If no `dst_model`
    is given, the `src_model` is used as `dst_model`.
    Then, if `dst_model` is set, `ir_act_server` referred by modified `ir_server_object_lines`
    are also updated. A chatter message informs the customer about this modification.
    """
    if dst_model is None and fields_mapping is None:
        raise SleepyDeveloperError(
            "at least dst_model or fields_mapping must be given to the move_field_references function."
        )

    _dst_model = dst_model if dst_model is not None else src_model

    # update ir_server_object_lines to point to new fields
    if fields_mapping is None:
        cr.execute(
            """
            WITH field_ids AS (
                SELECT mf1.id as old_field_id, mf2.id as new_field_id
                  FROM ir_model_fields mf1
                  JOIN ir_model_fields mf2 ON mf2.name = mf1.name
                 WHERE mf1.model = %s
                   AND mf2.model = %s
            )
               UPDATE ir_server_object_lines
                  SET col1 = f.new_field_id
                 FROM field_ids f
                WHERE col1 = f.old_field_id
            RETURNING server_id
            """,
            [src_model, _dst_model],
        )
    else:
        psycopg2.extras.execute_values(
            cr._obj,
            """
            WITH field_ids AS (
                SELECT mf1.id as old_field_id, mf2.id as new_field_id
                  FROM (VALUES %s) AS mapping(src_model, dst_model, old_name, new_name)
                  JOIN ir_model_fields mf1 ON mf1.name = mapping.old_name AND mf1.model = mapping.src_model
                  JOIN ir_model_fields mf2 ON mf2.name = mapping.new_name AND mf2.model = mapping.dst_model
            )
               UPDATE ir_server_object_lines
                  SET col1 = f.new_field_id
                 FROM field_ids f
                WHERE col1 = f.old_field_id
            RETURNING server_id
            """,
            [(src_model, _dst_model, fm[0], fm[1]) for fm in fields_mapping],
        )

    # update ir_act_server records to point to the right model if set
    if dst_model is not None and src_model != dst_model and cr.rowcount > 0:
        action_ids = tuple(set([row[0] for row in cr.fetchall()]))

        cr.execute(
            """
               UPDATE ir_act_server
                  SET model_name = %s, model_id = ir_model.id
                 FROM ir_model
                WHERE ir_model.model = %s
                  AND ir_act_server.id IN %s
            RETURNING ir_act_server.name
            """,
            [dst_model, dst_model, action_ids],
        )

        action_names = [row[0] for row in cr.fetchall()]

        # inform the customer through the chatter about this modification
        msg = (
            "The following server actions have been updated due to moving "
            "fields from '%(src_model)s' to '%(dst_model)s' model and need "
            "a checking from your side: %(actions)s"
        ) % {"src_model": src_model, "dst_model": dst_model, "actions": ", ".join(action_names)}

        add_to_migration_reports(message=msg, category="Server Actions")


def check_company_consistency(
    cr, model_name, field_name, logger=_logger, model_company_field="company_id", comodel_company_field="company_id"
):
    _validate_model(model_name)
    cr.execute(
        """
            SELECT ttype, relation, relation_table, column1, column2
              FROM ir_model_fields
             WHERE name = %s
               AND model = %s
               AND store IS TRUE
               AND ttype IN ('many2one', 'many2many')
    """,
        [field_name, model_name],
    )

    field_values = cr.dictfetchone()

    if not field_values:
        _logger.warning("Field %s not found on model %s.", field_name, model_name)
        return

    table = table_of_model(cr, model_name)
    comodel = field_values["relation"]
    cotable = table_of_model(cr, comodel)

    limit = 15

    if field_values["ttype"] == "many2one":
        query = """
            SELECT a.id, a.{model_company_field}, b.id, b.{comodel_company_field}, count(*) OVER ()
              FROM {table} a
              JOIN {cotable} b ON b.id = a.{field_name}
             WHERE a.{model_company_field} IS NOT NULL
               AND b.{comodel_company_field} IS NOT NULL
               AND a.{model_company_field} != b.{comodel_company_field}
             LIMIT {limit}
        """.format(
            **locals()
        )
    else:  # many2many
        m2m_relation = field_values["relation_table"]
        f1, f2 = field_values["column1"], field_values["column2"]
        query = """
            SELECT a.id, a.{model_company_field}, b.id, b.{comodel_company_field}, count(*) OVER ()
              FROM {m2m_relation} m
              JOIN {table} a ON a.id = m.{f1}
              JOIN {cotable} b ON b.id = m.{f2}
             WHERE a.{model_company_field} IS NOT NULL
               AND b.{comodel_company_field} IS NOT NULL
               AND a.{model_company_field} != b.{comodel_company_field}
             LIMIT {limit}
        """.format(
            **locals()
        )

    cr.execute(query)
    if cr.rowcount:
        logger.warning(
            "Company field %s/%s is not consistent with %s/%s for %d records (through %s relation %s)",
            model_name,
            model_company_field,
            comodel,
            comodel_company_field,
            cr.rowcount,
            field_values["ttype"],
            field_name,
        )

        bad_rows = cr.fetchall()
        total = bad_rows[-1][-1]
        lis = "\n".join("<li>record #%s (company=%s) -&gt; record #%s (company=%s)</li>" % bad[:-1] for bad in bad_rows)

        add_to_migration_reports(
            message="""\
            <details>
              <summary>
                Some inconsistencies have been found on field {model_name}/{field_name} ({total} records affected; show top {limit})
              </summary>
              <ul>
                {lis}
              </ul>
            </details>
        """.format(
                **locals()
            ),
            category="Multi-company inconsistencies",
            format="html",
        )


def split_group(cr, from_groups, to_group):
    """Users have all `from_groups` will be added into `to_group`"""

    def check_group(g):
        if isinstance(g, basestring):
            gid = ref(cr, g)
            if not gid:
                _logger.warning("split_group(): Unknow group: %r", g)
            return gid
        return g

    if not isinstance(from_groups, (list, tuple, set)):
        from_groups = [from_groups]

    from_groups = [g for g in map(check_group, from_groups) if g]
    if not from_groups:
        return

    if isinstance(to_group, basestring):
        to_group = ref(cr, to_group)

    assert to_group

    cr.execute(
        """
        INSERT INTO res_groups_users_rel(uid, gid)
             SELECT uid, %s
               FROM res_groups_users_rel
           GROUP BY uid
             HAVING array_agg(gid) @> %s
             EXCEPT
             SELECT uid, gid
               FROM res_groups_users_rel
              WHERE gid = %s
    """,
        [to_group, from_groups, to_group],
    )


def drop_workflow(cr, osv):
    if not table_exists(cr, "wkf"):
        # workflows have been removed in 10.saas~14
        # noop if there is no workflow tables anymore...
        return

    cr.execute(
        """
        -- we want to first drop the foreign keys on the workitems because
        -- it slows down the process a lot
        ALTER TABLE wkf_triggers DROP CONSTRAINT wkf_triggers_workitem_id_fkey;
        ALTER TABLE wkf_workitem DROP CONSTRAINT wkf_workitem_act_id_fkey;
        ALTER TABLE wkf_workitem DROP CONSTRAINT wkf_workitem_inst_id_fkey;
        ALTER TABLE wkf_triggers DROP CONSTRAINT wkf_triggers_instance_id_fkey;

        -- if this workflow is used as a subflow, complete workitem running this subflow
        UPDATE wkf_workitem wi
           SET state = 'complete'
          FROM wkf_instance i JOIN wkf w ON (w.id = i.wkf_id)
         WHERE wi.subflow_id = i.id
           AND w.osv = %(osv)s
           AND wi.state = 'running'
        ;

        -- delete the workflow and dependencies
        WITH deleted_wkf AS (
            DELETE FROM wkf WHERE osv = %(osv)s RETURNING id
        ),
        deleted_wkf_instance AS (
            DELETE FROM wkf_instance i
                  USING deleted_wkf w
                  WHERE i.wkf_id = w.id
              RETURNING i.id
        ),
        _delete_triggers AS (
            DELETE FROM wkf_triggers t
                  USING deleted_wkf_instance i
                  WHERE t.instance_id = i.id
        ),
        deleted_wkf_activity AS (
            DELETE FROM wkf_activity a
                  USING deleted_wkf w
                  WHERE a.wkf_id = w.id
              RETURNING a.id
        )
        DELETE FROM wkf_workitem wi
              USING deleted_wkf_instance i
              WHERE wi.inst_id = i.id
        ;

        -- recreate constraints
        ALTER TABLE wkf_triggers ADD CONSTRAINT wkf_triggers_workitem_id_fkey
            FOREIGN KEY (workitem_id) REFERENCES wkf_workitem(id)
            ON DELETE CASCADE;
        ALTER TABLE wkf_workitem ADD CONSTRAINT wkf_workitem_act_id_fkey
            FOREIGN key (act_id) REFERENCES wkf_activity(id)
            ON DELETE CASCADE;
        ALTER TABLE wkf_workitem ADD CONSTRAINT wkf_workitem_inst_id_fkey
            FOREIGN KEY (inst_id) REFERENCES wkf_instance(id)
            ON DELETE CASCADE;
        ALTER TABLE wkf_triggers ADD CONSTRAINT wkf_triggers_instance_id_fkey
            FOREIGN KEY (instance_id) REFERENCES wkf_instance(id)
            ON DELETE CASCADE;
        """,
        dict(osv=osv),
    )


@contextmanager
def no_fiscal_lock(cr):
    env(cr)["res.company"].invalidate_cache()
    columns = [col for col in get_columns(cr, "res_company")[0] if col.endswith("_lock_date")]
    assert columns
    set_val = ", ".join("{} = NULL".format(col) for col in columns)
    returns = ", ".join("old.{}".format(col) for col in columns)
    cr.execute(
        """
            UPDATE res_company c
               SET {}
              FROM res_company old
             WHERE old.id = c.id
         RETURNING {}, old.id
        """.format(
            set_val, returns
        )
    )
    data = cr.fetchall()
    yield
    set_val = ", ".join("{} = %s".format(col) for col in columns)
    cr.executemany(
        """
            UPDATE res_company
               SET {}
             WHERE id = %s
        """.format(
            set_val
        ),
        data,
    )


__all__ = list(locals())
