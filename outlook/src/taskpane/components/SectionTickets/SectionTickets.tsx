import Partner from '../../../classes/Partner';
import HelpdeskTicket from '../../../classes/HelpdeskTicket';
import * as React from 'react';
import api from '../../api';
import AppContext from '../AppContext';
import Section from '../Section/Section';
import { _t } from '../../../utils/Translator';

type SectionTicketsProps = {
    partner: Partner;
    canCreatePartner: boolean;
};

type SectionTicketsState = {
    tickets: HelpdeskTicket[];
};

class SectionTickets extends React.Component<SectionTicketsProps, SectionTicketsState> {
    constructor(props, context) {
        super(props, context);
        const sortedTicket = this.props.partner.tickets.sort((t1, t2) => Number(t1.isClosed) - Number(t2.isClosed));
        this.state = { tickets: sortedTicket };
    }

    render() {
        return (
            <Section
                records={this.state.tickets}
                partner={this.props.partner}
                canCreatePartner={this.props.canCreatePartner}
                model="helpdesk.ticket"
                odooEndpointCreateRecord={api.createTicket}
                odooRecordIdName="ticket_id"
                odooRedirectAction="helpdesk_mail_plugin.helpdesk_ticket_action_form_edit"
                title="Tickets"
                titleCount="Tickets (%(count)s)"
                msgNoPartner="Save Contact to create new Tickets.."
                msgNoPartnerNoAccess="The Contact needs to exist to create Ticket."
                msgNoRecord="No tickets found for this contact."
                msgLogEmail="Log Email Into Ticket"
                getRecordDescription={(ticket) => ticket.isClosed && _t('Closed')}
            />
        );
    }
}
SectionTickets.contextType = AppContext;
export default SectionTickets;
