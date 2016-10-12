# -*- coding: utf-8 -*-
from lxml import etree

from openerp.tools.translate import TRANSLATED_ATTRS, encode
from openerp.addons.base.maintenance.migrations import util
from openerp.addons.base.ir.ir_ui_view import TRANSLATED_ATTRS_RE
from openerp.tools.view_validation import valid_view

def migrate(cr, version):
    # check for custom views that inherit on translated attributes
    # this check is normatlly done at the end of the migration but an early fail will help
    msgs = []
    arch_col = 'arch_db' if util.column_exists(cr, 'ir_ui_view', 'arch_db') else 'arch'
    cr.execute("""
          SELECT v.id, {arch_col}
            FROM ir_ui_view v
       LEFT JOIN ir_model_data md ON (md.model = 'ir.ui.view' AND md.res_id = v.id)
           WHERE md.module IS NULL
             AND v.active = true
    """.format(arch_col=arch_col))
    for vid, arch_xml in cr.fetchall():
        try:
            arch = etree.fromstring(encode(arch_xml))
        except etree.XMLSyntaxError:
            msgs.append('Invalid XML arch for view %d' % vid)
            continue
        for node in arch.xpath('//*[@position]'):
            # inheritance may not use a translated attribute as selector
            if node.tag == 'xpath':
                match = TRANSLATED_ATTRS_RE.search(node.get('expr', ''))
                if match:
                    message = "View #%d: inheritance may not use attribute %r as a selector." % (vid, match.group(1))
                    msgs.append(message)
            else:
                for attr in TRANSLATED_ATTRS:
                    if node.get(attr):
                        message = "View #%d: inheritance may not use attribute %r as a selector." % (vid, attr)
                        msgs.append(message)
        if not valid_view(arch):
            msgs.append('View #%d invalid: see log' % vid)

    if msgs:
        msgs.insert(0, 'Custom view validation failed:')
        raise util.MigrationError('\n'.join(msgs))
