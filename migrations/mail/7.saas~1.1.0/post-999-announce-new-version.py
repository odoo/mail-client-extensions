# -*- coding: utf-8 -*-

from openerp import release, SUPERUSER_ID
from openerp.modules.registry import RegistryManager

def migrate(cr, version):
    registry = RegistryManager.get(cr.dbname)
    IMD = registry['ir.model.data']
    try:
        poster = IMD.get_object_reference(cr, SUPERUSER_ID, 'mail', 'group_all_employees')
    except ValueError:
        # Cannot found group, post the message on the wall of the admin
        poster = registry['res.users'].browse(cr, SUPERUSER_ID, SUPERUSER_ID)

    if not poster.exists():
        return

    message = """
        <p>OpenERP has been upgraded to version {version}.</p>
        <h2>What&#39;s new in this upgrade?</h2>

        <ul>
            <li><strong>New instant messaging</strong> system, directly integrated in your working environment. Install the new Instant Messaging App, click on the new chat icon in the top right and get started!</li>
            <li><strong>Improved Sales Teams</strong>. CRM Sales Teams are now displayed only if you need them, there is a new option to toggle them in the Sales Settings menu (&quot;<em>Use Sales Teams</em>&quot; option in <em>Settings/Configuration/Sales</em>). When enabled, a new Sales Team menu will appear in your Sales menu, giving you a central dashboard with a quick overview of all Leads, Opportunities, Quotations, Invoices and the monthly turnover, by Sales Team.<br />
            And we&#39;re already working on more widgets and performance indicators that will be added to this dashboard in the next upgrade!</li>
            <li><strong>Enhanced mass-mailing</strong> features, specifically designed for the CRM. Whenever you&#39;re composing a mass-mail on Leads/Opportunities, you can now choose whether the message should appear in the history of the corresponding documents, whether the followers should be notified, and whether you want replies to end up in the document history or to be sent to a different email (for example the email of another sales team).</li>
            <li><strong>Recurrent Invoices on Contracts</strong>. If you use contracts (you can enable Contracts via <em>Settings/Sales/Contracts Management</em>), you will see a new option on every contract: <em>Generate recurring invoices automatically<strong>.</strong></em> This lets you define a recurrence interval, a start date and some template invoice lines, and the system will automatically create draft invoices for you.</li>
            <li>Plus a ton of various performance improvements and small bugfixes</li>
        </ul>

        <p>Enjoy the new OpenERP Online!</p>
    """.format(version=release.version)

    poster.message_post(message, type='notification', subtype='mail.mt_comment')
