import logging
import os
import re
from functools import lru_cache

from odoo import modules

from odoo.upgrade import util
from odoo.upgrade.util import snippets
from odoo.upgrade.util.convert_bootstrap import BootstrapConverter, BootstrapHTMLConverter, convert_tree

_logger = logging.getLogger(__name__)


def convert_views_bootstrap(cr, src_version, dst_version, views_ids):
    """
    Convert the specified views xml arch Bootstrap version from ``src_version`` to ``dst_version``.

    :param psycopg2.cursor cr: the database cursor.
    :param str src_version: the Bootstrap version to convert from.
    :param str dst_version: the Bootstrap version to convert to.
    :param typing.Collection[int] views_ids: the ids of the views to convert.
    """
    if not views_ids:
        return
    _logger.info("Converting %s views/templates Bootstrap code from %s to %s", len(views_ids), src_version, dst_version)

    for view_id in views_ids:
        with util.edit_view(cr, view_id=view_id, active=None) as arch:
            convert_tree(arch, src_version, dst_version, is_qweb=True)
        # TODO abt: maybe notify in the log or report that custom views with noupdate=False were converted?


def convert_views(cr):
    """Convert website views / COWed templates to Bootstrap 5."""
    # views to convert must have `website_id` set and not come from standard modules
    standard_modules = set(modules.get_modules()) - {"studio_customization", "__export__", "__cloc_exclude__"}

    is_bs = get_bs5_where_clause(cr, util.SQLStr("v.arch_db"))

    # Search for custom/cow'ed views (they have no external ID)... but also
    # search for views with external ID that have a related COW'ed view. Indeed,
    # when updating a generic view after this script, the archs are compared to
    # know if the related COW'ed views must be updated too or not: if we only
    # convert COW'ed views to Bootstrap 5, they won't get the generic view
    # update as they will be judged different from them (user customization)
    # because of the BS5 changes that were made.
    # E.g.
    # - In 15.0, install website_sale
    # - Enable eCommerce categories: a COW'ed view is created to enable the
    #   feature (it leaves the generic disabled and creates an exact copy but
    #   enabled)
    # - Migrate to 16.0: you expect your enabled COW'ed view to get the new 16.0
    #   version of eCommerce categories... but if the COW'ed view was migrated
    #   to BS5 while the generic was not, they won't be considered the same
    #   anymore and only the generic view will get the 16.0 update.
    query = util.format_query(
        cr,
        """
        WITH keys AS (
              SELECT key
                FROM ir_ui_view
            GROUP BY key
              HAVING COUNT(*) > 1
        )
           SELECT v.id
             FROM ir_ui_view v
        LEFT JOIN ir_model_data imd
               ON imd.model = 'ir.ui.view'
              AND imd.module IN %s
              AND imd.res_id = v.id
        LEFT JOIN keys
               ON v.key = keys.key
            WHERE v.type = 'qweb'
              AND ({is_bs})
              AND (
                  imd.id IS NULL
                  OR (
                      keys.key IS NOT NULL
                      AND imd.noupdate = FALSE
                  )
              )
        """,
        is_bs=util.SQLStr(is_bs),
    )
    cr.execute(query, [tuple(standard_modules)])
    views_ids = [view_id for (view_id,) in cr.fetchall()]
    if views_ids:
        convert_views_bootstrap(cr, "4.0", "5.0", views_ids)


@lru_cache(maxsize=1)
def get_keyword_list():
    conversions = BootstrapConverter.get_conversions("4.0", "5.0")

    kwd_pattern = r"[A-Za-z][\w-]*"

    classes = set()
    other_kwds = set()
    for compiled_xpath, _ in conversions:
        xpath = compiled_xpath.path

        class_match = re.search(rf"hasclass\s*\(\s*['\"]({kwd_pattern})['\"]\s*\)", xpath)
        if class_match:
            classes.add(class_match.group(1))

        regex_match = re.search(r"regex\((.*)\)", xpath)
        if regex_match:
            regex_inner = regex_match.group(1)
            matches = re.findall(rf"(?<![(|@\[-\\])\b{kwd_pattern}", regex_inner)
            classes.update(matches)

        if not class_match and not regex_match:
            attr_match = re.search(rf"@({kwd_pattern})\b", xpath)
            if attr_match:
                other_kwds.add(attr_match.group(1))

            tag_match = re.search(rf"(?<=/)({kwd_pattern})\b(?!\s*\()", xpath)
            if tag_match:
                other_kwds.add(tag_match.group(1))

    other_kwds -= {"class", "regex", "concat", "hasclass"}
    return classes, other_kwds


def get_bs5_where_clause(cr, column):
    def add_word_delimiters(keyword):
        keyword = re.sub(r"^(?=\w)", r"\\m", keyword)
        keyword = re.sub(r"(?<=\w)$", r"\\M", keyword)
        return keyword  # noqa RET504

    classes, other_kwds = get_keyword_list()
    query = util.format_query(
        cr,
        r"(({column} ~ '\mclass\M\s*=' AND {column} ~ %(classes)s) OR {column} ~ %(others)s)",
        column=column,
    )
    return cr.mogrify(
        query,
        {
            "classes": "|".join(add_word_delimiters(cls) for cls in classes),
            "others": "|".join(add_word_delimiters(kw) for kw in other_kwds),
        },
    ).decode()


def convert_html_fields(cr):
    _logger.info("Converting html fields data Bootstrap code from 4.0 to 5.0")
    converter_fn = BootstrapHTMLConverter("4.0", "5.0")

    html_fields = list(snippets.html_fields(cr))
    for table, columns in util.log_progress(html_fields, _logger, "tables", log_hundred_percent=True):
        if table not in ("mail_message", "mail_activity"):
            extra_where = " OR ".join(
                f"({get_bs5_where_clause(cr, util.get_value_or_en_translation(cr, table, column))})"
                for column in columns
            )
            snippets.convert_html_columns(cr, table, columns, converter_fn, extra_where=extra_where)


def migrate(cr, version):
    if not util.module_installed(cr, "web"):
        return

    convert_views(cr)

    if util.str2bool(os.getenv("UPG_BS5_CONVERT_HTML_FIELDS", "1")):
        convert_html_fields(cr)
