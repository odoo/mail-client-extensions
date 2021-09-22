import * as React from 'react';
import HelpdeskTicket from '../../../../classes/HelpdeskTicket';
import '../../../../utils/ListItem.css';
import './TicketListItem.css';
import { _t } from '../../../../utils/Translator';
import api from '../../../api';
import AppContext from '../../AppContext';
import Logger from '../../Log/Logger';

type TicketListItemProps = {
    ticket: HelpdeskTicket;
};

class TicketListItem extends React.Component<TicketListItemProps, {}> {
    openInOdoo = () => {
        const cids = this.context.getUserCompaniesString();
        const url = `${api.baseURL}/web#id=${this.props.ticket.id}&model=helpdesk.ticket&view_type=form${cids}`;
        window.open(url, '_blank');
    };

    render() {
        return (
            <div className="list-item-root-container" onClick={this.openInOdoo}>
                <div className="list-item-container">
                    <div className="list-item-info-container">
                        <div className="list-item-title-text">{this.props.ticket.name}</div>
                        {this.props.ticket.isClosed && <div className="ticket-closed muted-text">{_t('Closed')}</div>}
                    </div>
                    <Logger
                        resId={this.props.ticket.id}
                        model="helpdesk.ticket"
                        tooltipContent={_t('Log Email Into Ticket')}
                    />
                </div>
            </div>
        );
    }
}

TicketListItem.contextType = AppContext;

export default TicketListItem;
