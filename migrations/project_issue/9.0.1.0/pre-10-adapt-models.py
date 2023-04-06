# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.table_exists(cr, 'project_issue'):
        # fresh install for crm_helpdesk migration
        return
    cr.execute("UPDATE project_issue SET kanban_state='normal' WHERE kanban_state IS NULL")

    # categories -> tags
    cr.execute("""ALTER TABLE project_category_project_issue_rel
                    RENAME TO project_issue_project_tags_rel""")
    cr.execute("""ALTER TABLE project_issue_project_tags_rel
                RENAME COLUMN project_category_id TO project_tags_id""")
    util.update_field_usage(cr, 'project.issue', 'categ_ids', 'tag_ids')

    cr.execute("""
        INSERT INTO project_tags(name)
             SELECT v.name
               FROM project_issue i JOIN project_issue_version v ON (v.id = i.version_id)
              WHERE NOT EXISTS(SELECT 1 FROM project_tags WHERE name=v.name)
           GROUP BY v.name
    """)
    cr.execute("""
        INSERT INTO project_issue_project_tags_rel(project_issue_id, project_tags_id)
             SELECT i.id, t.id
               FROM project_issue i
               JOIN project_issue_version v ON (v.id = i.version_id)
               JOIN project_tags t ON (t.name = v.name)
              WHERE NOT EXISTS(SELECT 1
                                 FROM project_issue_project_tags_rel s
                                WHERE s.project_issue_id = i.id
                                  AND s.project_tags_id = t.id)
    """)

    util.remove_field(cr, 'project.issue', 'version_id')
    util.delete_model(cr, 'project.issue.version')
