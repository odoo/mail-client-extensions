# -*- coding: utf-8 -*-
from lxml import etree
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    with util.skippable_cm(), util.edit_view(cr, 'website.footer_custom') as arch:
        favicon = etree.fromstring('''
            <link rel="shortcut icon" type="image/x-icon" t-attf-href="/web/image/website/{{website.id}}/favicon/"/>
        ''')
        head = arch.find('.//head')
        head.append(favicon)
