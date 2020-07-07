# -*- coding: utf-8 -*-
import logging
from lxml import etree, html
from odoo.upgrade import util

_logger = logging.getLogger("odoo.upgrade.web_editor.132." + __name__)
utf8_parser = html.HTMLParser(encoding="utf-8")


class Snippet:
    def __init__(self, name, tag="*", klass="", selector=""):
        self.name = name
        self.tag = tag
        self.klass = klass or name
        self.selector = selector or f'//{tag}[hasclass("{self.klass}")]'


def add_snippet_names(cr, table, column, snippets, select_query):
    """
    Execute the select_query then for each snippet contained in arch add the right data-snippet
    attribute on the right element.

    :param str table: The table we are working on
    :param str column: The column we are working on
    :param list snippets: list of all snippets to migrate
    :param str select_query: a query that when executed will return (id, list of snippets contained in the arch, arch)
    """
    _logger.info("Add snippet names on %s.%s", table, column)
    cr.execute(select_query)

    it = util.log_progress(cr.fetchall(), qualifier="rows", logger=_logger, size=cr.rowcount, log_hundred_percent=True)

    for res_id, regex_matches, arch in it:
        regex_matches = [match[0] for match in regex_matches]
        body = html.fromstring(arch, parser=utf8_parser)
        for snippet in snippets:
            if snippet.klass in regex_matches:
                body_snippets = body.xpath(snippet.selector)
                for body_snippet in body_snippets:
                    body_snippet.attrib["data-snippet"] = snippet.name
        body = etree.tostring(body, encoding="unicode")
        cr.execute(f"UPDATE {table} SET {column} = %s WHERE id = %s", [body, res_id])


def add_snippet_names_on_html_field(cr, table, column, snippets, regex):
    """
    Will search for all the snippets in the fields mentionned (should be html fields) and add
    the corresponding data-snippet on them.
    """
    if not (util.column_exists(cr, table, column) and util.table_exists(cr, table)):
        # Should be a regular table (cannot update views)
        return

    select_query = cr.mogrify(
        f"""
            SELECT id, array((SELECT regexp_matches({column}, %(regex)s, 'g'))), {column}
              FROM {table}
             WHERE {column} ~ %(regex)s
        """,
        dict(regex=regex),
    )
    add_snippet_names(cr, table, column, snippets, select_query)


def get_regex_from_snippets_list(snippets):
    return "(%s)" % "|".join(snippet.klass for snippet in snippets)
