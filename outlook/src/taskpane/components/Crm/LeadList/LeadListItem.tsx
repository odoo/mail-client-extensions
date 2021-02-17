import * as React from "react";
import Lead from "../../../../classes/Lead";
import "./LeadListItem.css";
import "../../Contact/ContactList/ContactListItem/ContactListItem.css";
import api from "../../../api";
import Logger from "../../Log/Logger";
import "../../../../utils/ListItem.css"

type LeadsListItemProps = {
    lead: Lead;
};


const LeadListItem = (props: LeadsListItemProps) => {

    const openInOdoo = () => {
        let url = api.baseURL+`/web#id=${props.lead.id}&model=crm.lead&view_type=form`;
        window.open(url,"_blank");
    }

    let expectedRevenueString = props.lead.expectedRevenue+" at "+props.lead.probability+"%";

    if (props.lead.recurringPlan)
    {
        expectedRevenueString = props.lead.expectedRevenue+ " + "+props.lead.recurringRevenue
            +" "+props.lead.recurringPlan
            +" at "+props.lead.probability+"%";
    }

    let expectedRevenuesText = (
        <div className="lead-list-item-revenue-text">
            {expectedRevenueString}
        </div>
    );

    return (
        <div className="list-item-root-container" onClick={openInOdoo}>
            <div className="list-item-container">
                <div className="list-item-info-container">
                    <div className="list-item-title-text">
                        {props.lead.name}
                    </div>
                    {expectedRevenuesText}
                </div>
                <Logger resId={props.lead.id} model="crm.lead" tooltipContent="Log Email Into Lead"/>
            </div>
        </div>
    );

}

export default LeadListItem;
