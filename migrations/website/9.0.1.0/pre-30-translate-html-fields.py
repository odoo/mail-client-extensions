# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _get_tr(cr, lang, model, field):
    table = util.table_of_model(cr, model)
    if not util.column_exists(cr, table, field):
        return
    l = locals()
    cr.execute("""
        UPDATE {table} a
           SET {field}=t.value
          FROM ir_translation t
         WHERE t.type = 'model'
           AND t.name = concat(%(model)s, ',', %(field)s)
           AND t.res_id = a.id
           AND t.src = a.{field}
           AND t.value IS NOT NULL
           AND t.lang = %(lang)s
    """.format(**l), l)

def migrate(cr, version):
    # translated html fields are impossible to migrate.
    # in 8.0, they were translated as a blob.
    # in 9.0, they are now splitted on tags.
    # Doing the splitting ourself and matching the corresponding part in the splitted translation
    # is not possible (number of tag may differ)
    # We can mitigate this if the website only have one lang available.
    # In this case, we will just copy translated blob inside the original document.

    cr.execute("SELECT l.code FROM website_lang_rel r JOIN res_lang l ON (l.id = r.lang_id)")
    if cr.rowcount != 1:
        return
    [lang] = cr.fetchone()
    if lang == 'en_US':
        # XXX we can have a translation for en_US. Should we still do it?
        return

    # module: event
    _get_tr(cr, lang, 'event.event', 'description')

    # module: payment
    for msg in 'pre post pending done cancel error'.split():
        _get_tr(cr, lang, 'payment.acquirer', msg + '_msg')

    # module: survey
    _get_tr(cr, lang, 'survey.survey', 'description')
    _get_tr(cr, lang, 'survey.survey', 'thank_you_message')
    _get_tr(cr, lang, 'survey.page', 'description')
    _get_tr(cr, lang, 'survey.question', 'description')

    # module: website_blog
    _get_tr(cr, lang, 'blog.post', 'content')

    # module: website_event_track
    _get_tr(cr, lang, 'event.track', 'description')

    # module: website_forum
    _get_tr(cr, lang, 'forum.forum', 'faq')

    # module: website_forum_doc
    _get_tr(cr, lang, 'forum.documentation.toc', 'introduction')

    # module: website_hr_recruitment
    _get_tr(cr, lang, 'hr.job', 'website_description')

    # module: website_quote
    _get_tr(cr, lang, 'sale.quote.template', 'website_description')
    _get_tr(cr, lang, 'sale.order', 'website_description')
    _get_tr(cr, lang, 'sale.quote.option', 'website_description')

    # module: website_sale
    _get_tr(cr, lang, 'product.template', 'website_description')

    # module: website_slide
    _get_tr(cr, lang, 'slide.channel', 'description')
    _get_tr(cr, lang, 'slide.channel', 'access_error_msg')
