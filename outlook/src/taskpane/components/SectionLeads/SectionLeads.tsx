import * as React from 'react';
import Partner from '../../../classes/Partner';

import AppContext from '../AppContext';
import api from '../../api';
import Lead from '../../../classes/Lead';
import ListItem from '../ListItem/ListItem';
import CollapseSection from '../CollapseSection/CollapseSection';

import { ContentType, HttpVerb, sendHttpRequest } from '../../../utils/httpRequest';
import { _t } from '../../../utils/Translator';

type LeadSectionProps = {
    partner: Partner;
};

type SectionLeadsState = {
    leads: Lead[];
    isCollapsed: boolean;
};

class SectionLeads extends React.Component<LeadSectionProps, SectionLeadsState> {
    constructor(props, context) {
        super(props, context);
        const isCollapsed = !props.partner.leads || !props.partner.leads.length;
        this.state = { leads: this.props.partner.leads, isCollapsed: isCollapsed };
    }

    private createOpportunityRequest = () => {
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
                    api.baseURL + api.createLead,
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
            const action = 'crm_mail_plugin.crm_lead_action_form_edit';
            const url = `${api.baseURL}/web#action=${action}&id=${parsed.result.lead_id}&model=crm.lead&view_type=form${cids}`;
            window.open(url);
        });
    };

    private getLeadDescription = (lead): string => {
        const expectedRevenueString = _t(
            lead.recurringPlan
                ? '%(expected_revenue)s + %(recurring_revenue)s %(recurring_plan)s at %(probability)s%'
                : '%(expected_revenue)s at %(probability)s%',
            {
                expected_revenue: lead.expectedRevenue,
                recurring_revenue: lead.recurringRevenue,
                recurring_plan: lead.recurringPlan,
                probability: lead.probability,
            },
        );

        return expectedRevenueString;
    };

    private getSectionLeads = () => {
        if (!this.props.partner.isAddedToDatabase()) {
            return <div className="list-text">{_t('Save Contact to create new Opportunities.')}</div>;
        } else if (this.state.leads.length > 0) {
            return (
                <div className="section-content">
                    {this.state.leads.map((lead) => (
                        <ListItem
                            model="crm.lead"
                            res_id={lead.id}
                            key={lead.id}
                            title={lead.name}
                            description={this.getLeadDescription(lead)}
                            logTitle={_t('Log Email Into Lead')}
                        />
                    ))}
                </div>
            );
        }
        return <div className="list-text">{_t('No opportunities found for this contact.')}</div>;
    };

    render() {
        const leadCount = this.state.leads && this.state.leads.length;
        const title = this.state.leads
            ? _t('Opportunities (%(count)s)', { count: leadCount.toString() })
            : _t('Opportunities');

        return (
            <CollapseSection
                isCollapsed={this.state.isCollapsed}
                title={title}
                hasAddButton={this.props.partner.isAddedToDatabase()}
                onAddButtonClick={this.createOpportunityRequest}>
                {this.getSectionLeads()}
            </CollapseSection>
        );
    }
}

SectionLeads.contextType = AppContext;

export default SectionLeads;
