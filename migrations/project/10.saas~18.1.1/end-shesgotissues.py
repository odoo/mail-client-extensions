# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # create inherited view to show the new field
    vid = util.env(cr)['ir.ui.view'].create({
        'model': 'project.task',
        'name': 'Show Legacy Reference',
        'inherit_id': util.ref(cr, 'project.view_task_form2'),
        'type': 'form',
        'active': False,
        'arch': """<data>
                     <field name='tag_ids' position='after'>
                       <field name='x_original_issue_id'/>
                     </field>
                   </data>""",
    }).id
    cr.execute('UPDATE ir_ui_view SET active=true WHERE id=%s', [vid])
