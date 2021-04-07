import * as React from "react";
import Lead from "../../../../classes/Lead";
import "./LeadListItem.css";
import "../../Contact/ContactList/ContactListItem/ContactListItem.css";
import api from "../../../api";
import Logger from "../../Log/Logger";
import "../../../../utils/ListItem.css"
import { _t } from "../../../../utils/Translator";

type LeadsListItemProps = {
    lead: Lead;
};


const LeadListItem = (props: LeadsListItemProps) => {

    const openInOdoo = () => {
        let url = api.baseURL+`/web#id=${props.lead.id}&model=crm.lead&view_type=form`;
        window.open(url,"_blank");
    }

    let expectedRevenueString = _t("%(expected_revenue)s at %(probability)s%", {
        expected_revenue: props.lead.expectedRevenue,
        probability: props.lead.probability
    });

    if (props.lead.recurringPlan)
    {
        expectedRevenueString = _t("%(expected_revenue)s + %(recurring_revenue)s %(recurring_plan)s at %(probability)s%", {
            expected_revenue: props.lead.expectedRevenue,
            recurring_revenue: props.lead.recurringRevenue,
            recurring_plan: props.lead.recurringPlan,
            probability: props.lead.probability
        });
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
                <Logger resId={props.lead.id} model="crm.lead" tooltipContent={_t("Log Email Into Lead")}/>
            </div>
        </div>
    );

}

export default LeadListItem;
