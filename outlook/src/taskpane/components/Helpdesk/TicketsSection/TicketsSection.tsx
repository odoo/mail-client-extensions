import Partner from "../../../../classes/Partner";
import HelpdeskTicket from "../../../../classes/HelpdeskTicket";
import * as React from "react";
import CollapseSection from "../../CollapseSection/CollapseSection";
import api from "../../../api";
import AppContext from '../../AppContext';
import "../../../../utils/ListItem.css";
import TicketListItem from "../TicketList/TicketListItem";
import {ContentType, HttpVerb, sendHttpRequest} from "../../../../utils/httpRequest";

type TicketsSectionProps = {
    partner: Partner;
}

type TicketsSectionState = {
    tickets: HelpdeskTicket[];
    isCollapsed: boolean;
}


class TicketsSection extends React.Component<TicketsSectionProps, TicketsSectionState> {

    constructor(props, context) {
        super(props, context);
        let isCollapsed = true;
        if (props.partner.tickets && props.partner.tickets.length > 0)
        {
            isCollapsed = false;
        }
        this.state = {tickets: this.props.partner.tickets, isCollapsed: isCollapsed};
    }

    private createTicketRequest = () => {

        Office.context.mailbox.item.body.getAsync(Office.CoercionType.Html, (result) =>
        {
            const message = result.value.split('<div id="x_appendonsend"></div>')[0]; // Remove the history and only log the most recent message.
            const subject = Office.context.mailbox.item.subject;

            const requestJson = {
                partner_id: this.props.partner.id,
                email_body: message,
                email_subject: subject
            }

            const createTicketRequest = sendHttpRequest(HttpVerb.POST, api.baseURL + api.createTicket,
                ContentType.Json,
                this.context.getConnectionToken(), requestJson, true);
            createTicketRequest.promise.then(response => {
                const parsed = JSON.parse(response);
                if (parsed['error']){
                    this.context.showTopBarMessage();
                    return;
                }
                else
                {
                    const action = "helpdesk_mail_plugin.helpdesk_ticket_action_form_edit";
                    const url = api.baseURL + `/web#action=${action}&id=${parsed.result.ticket_id}&model=helpdesk.ticket&view_type=form`;
                    window.open(url);
                }
            }).catch(error => {
                this.context.showHttpErrorMessage(error);
                console.log(error);
            });
        });
    }

    private onCollapseButtonClick = () => {
        this.setState({isCollapsed:!this.state.isCollapsed});
    };

    render() {

        let ticketsExpanded = null;

        let title = "Tickets";

        if (!this.props.partner.isAddedToDatabase())
        {
            if (!this.state.isCollapsed)
            {
                ticketsExpanded = (
                    <div className="list-text">
                        Save Contact to create new Tickets.
                    </div>
                );
            }
        }
        else
        {
            if (!this.state.isCollapsed)
            {
                let leadsContent = null;
                if (this.state.tickets.length > 0)
                {
                    const closedTickets = this.state.tickets.filter(ticket => ticket.isClosed);
                    const openTickets = this.state.tickets.filter(ticket => !ticket.isClosed);

                    const sortedTickets = openTickets.concat(closedTickets);

                    let ticketsList = sortedTickets.map(ticket => {
                        return (
                            <TicketListItem ticket={ticket} key={ticket.id}/>)
                    });
                    leadsContent = (
                        <div>
                            {ticketsList}
                        </div>
                    )
                }
                else
                {
                    leadsContent = (
                        <div className="list-text">
                            No tickets found for this contact
                        </div>
                    );
                }
                ticketsExpanded = (
                    <div className="section-content">
                        {leadsContent}
                    </div>
                );
            }
        }


        if (this.state.tickets)
            title = `Tickets (${this.state.tickets.length})`;

        return (
            <>
                    <CollapseSection onCollapseButtonClick={this.onCollapseButtonClick}
                                     isCollapsed={this.state.isCollapsed} title={title} hasAddButton={(this.props.partner.isAddedToDatabase())}
                                     onAddButtonClick={this.createTicketRequest}>
                        {ticketsExpanded}
                    </CollapseSection>
            </>
        )
    }

}
TicketsSection.contextType = AppContext;
export default TicketsSection;