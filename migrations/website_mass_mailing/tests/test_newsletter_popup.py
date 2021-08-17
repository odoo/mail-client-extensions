# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.5")
class TestNewsletterPopup(UpgradeCase):
    def prepare(self):
        content = """<section class="s_text_block o_colored_level" data-snippet="s_text_block">
            <div class="container">
                <div class="row s_nb_column_fixed no-gutters">
                    <div class="col-lg-8 offset-lg-2 pt32 pb32">
                        <div class="s_newsletter_subscribe_form js_subscribe" data-vxml="001" data-list-id="0"
                             data-snippet="s_newsletter_subscribe_form">
                            <div class="input-group">
                                <input type="email" name="email" class="js_subscribe_email form-control"
                                       placeholder="your email..."/>
                                <span class="input-group-append">
                                    <a role="button" href="#" class="btn btn-primary js_subscribe_btn o_submit">Subscribe</a>
                                    <a role="button" href="#" class="btn btn-success js_subscribed_btn d-none o_submit"
                                       disabled="disabled">Thanks</a>
                                </span>
                                %s
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>"""
        mailing_list = self.env["mailing.list"].create({"name": "Mailing List Test Migration"})
        w1_popup = self.env["website.mass_mailing.popup"].create(
            {"mailing_list_id": mailing_list.id, "popup_content": content % "<website1/>", "website_id": 1}
        )
        w2_popup = self.env["website.mass_mailing.popup"].create(
            {"mailing_list_id": mailing_list.id, "popup_content": content % "<website2/>", "website_id": 2}
        )

        # popup is root element, as product.website_description
        view_w1 = self.env["ir.ui.view"].create(
            {
                "arch": f"""<div class="o_newsletter_popup o_snippet_invisible" data-list-id="{mailing_list.id}"
                data-snippet="s_newsletter_subscribe_popup" data-name="Newsletter Popup" data-invisible="1"/>""",
                "type": "qweb",
                "website_id": 1,
            }
        )
        # popup is not root element, as for regular pages edition
        view_w2 = self.env["ir.ui.view"].create(
            {
                "arch": f"""<tag><div class="o_newsletter_popup o_snippet_invisible" data-list-id="{mailing_list.id}"
                data-snippet="s_newsletter_subscribe_popup" data-name="Newsletter Popup" data-invisible="1"/></tag>""",
                "type": "qweb",
                "website_id": 2,
            }
        )

        return {
            "mailing_list_id": mailing_list.id,
            "view_w1": view_w1.id,
            "view_w2": view_w2.id,
            "w1_popup_content": w1_popup.popup_content,
            "w2_popup_content": w2_popup.popup_content,
        }

    def check(self, init):
        """Only an empty `<div/>` was stored inside the `ir.ui.view.arch_db`:
        <div class="o_newsletter_popup" data-list-id="${mailing_list.id}" [...]/>
        The popup content was stored inside `website.mass_mailing.popup`
        table and retrieved in JS by RPC, based on the current website and the
        `data-list-id` attribute.

        After migration, the popup content should now have been moved directly
        inside the `ir.ui.view.arch_db`, as it now uses the behavior of the
        regular `s_popup` and `s_newsletter_subscribe_form`."""
        View = self.env["ir.ui.view"]

        def check_website(website_id):
            view_arch = View.browse(init["view_w%s" % website_id]).arch_db.replace("\n", "").replace(" ", "")
            popup_content = init["w%s_popup_content" % website_id].replace("\n", "").replace(" ", "")

            # Shouldn't be an exact match as the `data-list-id` from `.s_newsletter_subscribe_form`
            # was 0 but is now set to the `mailing.list`'s ID."
            self.assertNotIn(popup_content, view_arch)

            # replace the list-id to be able to check if exact match
            popup_content = popup_content.replace('data-list-id="0"', 'data-list-id="%s"' % init["mailing_list_id"])

            self.assertIn(
                popup_content,
                view_arch,
                "Popup content should have been move from `website.mass_mailing.popup` to the arch (website %s)."
                % website_id,
            )
            self.assertIn(
                "<website%s/>" % website_id,
                view_arch,
                "The popup content for the correct website (%s) should have been retrieved." % website_id,
            )

        check_website("1")
        check_website("2")
