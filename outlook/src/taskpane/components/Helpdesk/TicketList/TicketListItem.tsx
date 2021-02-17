import * as React from "react";
import HelpdeskTicket from "../../../../classes/HelpdeskTicket";
import '../../../../utils/ListItem.css'
import api from "../../../api";
import Logger from "../../Log/Logger";

type TicketListItemProps = {
    ticket: HelpdeskTicket
};


const TicketListItem = (props: TicketListItemProps) => {

    const openInOdoo = () => {
        let url = api.baseURL+`/web#id=${props.ticket.id}&model=helpdesk.ticket&view_type=form`;
        window.open(url,"_blank");
    }

    let closedText = null;

    if (props.ticket.isClosed)
    {
        closedText = (<div className="muted-text" style={{marginTop: "8px", fontSize: "14px"}}>Closed</div>)
    }

    return (
        <div className="list-item-root-container" onClick={openInOdoo}>
            <div className="list-item-container">
                <div className="list-item-info-container">
                    <div className="list-item-title-text">
                        {props.ticket.name}
                    </div>
                    {closedText}
                </div>
                <Logger resId={props.ticket.id} model="helpdesk.ticket" tooltipContent="Log Email Into Ticket"/>
            </div>
        </div>
    );

}

export default TicketListItem;
