from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        r"""
            SELECT id
              FROM ir_ui_view
             WHERE key = 'website.layout'
               AND website_id IS NOT NULL
               AND arch_db->>'en_US' !~ '\yeditable_in_backend\y'
        """
    )
    for (view,) in cr.fetchall():
        with util.edit_view(cr, view_id=view) as arch:
            comment = util.lxml.etree.Comment(
                """
                /!\\ Notice that some `html_data` keys were moved between the `t-if`
                version and the normal `t-set` below as a bug fix in stable 16.0.
                Existing users before that fix may experience issues with:
                - The publish button as a restricted editor
                - The "edit-in-backend" button as a restricted editor
                - The "Products" snippet as a visitor
                - ...
                None should be critical though (you just not have access to some
                (important) features anymore). An update of the website app or
                patching this view directly to have the following lines setting
                `html_data` should solve the issue.

                TODO remove this comment in master and also avoid the t-set outside
                of the if (kept here to be a bit more stable).
            """
            )

            e1 = util.lxml.etree.Element(
                "t",
                {
                    "t-set": "editable_in_backend",
                    "t-value": "edit_in_backend or ('website_published' in main_object.fields_get() and main_object._name != 'website.page')",
                },
            )
            e2 = util.lxml.etree.Element(
                "t",
                {
                    "t-set": "html_data",
                    "t-value": """{"lang": lang and lang.replace('_', '-'), "data-website-id": website.id if website else None,
                    "data-edit_translations": "1" if edit_translations else None,
                    "data-main-object": repr(main_object) if main_object else None,
                    "data-seo-object": repr(seo_object) if seo_object else None,}""",
                },
            )

            e3 = util.lxml.etree.Element(
                "t",
                {
                    "t-if": "not request.env.user._is_public()",
                    "t-set": "nothing",
                    "t-value": """html_data.update({'data-is-published': 'website_published' in main_object.fields_get() and main_object.website_published,
                    "data-can-publish": 'can_publish' in main_object.fields_get() and main_object.can_publish,
                    "data-editable-in-backend": editable_in_backend,
                })""",
                },
            )
            e4 = util.lxml.etree.Element(
                "t",
                {
                    "t-if": "editable or translatable",
                    "t-set": "nothing",
                    "t-value": """html_data.update({
                                        'data-editable': '1' if editable else None,
                                        'data-translatable': '1' if translatable else None,
                                        'data-view-xmlid': xmlid,
                                        'data-viewid': viewid,
                                        'data-oe-company-name': res_company.name,
                                  })""",
                },
            )
            element_to_replace = arch.find('.//t[@t-set="html_data"]')
            parent = element_to_replace.getparent()
            index = parent.index(element_to_replace)
            parent.remove(element_to_replace)
            parent.insert(index, comment)
            parent.insert(index + 1, e1)
            parent.insert(index + 2, e2)
            parent.insert(index + 3, e3)
            parent.insert(index + 4, e4)

    util.remove_view(cr, "website.user_navbar")
