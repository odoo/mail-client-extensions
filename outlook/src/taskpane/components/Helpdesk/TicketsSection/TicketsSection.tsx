import Partner from '../../../../classes/Partner';
import HelpdeskTicket from '../../../../classes/HelpdeskTicket';
import * as React from 'react';
import CollapseSection from '../../CollapseSection/CollapseSection';
import api from '../../../api';
import AppContext from '../../AppContext';
import '../../../../utils/ListItem.css';
import TicketListItem from '../TicketList/TicketListItem';
import { ContentType, HttpVerb, sendHttpRequest } from '../../../../utils/httpRequest';
import { _t } from '../../../../utils/Translator';

type TicketsSectionProps = {
    partner: Partner;
};

type TicketsSectionState = {
    tickets: HelpdeskTicket[];
    isCollapsed: boolean;
};

class TicketsSection extends React.Component<TicketsSectionProps, TicketsSectionState> {
    constructor(props, context) {
        super(props, context);
        const isCollapsed = !props.partner.tickets || !props.partner.tickets.length;
        this.state = { tickets: this.props.partner.tickets, isCollapsed: isCollapsed };
    }

    private createTicketRequest = () => {
        Office.context.mailbox.item.body.getAsync(Office.CoercionType.Html, async (result) => {
            const message = result.value.split('<div id="x_appendonsend"></div>')[0]; // Remove the history and only log the most recent message.
            const subject = Office.context.mailbox.item.subject;

            const requestJson = {
                partner_id: this.props.partner.id,
                email_body: message,
                email_subject: subject,
            };

            let response = null;
            try {
                response = await sendHttpRequest(
                    HttpVerb.POST,
                    api.baseURL + api.createTicket,
                    ContentType.Json,
                    this.context.getConnectionToken(),
                    requestJson,
                    true,
                ).promise;
            } catch (error) {
                this.context.showHttpErrorMessage(error);
                return;
            }

            const parsed = JSON.parse(response);
            if (parsed['error']) {
                this.context.showTopBarMessage();
                return;
            }

            const cids = this.context.getUserCompaniesString();
            const action = 'helpdesk_mail_plugin.helpdesk_ticket_action_form_edit';
            const url = `${api.baseURL}/web#action=${action}&id=${parsed.result.ticket_id}&model=helpdesk.ticket&view_type=form${cids}`;
            window.open(url);
        });
    };

    render() {
        let ticketsExpanded = null;

        if (!this.props.partner.isAddedToDatabase()) {
            ticketsExpanded = <div className="list-text">{_t('Save Contact to create new Tickets.')}</div>;
        } else if (this.state.tickets.length > 0) {
            const ticketsList = this.state.tickets
                .sort((t1, t2) => Number(t1.isClosed) - Number(t2.isClosed))
                .map((ticket) => <TicketListItem ticket={ticket} key={ticket.id} />);
            ticketsExpanded = <div className="section-content">{ticketsList}</div>;
        } else {
            ticketsExpanded = <div className="list-text">{_t('No tickets found for this contact.')}</div>;
        }

        const title = this.state.tickets
            ? _t('Tickets (%(count)s)', { count: this.state.tickets.length })
            : _t('Tickets');

        return (
            <CollapseSection
                isCollapsed={this.state.isCollapsed}
                title={title}
                hasAddButton={this.props.partner.isAddedToDatabase()}
                onAddButtonClick={this.createTicketRequest}>
                {ticketsExpanded}
            </CollapseSection>
        );
    }
}
TicketsSection.contextType = AppContext;
export default TicketsSection;
