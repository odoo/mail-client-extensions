# -*- coding: utf-8 -*-

def migrate(cr, version):
    renames = {
        'idea_category_sales': 'idea_cat_0',
        'idea_category_general': 'idea_cat_1',
        'idea_category_technical': 'idea_cat_2',
    }

    for f, t in renames.items():
        cr.execute("UPDATE ir_model_data SET name=%s WHERE module=%s AND name=%s", (t, 'idea', f))
