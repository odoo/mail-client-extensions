import * as React from 'react';
import HelpdeskTicket from '../../../../classes/HelpdeskTicket';
import '../../../../utils/ListItem.css';
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
        let url = api.baseURL + `/web#id=${this.props.ticket.id}&model=helpdesk.ticket&view_type=form${cids}`;
        window.open(url, '_blank');
    };

    render() {
        let closedText = null;

        if (this.props.ticket.isClosed) {
            closedText = (
                <div className="muted-text" style={{ marginTop: '8px', fontSize: '14px' }}>
                    {_t('Closed')}
                </div>
            );
        }

        return (
            <div className="list-item-root-container" onClick={this.openInOdoo}>
                <div className="list-item-container">
                    <div className="list-item-info-container">
                        <div className="list-item-title-text">{this.props.ticket.name}</div>
                        {closedText}
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
