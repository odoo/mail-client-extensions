from copy import deepcopy

from lxml import etree

from odoo.upgrade import util


def migrate(cr, version):
    # fetch the new arch
    cr.execute(
        """
        SELECT arch_db->>'en_US'
          FROM ir_ui_view view
          JOIN ir_model_data imd
            ON imd.res_id = view.id
         WHERE imd.name = 's_newsletter_subscribe_form'
           AND imd.module = 'website_mass_mailing'
        """
    )
    if cr.rowcount:
        arch = etree.fromstring(cr.fetchone()[0])
        new_subs_divs = arch.xpath(".//div[contains(@class, 's_newsletter_subscribe_form')]")[0]

        # fetch the views where old arch is present and update them
        cr.execute(
            r"""
            SELECT id
              FROM ir_ui_view
             WHERE arch_db->>'en_US' ILIKE '%s\_newsletter\_subscribe\_form%'
               AND website_id IS NOT NULL
            """
        )
        children = new_subs_divs.getchildren()
        for (view,) in cr.fetchall():
            with util.skippable_cm(), util.edit_view(cr, view_id=view) as arch:
                for newsletter_div in arch.xpath("//div[@data-snippet='s_newsletter_subscribe_form']"):
                    newsletter_div[:] = deepcopy(children)
