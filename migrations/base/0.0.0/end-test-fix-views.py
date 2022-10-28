from lxml.builder import E
from lxml.etree import tostring

from odoo.addons.base.maintenance.migrations import util

if util.version_gte("12.0"):
    from odoo.addons.base.maintenance.migrations.testing import DATA_TABLE
else:
    DATA_TABLE = None


def ts(e):
    return tostring(e, encoding="unicode")


def migrate(cr, version):
    # Companion script to TestFixViews in base/tests/test_fix_views.py
    # Here we simulate standard views that change during the upgrade
    if not DATA_TABLE or not util.table_exists(cr, DATA_TABLE):
        return
    cr.execute("SELECT 1 FROM {} WHERE key='base.tests.test_fix_views.TestFixViews' LIMIT 1".format(DATA_TABLE))
    if not cr.rowcount:
        return

    data = [
        (
            "test_upg.test_fix_views_standard_base_view",
            ts(
                E.form(
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
                E.xpath(E.div("Remove field"), expr="//field[@name='users']", position="replace"),
            ),
        ),
        (
            "test_upg.test_fix_views_view_3",
            ts(
                E.xpath(E.div("Remove field"), expr="//field[@name='name']", position="replace"),
            ),
        ),
    ]

    IrUiView = util.env(cr)["ir.ui.view"]
    for xmlid, arch in data:
        view = IrUiView.browse(util.ref(cr, xmlid))
        view.arch = arch
