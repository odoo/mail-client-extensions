# -*- coding: utf-8 -*-

from lxml import etree, html

import odoo.upgrade.util.snippets as snip
from odoo.upgrade import util

utf8_parser = html.HTMLParser(encoding="utf-8")


def migrate(cr, version):
    # -> For the views
    migrate_event_snippet(cr, "ir_ui_view", "arch_db")
    # -> For the HTML fields
    for table, column in snip.get_html_fields(cr):
        migrate_event_snippet(cr, table, column)


def migrate_event_snippet(cr, table, column):
    filter_id = str(util.ref(cr, "website_event.website_snippet_filter_event_list"))
    if util.column_type(cr, table, column.strip('"')) == "jsonb":
        column_select = f"{column}->>'en_US'"
        column_value = "jsonb_build_object('en_US', %s)"
    else:
        column_select = column
        column_value = "%s"
    cr.execute(
        rf"""
            SELECT id, {column_select}
              FROM {table}
              WHERE {column_select} ~ '\ys_country_events\y'
        """
    )
    for res_id, body in cr.fetchall():
        body = html.fromstring(body, parser=utf8_parser)
        snippet_els = body.xpath("//*[@data-snippet='s_country_events']")
        for el in snippet_els:
            # since the new snippet has nothing to do with the old snippet, we don't need to retrieve any configuration
            el.tag = "section"
            el.set("class", "s_events s_event_upcoming_snippet s_dynamic d-none pt32 pb32 s_event_event_picture")
            el.set("data-snippet", "s_events")
            el.set("data-number-of-records", "4")
            el.set("data-number-of-elements", "2")
            el.set("data-number-of-elements-small-devices", "1")
            el.set("data-filter-id", filter_id)

            template_xmlid = "website_event.dynamic_filter_template_event_event_picture"
            el.set("data-template-key", template_xmlid)

            for old_container in el.xpath(".//div[hasclass('country_events_list')]"):
                new_container = html.fromstring(
                    """
<div class="container o_not_editable">
    <div class="css_non_editable_mode_hidden">
        <div class="missing_option_warning alert alert-info rounded-0 fade show d-none d-print-none">
            Your Dynamic Snippet will be displayed here...
            This message is displayed because you did not provide both a filter and a template to use.
            <br/>
        </div>
    </div>
    <div class="dynamic_snippet_template"/>
</div>
                    """,
                    parser=utf8_parser,
                )
                old_container.getparent().replace(old_container, new_container)

        if snippet_els:
            body = etree.tostring(body, encoding="unicode")
            cr.execute(f"UPDATE {table} SET {column} = {column_value} WHERE id = %s", [body, res_id])
