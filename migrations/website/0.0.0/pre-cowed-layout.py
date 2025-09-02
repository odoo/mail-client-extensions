# -*- coding: utf-8 -*-

import logging

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.upgrade.website.tests." + __name__)


def migrate(cr, version):
    # COW appeared after saas-11.4, arch_updated appeared after saas-12.2.
    if util.version_gte("saas~12.3"):
        _reset_cowed_views(cr, version)


def _reset_cowed_views(cr, version):
    views_to_reset = set()
    # Share with post-cowed-layout.
    util.ENVIRON["website_cowed_views_to_reset"] = views_to_reset
    layout_view_keys = [
        "web.layout",
        "web.frontend_layout",
        "portal.frontend_layout",
        "website.layout",
        "website.navbar_toggler",
    ]
    columns = util.get_columns(cr, "ir_ui_view", ignore=("id", "key", "active"))
    cr.execute(
        """
        SELECT id,
               key,
               website_id
          FROM ir_ui_view
         WHERE key IN %s
           AND arch_updated
           AND website_id IS NOT NULL
        """,
        [tuple(layout_view_keys)],
    )
    report_msgs = []
    for id, key, website_id in cr.fetchall():
        # Create backup record.
        backup_key = "{}_backup_upgrade_{}_{}".format(
            key,
            version.replace("saas~", "").replace("saas-", "").replace(".", "_"),
            website_id,
        )
        cr.execute(
            util.format_query(
                cr,
                """
                INSERT INTO ir_ui_view AS backup_view
                            ({columns}, active, key)
                     SELECT {columns}, false, %s
                       FROM ir_ui_view v
                      WHERE v.id = %s
                  RETURNING backup_view.id
                """,
                columns=columns,
            ),
            [backup_key, id],
        )
        backup_id = cr.fetchone()[0]
        _logger.info(
            "COWed ir.ui.view(id=%s, key=%r) for website=%s had a different arch. "
            "It has been reset, a backup copy was archived with key=%r",
            id,
            key,
            website_id,
            backup_key,
        )
        report_msgs.append(
            "COWed view {} (website={}), backup copy {}".format(
                util.get_anchor_link_to_record("ir.ui.view", id, key),
                website_id,
                util.get_anchor_link_to_record("ir.ui.view", backup_id, backup_key),
            )
        )
        views_to_reset.add(key)
    if report_msgs:
        util.add_to_migration_reports(
            category="Website",
            message="""
            <details>
            <summary>
            Some COWed views had a modified arch. These views are fundamental for the
            correct website layout. To ensure compatibility with newer Odoo versions
            they have been reset. A backup copy has been saved for each of them.
            See the full list below.
            </summary>
            <ul>{}</ul>
            </details>
            """.format(" ".join("<li>{}</li>".format(m) for m in report_msgs)),
            format="html",
        )
