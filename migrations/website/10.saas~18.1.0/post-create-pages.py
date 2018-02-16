# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):

    # create a redirection for created pages
    R = util.env(cr)['website.redirect']
    redirects = {
        'website.homepage': '/',
        'website.contactus': '/conctactus',
        'website.aboutus': '/aboutus',
        # from other modules...
        'website_crm.contactus_thanks': '/contactus-thank-you',
        'website_hr_recruitment.thankyou': '/job-thank-you',
    }
    for f, t in redirects.items():
        if not util.ref(cr, f):
            continue
        R.create(dict(url_from='/page/' + f, url_to=t, type='302'))
        if f.startswith('website.'):
            R.create(dict(url_from='/page/' + f[8:], url_to=t, type='302'))

    # create pages
    cr.execute("""
        WITH views AS (
             SELECT id,
                    CONCAT('/page/', CASE WHEN substr(key, 1, 8) = 'website.' THEN substr(key, 9)
                                          ELSE key END) as url,
                    website_id
               FROM ir_ui_view v
              WHERE page=true
                AND type='qweb'
                AND NOT EXISTS(SELECT 1 FROM website_page WHERE view_id=v.id)
        ),
        pages AS (
            INSERT INTO website_page(url, view_id, website_published, website_indexed)
                 SELECT url, id, true, true
                   FROM views
              RETURNING id, view_id
        ),
        _m2m_website AS (
            INSERT INTO website_website_page_rel(website_page_id, website_id)
                 SELECT p.id, v.website_id
                   FROM pages p
                   JOIN views v ON (v.id = p.view_id)
                  WHERE v.website_id IS NOT NULL
        )
        UPDATE website_menu m
           SET page_id = p.id
          FROM pages p, views v
         WHERE v.id = p.view_id
           AND (   m.url = v.url
                OR (    substr(m.url, 1, 14) = '/page/website.'
                    AND v.url = CONCAT('/page/', substr(m.url, 15)))
           )
           -- https://modern-sql.com/feature/is-distinct-from
           AND m.website_id IS NOT DISTINCT FROM v.website_id
    """)

    # redirect 'website.' pages to naked version
    cr.execute("""
        SELECT key
          FROM ir_ui_view
         WHERE page=true
           AND type='qweb'
           AND key LIKE 'website.%'
    """)
    for key, in cr.fetchall():
        R.create(dict(url_from='/page/' + key, url_to='/page/' + key[8:], type='302'))
