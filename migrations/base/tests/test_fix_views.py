from lxml.builder import E
from lxml.etree import tostring

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase


def ts(e):
    return tostring(e, encoding="unicode")


class TestFixViews(UpgradeCase):
    def prepare(self):
        view_ids = []

        def create_view(_vals, standard_view=False, arch_fs=None, noupdate=False):

            # default values
            vals = {
                "active": True,
                "priority": 10,
                "type": "form",
                "model": "res.groups",
                "mode": "primary",
                "arch_fs": arch_fs,
            }
            vals.update(_vals)
            view = self.env["ir.ui.view"].create(vals)
            view_ids.append(view.id)

            if standard_view:
                self.env["ir.model.data"].create(
                    {
                        "res_id": view.id,
                        "model": "ir.ui.view",
                        "module": "test_upg",
                        "name": vals["name"],
                        "noupdate": noupdate,
                    }
                )

            return view.id

        base_id = create_view(
            {
                "name": "test_fix_views_standard_base_view",
                "arch_db": ts(
                    E.form(
                        E.field(name="name"),
                        E.field(name="comment"),
                        E.field(name="users"),
                        E.field(name="share"),
                    ),
                ),
            },
            standard_view=True,
        )

        create_view(
            {
                "name": "test_fix_views_extension_view1",
                "mode": "extension",
                "inherit_id": base_id,
                "arch_db": ts(
                    E.xpath(E.div("Before first field"), expr="//field[@name='name']", position="before"),
                ),
            }
        )

        create_view(
            {
                "name": "test_fix_views_extension_view2",
                "mode": "extension",
                "inherit_id": base_id,
                "arch_db": ts(
                    E.xpath(E.div("After last field"), expr="//field[@name='users']", position="after"),
                ),
            }
        )

        vid = create_view(
            {
                "name": "test_fix_views_extension_view3",
                "mode": "extension",
                "inherit_id": base_id,
                "arch_db": ts(
                    E.xpath(E.div("After a field"), expr="//field[@name='name']", position="after"),
                ),
            }
        )

        create_view(
            {
                "name": "test_fix_views_extension_view8",
                "mode": "extension",
                "inherit_id": vid,
                "arch_db": ts(
                    E.xpath(E.div("Second inherit view"), expr="//field[@name='name']", position="after"),
                ),
            }
        )

        create_view(
            {
                "name": "test_fix_views_extension_view9",
                "mode": "extension",
                "inherit_id": base_id,
                "arch_db": ts(
                    E.field(E.div("Using <field position='after'/>"), name="name", position="after"),
                ),
            }
        )

        create_view(
            {
                "name": "test_fix_views_extension_view4",
                "mode": "extension",
                "inherit_id": base_id,
                "arch_db": ts(
                    E.xpath(E.div("Before a field"), expr="//field[@name='users']", position="before"),
                ),
            }
        )

        create_view(
            {
                "name": "test_fix_views_extension_view7",
                "mode": "extension",
                "inherit_id": base_id,
                "arch_db": ts(
                    E.data(
                        E.xpath(E.div("Anchor is gone"), expr="//field[@name='users']", position="before"),
                        E.xpath(E.div("Double anchor is gone"), expr="//field[@name='name']", position="before"),
                        E.xpath(E.div("Remove anchor is gone"), expr="//field[@name='share']", position="replace"),
                    )
                ),
            }
        )

        create_view(
            {
                "name": "test_fix_views_extension_view6",
                "mode": "extension",
                "inherit_id": base_id,
                "arch_db": ts(
                    E.xpath(E.attribute("1", name="invisible"), expr="//field[@name='name']", position="attributes"),
                ),
            }
        )

        base_id = create_view(
            {
                "name": "test_fix_views_standard_base_view2",
                "arch_db": ts(
                    E.form(
                        E.field(name="name"),
                        E.field(name="comment"),
                        E.field(name="users"),
                    ),
                ),
                "priority": 11,
            },
            standard_view=True,
        )

        create_view(
            {
                "name": "test_fix_views_standard_extension_view",
                "mode": "extension",
                "inherit_id": base_id,
                "arch_db": ts(
                    E.xpath(E.div("Position after"), expr="//field[@name='name']", position="after"),
                ),
            },
            standard_view=True,
        )

        create_view(
            {
                "name": "test_fix_views_extension_view5",
                "mode": "extension",
                "inherit_id": base_id,
                "arch_db": ts(
                    E.xpath(E.div("Remove field"), expr="//field[@name='comment']", position="replace"),
                ),
                "priority": 9,
            }
        )

        # Views used to test inheritance of type mode="primary"
        # ###
        # 1. Test when the parent is noupdate=1 and the child is updated and can't find a node (parent should be restored)
        # ###
        parent_id = create_view(
            {
                "name": "test_fix_views_parent",
                "arch_db": ts(
                    E.form(
                        E.field(name="name"),
                        E.field(name="comment"),
                    ),
                ),
            },
            standard_view=True,
            arch_fs="test_views.xml",
            noupdate=True,
        )

        create_view(
            {
                "name": "test_fix_views_child",
                "mode": "primary",
                "inherit_id": parent_id,
                "arch_db": ts(
                    E.xpath(E.div("Remove field"), expr="//field[@name='comment']", position="replace"),
                ),
                "priority": 11,
            },
            standard_view=True,
        )

        # ###
        # 2. Test when the GRANDparent is noupdate=1 and the child is updated and can't
        # find a node (grandparent should be restored in this case, but the parent is restored along the way too)
        # ###
        view_1_id = create_view(
            {
                "name": "test_fix_views_view_1",
                "arch_db": ts(
                    E.form(
                        E.field(name="comment"),
                        E.field(name="users"),
                    ),
                ),
            },
            standard_view=True,
            arch_fs="test_views.xml",
            noupdate=True,
        )

        view_2_id = create_view(
            {
                "name": "test_fix_views_view_2",
                "mode": "primary",
                "inherit_id": view_1_id,
                "arch_db": ts(
                    E.xpath(E.div("Remove field"), expr="//field[@name='comment']", position="replace"),
                ),
                "priority": 11,
            },
            standard_view=True,
            arch_fs="test_views.xml",
        )

        create_view(
            {
                "name": "test_fix_views_view_3",
                "mode": "primary",
                "inherit_id": view_2_id,
                "arch_db": ts(
                    E.xpath(E.div("Remove field"), expr="//field[@name='users']", position="replace"),
                ),
                "priority": 12,
            },
            standard_view=True,
        )

        return view_ids

    def check(self, view_ids):
        views = self.env["ir.ui.view"].browse(view_ids)
        for view in views:
            self.assertTrue(view.active, "The view {} was disabled during the migration".format(view.name))
            try:
                view._check_xml()
            except Exception as e:
                self.fail("Failed to fix view {}:\n{}".format(view.name, e))
