# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # This should delete nothing as it's
    cr.execute("DELETE FROM ir_translation WHERE type IN ('field', 'report', 'view', 'help')")

    # Those fields are (x|ht)ml_translate
    fields_translations_to_modify = util.splitlines("""

        ir.ui.view,arch_db

        blog.post,content
        digest.tip,tip_description
        event.event,description
        event.track,description

        hr.job,website_description
        im_livechat.channel,website_description

        product.template,quote_description   # will be rename to quotation_only_description later
        product.template.website_description

        sale.order,website_description
        sale.order.line,website_description
        sale.order.option,website_description
        sale.order.template,website_description
        sale.order.template.line,website_description
        sale.order.template.option,website_description

        slide.channel,description
        slide.channel,access_error_msg

    """)

    cr.execute(
        """
        UPDATE ir_translation
           SET type='model_terms'
         WHERE type='model'
           AND name IN %s
    """,
        [tuple(fields_translations_to_modify)],
    )

    # De-duplicate translations
    cr.execute(
        """
        UPDATE ir_translation
           SET type='model_terms'
         WHERE id IN (
             SELECT unnest(array_agg(id))
               FROM ir_translation
              WHERE type='model'
           GROUP BY name, lang, res_id
             HAVING count(id) > 1
        )
    """
    )

    cr.execute(
        """
        DELETE FROM ir_translation WHERE id IN (
             SELECT unnest((array_agg(id ORDER BY id))[2:array_length(array_agg(id), 1)])
               FROM ir_translation
              WHERE type='code'
           GROUP BY lang, md5(src)
             HAVING count(id) > 1
        )
    """
    )

    cr.execute(
        """
        DELETE FROM ir_translation WHERE id IN (
             SELECT unnest((array_agg(id ORDER BY id))[2:array_length(array_agg(id), 1)])
               FROM ir_translation
              WHERE type IN ('selection', 'constraint', 'sql_constraint')
           GROUP BY type, lang, name, md5(src)
             HAVING count(id) > 1
        )
    """
    )
