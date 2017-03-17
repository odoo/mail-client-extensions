# -*- coding: utf-8 -*-

def migrate(cr, version):
    # description of 'project.task' is now an html field

    cr.execute("""UPDATE project_task
                     SET description=CONCAT('<p>', REPLACE(description, E'\n', '<br>'), '</p>')
                   WHERE description IS NOT NULL
               """)

