import logging

import lxml.etree as et

from odoo.tools import safe_eval

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    updated_views = []
    cr.execute(r"SELECT id, name FROM ir_ui_view WHERE arch_db->>'en_US' ~ '\ystyle-inline\y'")
    for vid, vname in cr.fetchall():
        with util.edit_view(cr, view_id=vid) as arch:
            for elem in arch.xpath("//field[contains(@options, 'style-inline')]"):
                try:
                    options = safe_eval(
                        elem.attrib.get("options"),
                        context=util.SelfPrintEvalContext({"true": True, "false": False}),
                    )
                except Exception:
                    _logger.error("Couldn't parse `options` attribute in %s", et.tostring(elem).decode())  # noqa: TRY400
                    continue
                if options.pop("inline-style", None):
                    elem.set("widget", "html_mail")
                    elem.set("options", str(options))
                    updated_views.append((vid, vname, elem.get("name")))

    if updated_views:
        util.add_to_migration_reports(
            category="Views",
            format="html",
            message="""
            <summary>
                HTML fields edited inline should now use the widget `html_mail` or any extension (maybe a custom one).
                All fields in views using style-inline as an `option` have been set to use the `html_mail` widget instead.
                Below is a list of updated fields on each view.
            <details>
                <ul>{}</ul>
            </details>
            </summay>
            """.format(
                "\n".join(
                    "<li>Field {!r} updated in view {}</li>".format(
                        fname, util.get_anchor_link_to_record("ir.ui.view", vid, vname)
                    )
                    for vid, vname, fname in updated_views
                )
            ),
        )
