# -*- coding: utf-8 -*-
import logging

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Remove dashboard view_mode from window actions
    cr.execute(
        """
        WITH
        rem AS (
            DELETE FROM ir_act_window_view awv
             WHERE awv.view_mode = 'dashboard'
        ),
        upd AS (
            UPDATE ir_act_window a
               SET view_mode = ARRAY_TO_STRING(ARRAY_REMOVE(STRING_TO_ARRAY(a.view_mode, ','), 'dashboard'), ',')
             WHERE a.view_mode LIKE '%dashboard%'
         RETURNING a.id,
                   a.view_mode
        )
        SELECT upd.id, d.module || '.' || d.name
          FROM upd
     LEFT JOIN ir_model_data d
            ON d.res_id = upd.id
           AND d.model = 'ir.actions.act_window'
           AND d.module != 'studio_customization'
         WHERE upd.view_mode = '' -- invalid value
    """
    )
    invalid_ids = []
    for id_, xmlid in cr.fetchall():
        if xmlid:
            _logger.warning("Restore action %r since it was using only dashboard views", xmlid)
            util.update_record_from_xml(cr, xmlid)
        else:
            invalid_ids.append(id_)
    remove_custom_views(cr)
    if invalid_ids:
        cr.execute(
            """
            UPDATE ir_act_window
               SET view_mode = 'tree,form'
             WHERE view_mode = ''
               AND id IN %s
            """,
            [tuple(invalid_ids)],
        )

        msg = """
        <details>
            <summary>
            In Odoo 16 'dashboard' is no longer a valid view mode for window actions.
            The following actions were using only dashboard and have been reset to the defult list and form view.
            </summary>
            <ul>
            {}
            <ul>
        </details>
        """.format(
            "\n".join(
                "<li>{}</li>".format(
                    util.get_anchor_link_to_record("ir.actions.act_window", id_, f"Ir.Action(id={id_})")
                )
                for id_ in invalid_ids
            )
        )
        util.add_to_migration_reports(msg, format="html", category="Actions")


def remove_custom_views(cr):
    pattern = r'\yview_mode="dashboard"'
    _logger.info("Fixing/removing broken dashboard actions from custom views")
    for _, act in util.helpers._dashboard_actions(cr, pattern):
        if act.get("view_mode") == "dashboard":
            act.getparent().remove(act)
