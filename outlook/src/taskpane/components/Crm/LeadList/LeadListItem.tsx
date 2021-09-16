import * as React from 'react';
import Lead from '../../../../classes/Lead';
import './LeadListItem.css';
import '../../Contact/ContactList/ContactListItem/ContactListItem.css';
import api from '../../../api';
import Logger from '../../Log/Logger';
import '../../../../utils/ListItem.css';
import { _t } from '../../../../utils/Translator';
import AppContext from '../../AppContext';

type LeadsListItemProps = {
    lead: Lead;
};

class LeadListItem extends React.Component<LeadsListItemProps, {}> {
    openInOdoo = () => {
        const cids = this.context.getUserCompaniesString();
        let url = api.baseURL + `/web#id=${this.props.lead.id}&model=crm.lead&view_type=form${cids}`;
        window.open(url, '_blank');
    };

    render() {
        let expectedRevenueString = _t('%(expected_revenue)s at %(probability)s%', {
            expected_revenue: this.props.lead.expectedRevenue,
            probability: this.props.lead.probability,
        });

        if (this.props.lead.recurringPlan) {
            expectedRevenueString = _t(
                '%(expected_revenue)s + %(recurring_revenue)s %(recurring_plan)s at %(probability)s%',
                {
                    expected_revenue: this.props.lead.expectedRevenue,
                    recurring_revenue: this.props.lead.recurringRevenue,
                    recurring_plan: this.props.lead.recurringPlan,
                    probability: this.props.lead.probability,
                },
            );
        }

        let expectedRevenuesText = <div className="lead-list-item-revenue-text">{expectedRevenueString}</div>;

        return (
            <div className="list-item-root-container" onClick={this.openInOdoo}>
                <div className="list-item-container">
                    <div className="list-item-info-container">
                        <div className="list-item-title-text">{this.props.lead.name}</div>
                        {expectedRevenuesText}
                    </div>
                    <Logger resId={this.props.lead.id} model="crm.lead" tooltipContent={_t('Log Email Into Lead')} />
                </div>
            </div>
        );
    }
}

LeadListItem.contextType = AppContext;

export default LeadListItem;
