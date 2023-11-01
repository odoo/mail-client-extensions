from lxml.builder import E
from lxml.etree import Comment, tostring

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase


def ts(e):
    return tostring(e, encoding="unicode")


class TestFixViews(UpgradeCase):
    def _get_base_version(self):
        self.env.cr.execute("SELECT latest_version FROM ir_module_module WHERE name='base'")
        return self.env.cr.fetchone()[0]

    def prepare(self):
        info = []

        def create_view(
            _vals,
            standard_view=False,
            arch_fs=None,
            noupdate=False,
            disabled_post_upgrade=False,
        ):
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
            info.append((view.id, disabled_post_upgrade))

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

        base_id1 = base_id = create_view(
            {
                "name": "test_fix_views_standard_base_view",
                "arch_db": ts(
                    E.form(
                        E.field(name="name"),  # gone after upgrade
                        Comment("Ensure this comment here doesn't fail the upgrade; __last_update"),
                        E.field(name="comment"),
                        E.field(name="users"),  # gone after upgrade
                        E.field(name="share"),  # gone after upgrade
                        E.div("This will be gone during the upgrade", id="gone"),
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

        # A custom view that fails should have its children re-activated
        # TODO: This should be an example of a custom view that is disabled during the upgrade
        #       that's to test that its children are re-enabled and checked. The problem is that
        #       the fixer is working "so good" that I cannot find a valid and simple example of
        #       a custom view being disabled with the fixer activated. ¯\_(ツ)_/¯
        custom_base_id = create_view(
            {
                "name": "test_fix_views_custom_base_view",
                "mode": "extension",
                "inherit_id": base_id1,
                "arch_db": ts(E.xpath(E.div(id="Remove div"), expr="//div[@id='gone']", position="replace")),
            },
            disabled_post_upgrade=False,  # Should be True, see TODO before
        )

        create_view(
            {
                "name": "test_fix_views_custom_extension_view",
                "mode": "extension",
                "inherit_id": custom_base_id,
                "arch_db": ts(
                    E.xpath(E.div("This is OK"), expr="//field[@name='comment']", position="after"),
                ),
            },
        )

        # Test check for primary views with a custom extension in one of its primary parents
        p1_id = create_view(
            {
                "name": "test_fix_views_p1",
                "mode": "primary",
                "arch_db": ts(
                    E.form(
                        E.field(name="name"),
                    ),
                ),
            },
            standard_view=True,
        )
        create_view(
            {
                "name": "test_fix_views_p2",
                "mode": "primary",
                "inherit_id": p1_id,
                "arch_db": ts(
                    E.xpath("<div>bad</div>", expr="//field[@name='name']", position="after"),
                ),
            },
            standard_view=True,
        )
        create_view(
            {
                "name": "test_fix_views_e1",
                "mode": "extension",
                "inherit_id": p1_id,
                "arch_db": ts(
                    E.xpath(expr="//field[@name='name']", position="replace"),
                ),
            },
        )

        # Ensure we do not try to search by comment tag
        base_id2 = create_view(
            {
                "name": "test_fix_views_standard_base_view_comments",
                "arch_db": ts(
                    E.form(
                        E.field(name="name"),  # gone after upgrade
                        Comment("Ensure this comment here doesn't fail the upgrade"),
                    ),
                ),
            },
            standard_view=True,
        )
        create_view(
            {
                "name": "test_fix_views_standard_base_view_comments_ext",
                "mode": "extension",
                "inherit_id": base_id2,
                "arch_db": ts(
                    E.xpath("<div>OK</div>", expr="//field[@name='name']", position="after"),
                ),
            },
        )

        base_id3 = create_view(
            {
                "name": "test_fix_views_standard_base_view_update_replace",
                "arch_db": ts(
                    E.form(
                        E.field(name="name"),
                        E.field(name="comment"),
                    ),
                ),
            },
            standard_view=True,
        )
        create_view(
            {
                "name": "test_fix_views_standard_base_view_update_replace_ext1",
                "mode": "extension",
                "inherit_id": base_id3,
                "arch_db": ts(
                    E.data(
                        E.xpath(E.div("Child"), expr="//field[@name='comment']", position="replace"),
                    ),
                ),
            },
        )
        create_view(
            {
                "name": "test_fix_views_standard_base_view_update_replace_ext2",
                "mode": "extension",
                "inherit_id": base_id3,
                "arch_db": ts(
                    # will be anchored after `comment` post-upgrade, instead of `name`
                    E.field("<div>OK</div>", name="name", position="after"),
                ),
            },
            standard_view=True,
        )

        base_id4 = create_view(
            {
                "name": "test_fix_views_standard_base_view_update_replace_without_child",
                "arch_db": ts(
                    E.form(
                        E.field(name="name"),
                        E.field(name="comment"),
                    ),
                ),
            },
            standard_view=True,
        )
        create_view(
            {
                "name": "test_fix_views_standard_base_view_update_replace_without_child_ext1",
                "mode": "extension",
                "inherit_id": base_id4,
                "arch_db": ts(
                    E.data(
                        E.xpath(expr="//field[@name='comment']", position="replace"),
                    ),
                ),
            },
        )
        create_view(
            {
                "name": "test_fix_views_standard_base_view_update_replace_without_child_ext2",
                "mode": "extension",
                "inherit_id": base_id4,
                "arch_db": ts(
                    # will be anchored after `comment` post-upgrade, instead of `name`
                    E.field("<div>OK</div>", name="name", position="after"),
                ),
            },
            standard_view=True,
        )
        if not util.version_gte("16.0"):
            base_id5 = create_view(
                {
                    "name": "test_fix_views_standard_base_view_group_adding_base",
                    "arch_db": ts(
                        E.form(
                            E.field(name="name", attrs="{'invisible': [['comment','=',1]]}"),
                            E.field(name="comment"),
                        ),
                    ),
                },
                standard_view=True,
            )
            create_view(
                {
                    "name": "test_fix_views_standard_base_view_group_adding_child_ext1",
                    "mode": "extension",
                    "inherit_id": base_id5,
                    "arch_db": ts(
                        E.data(
                            E.xpath(
                                E.attribute("base.group_system", name="groups"),
                                expr="//field[2]",
                                position="attributes",
                            ),
                        ),
                    ),
                },
            )
        return [self._get_base_version(), info]

    def check(self, data):
        version, info = data
        if version == self._get_base_version():
            # To allow running test_prepare/check without running the upgrade scripts
            # Practial use case: upgrade from master to master in runbot
            return
        views = self.env["ir.ui.view"].browse([x[0] for x in info])
        for view, (vid, disabled) in zip(views, info):
            assert view.id == vid
            self.assertTrue(
                view.active == (not disabled),
                "The view {} was {}disabled during the migration".format(view.name, "not " if disabled else ""),
            )
            if disabled:
                continue  # we don't check disabled views
            try:
                view._check_xml()
            except Exception as e:
                self.fail("Failed to fix view {}:\n{}".format(view.name, e))
