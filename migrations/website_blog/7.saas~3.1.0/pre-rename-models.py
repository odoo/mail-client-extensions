# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.rename_model(cr, 'document.page', 'blog.post')

    cr.execute("""CREATE TABLE blog_blog(
                    id SERIAL NOT NULL,
                    name varchar,
                    PRIMARY KEY(id)
                  )
                """)

    util.create_column(cr, 'blog_post', 'blog_id', 'int4')

    cr.execute("""SELECT id, name
                    FROM blog_post b
                   WHERE type=%s
                     AND EXISTS(SELECT 1
                                  FROM blog_post
                                 WHERE parent_id = b.id
                                   AND type=%s
                                   AND length(trim(coalesce(content, ''))) > 0
                                )
                """, ('category', 'content'))
    for old_id, name in cr.fetchall():
        cr.execute("INSERT INTO blog_blog(name) VALUES(%s) RETURNING id", (name,))
        [blog_id] = cr.fetchone()
        cr.execute("UPDATE blog_post SET blog_id=%s WHERE parent_id=%s", (blog_id, old_id))

    cr.execute("DELETE FROM blog_post WHERE type=%s", ('category',))

    cr.execute("SELECT count(1) FROM blog_post WHERE blog_id IS NULL")
    if cr.fetchone()[0]:
        cr.execute("INSERT INTO blog_blog(name) VALUES(%s) RETURNING id", ('Pages',))
        [blog_id] = cr.fetchone()
        cr.execute("UPDATE blog_post SET blog_id=%s WHERE blog_id IS NULL", (blog_id,))

    util.rename_model(cr, 'document.page.history', 'blog.post.history')
    util.rename_field(cr, 'blog.post.history', 'page_id', 'post_id')
