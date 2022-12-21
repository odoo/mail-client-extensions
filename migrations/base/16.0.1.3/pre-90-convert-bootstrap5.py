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
    _logger.info(f"Converting {len(views_ids)} views/templates Bootstrap code from {src_version} to {dst_version}")

    for view_id in views_ids:
        with util.edit_view(cr, view_id=view_id, active=None) as arch:
            convert_tree(arch, src_version, dst_version, is_qweb=True)
        # TODO abt: maybe notify in the log or report that custom views with noupdate=False were converted?

    cr.execute("UPDATE ir_ui_view SET arch_updated = True WHERE id IN %s", [tuple(views_ids)])


# def bootstrap_html_converter(src_version, dst_version):
#     """
#     Creates a function that converts HTML Bootstrap code from ``src_version`` to ``dst_version``.

#     The returned function accepts a single argument, the html content to convert,
#     and returns a tuple of (has_changed, converted_html), suitable for usage with
#     ``util.snippets.convert_html_content``.

#     :param str src_version: the Bootstrap version to convert from.
#     :param str dst_version: the Bootstrap version to convert to.
#     :rtype: callable[[str], tuple[bool, str]]
#     """

#     @lru_cache(maxsize=128)  # does avg 20~30% hits
#     def convert(content):
#         if not content:
#             return False, content
#         converted_content = convert_arch(content, src_version, dst_version, is_html=True, is_qweb=True)
#         return content != converted_content, converted_content

#     return convert


def convert_views(cr):
    """Convert website views / COWed templates to Bootstrap 5."""
    # views to convert must have `website_id` set and not come from standard modules
    standard_modules = set(modules.get_modules()) - {"studio_customization", "__export__", "__cloc_exclude__"}

    is_bs = get_bs5_where_clause(cr, "v.arch_db")

    cr.execute(
        f"""
        SELECT v.id
          FROM ir_ui_view v
         WHERE ({is_bs})
           AND v.type = 'qweb'
           AND NOT EXISTS (SELECT 1
                             FROM ir_model_data imd
                            WHERE imd.model = 'ir.ui.view'
                              AND imd.module IN %s
                              AND imd.res_id = v.id
                              AND imd.noupdate = False)
        """,
        [tuple(standard_modules)],
    )
    views_ids = [view_id for view_id, in cr.fetchall()]
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
        return keyword

    classes, other_kwds = get_keyword_list()
    clause = cr.mogrify(
        rf"(({column} ~ '\mclass\M\s*=' AND {column} ~ %(classes)s) OR {column} ~ %(others)s)",
        {
            "classes": "|".join(add_word_delimiters(cls) for cls in classes),
            "others": "|".join(add_word_delimiters(kw) for kw in other_kwds),
        },
    ).decode()
    return clause


def convert_html_fields(cr):
    _logger.info("Converting html fields data Bootstrap code from 4.0 to 5.0")
    # converter_fn = bootstrap_html_converter("4.0", "5.0")
    converter_fn = BootstrapHTMLConverter("4.0", "5.0")

    html_fields = list(snippets.html_fields(cr))
    for table, columns in util.log_progress(html_fields, _logger, "tables", log_hundred_percent=True):
        if table not in ("mail_message", "mail_activity"):
            extra_where = " OR ".join(f"({get_bs5_where_clause(cr, column)})" for column in columns)
            snippets.convert_html_columns(cr, table, columns, converter_fn, extra_where=extra_where)

    # convert_cache_info = converter_fn.cache_info()
    # processed_count = convert_cache_info.hits + convert_cache_info.misses
    # if processed_count:
    #     _logger.info(
    #         f"Processed {processed_count} html fields values"
    #         f" ({convert_cache_info.hits / processed_count:.2%} cache hits)"
    #     )
    # else:
    #     _logger.info("No html fields values to process found")

    # converter_fn.cache_clear()


def migrate(cr, version):
    if not util.module_installed(cr, "web"):
        return

    convert_views(cr)

    if util.str2bool(os.getenv("UPG_BS5_CONVERT_HTML_FIELDS", "1")):
        convert_html_fields(cr)
