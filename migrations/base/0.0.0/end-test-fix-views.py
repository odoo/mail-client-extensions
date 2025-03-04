from lxml.builder import E
from lxml.etree import Comment, tostring

from odoo.addons.base.maintenance.migrations import util

# defined in odoo.addons.base.maintenance.migrations.testing
# don't import to avoid importing odoo.tests
DATA_TABLE = "upgrade_test_data" if util.version_gte("12.0") else None


def ts(e):
    return tostring(e, encoding="unicode")


def migrate(cr, version):
    # Companion script to TestFixViews in base/tests/test_fix_views.py
    # Here we simulate standard views that change during the upgrade
    if not DATA_TABLE or not util.table_exists(cr, DATA_TABLE):
        return
    query = util.format_query(
        cr, "SELECT 1 FROM {} WHERE key='base.tests.test_fix_views.TestFixViews' LIMIT 1", DATA_TABLE
    )
    cr.execute(query)
    if not cr.rowcount:
        return

    data = [
        (
            "test_upg.test_fix_views_standard_base_view",
            ts(
                E.form(
                    Comment("Ensure this comment here doesn't fail the upgrade"),
                    E.field(name="comment"),
                ),
            ),
        ),
        (
            "test_upg.test_fix_views_standard_extension_view",
            ts(
                E.xpath(E.div("Position after"), expr="//field[@name='comment']", position="after"),
            ),
        ),
        (
            "test_upg.test_fix_views_child",
            ts(
                E.xpath(E.div("Remove field"), expr="//field[@name='full_name']", position="replace"),
            ),
        ),
        (
            "test_upg.test_fix_views_view_3",
            ts(
                E.xpath(E.div("Remove field"), expr="//field[@name='name']", position="replace"),
            ),
        ),
        (
            "test_upg.test_fix_views_standard_base_view_comments",
            ts(
                E.form(
                    E.div(
                        Comment("Ensure this comment here doesn't fail the upgrade"),
                    ),
                ),
            ),
        ),
        (
            "test_upg.test_fix_views_standard_base_view_update_replace_ext2",
            ts(
                E.field("<div>OK</div>", name="comment", position="after"),
            ),
        ),
        (
            "test_upg.test_fix_views_standard_base_view_update_replace_without_child_ext2",
            ts(
                E.field("<div>OK</div>", name="comment", position="after"),
            ),
        ),
        (
            "test_upg.test_fix_views_qweb_report",
            ts(
                E.div(name="new"),
            ),
        ),
        (
            "test_upg.test_fix_views_qweb_non_report",
            ts(
                E.div(name="new"),
            ),
        ),
    ]

    IrUiView = util.env(cr)["ir.ui.view"]
    for xmlid, arch in data:
        view = IrUiView.browse(util.ref(cr, xmlid))
        view.arch = arch
