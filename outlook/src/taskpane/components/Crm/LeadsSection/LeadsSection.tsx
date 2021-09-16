import * as React from 'react';
import Partner from '../../../../classes/Partner';

import AppContext from '../../AppContext';
import api from '../../../api';
import Lead from '../../../../classes/Lead';
import LeadListItem from '../LeadList/LeadListItem';
import CollapseSection from '../../CollapseSection/CollapseSection';

import { ContentType, HttpVerb, sendHttpRequest } from '../../../../utils/httpRequest';
import { _t } from '../../../../utils/Translator';

type LeadSectionProps = {
    partner: Partner;
};

type LeadsSectionState = {
    leads: Lead[];
    isCollapsed: boolean;
};

class LeadsSection extends React.Component<LeadSectionProps, LeadsSectionState> {
    constructor(props, context) {
        super(props, context);
        let isCollapsed = true;
        if (props.partner.leads && props.partner.leads.length > 0) {
            isCollapsed = false;
        }
        this.state = { leads: this.props.partner.leads, isCollapsed: isCollapsed };
    }

    private createOpportunityRequest = () => {
        Office.context.mailbox.item.body.getAsync(Office.CoercionType.Html, (result) => {
            const message = result.value.split('<div id="x_appendonsend"></div>')[0]; // Remove the history and only log the most recent message.
            const subject = Office.context.mailbox.item.subject;

            const requestJson = {
                partner_id: this.props.partner.id,
                email_body: message,
                email_subject: subject,
            };

            const logRequest = sendHttpRequest(
                HttpVerb.POST,
                api.baseURL + api.createLead,
                ContentType.Json,
                this.context.getConnectionToken(),
                requestJson,
                true,
            );
            logRequest.promise
                .then((response) => {
                    const parsed = JSON.parse(response);
                    if (parsed['error']) {
                        this.context.showTopBarMessage();
                        return;
                    } else {
                        const cids = this.context.getUserCompaniesString();
                        const action = 'crm_mail_plugin.crm_lead_action_form_edit';
                        const url =
                            api.baseURL +
                            `/web#action=${action}&id=${parsed.result.lead_id}&model=crm.lead&view_type=form${cids}`;
                        window.open(url);
                    }
                })
                .catch((error) => {
                    this.context.showHttpErrorMessage(error);
                    console.log(error);
                });
        });
    };

    private onCollapseButtonClick = () => {
        this.setState({ isCollapsed: !this.state.isCollapsed });
    };

    render() {
        let leadsExpanded = null;

        let title = _t('Opportunities');

        if (!this.props.partner.isAddedToDatabase()) {
            if (!this.state.isCollapsed) {
                leadsExpanded = <div className="list-text">{_t('Save Contact to create new Opportunities.')}</div>;
            }
        } else {
            if (!this.state.isCollapsed) {
                let leadsContent = null;
                if (this.state.leads.length > 0) {
                    let leads = this.state.leads.map((lead) => {
                        return <LeadListItem lead={lead} key={lead.id} />;
                    });
                    leadsContent = <div className="section-content">{leads}</div>;
                } else {
                    leadsContent = <div className="list-text">{_t('No opportunities found for this contact.')}</div>;
                }
                leadsExpanded = <div>{leadsContent}</div>;
            }
        }

        if (this.state.leads)
            title = _t('Opportunities (%(count)s)', {
                count: this.props.partner.leads.length.toString(),
            });

        return (
            <>
                <CollapseSection
                    onCollapseButtonClick={this.onCollapseButtonClick}
                    isCollapsed={this.state.isCollapsed}
                    title={title}
                    hasAddButton={this.props.partner.isAddedToDatabase()}
                    onAddButtonClick={this.createOpportunityRequest}>
                    {leadsExpanded}
                </CollapseSection>
            </>
        );
    }
}

LeadsSection.contextType = AppContext;

export default LeadsSection;
