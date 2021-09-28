import * as React from 'react';
import Partner from '../../../../classes/Partner';
import AppContext from '../../AppContext';
import ContactListItem from '../ContactList/ContactListItem/ContactListItem';
import SectionLeads from '../../SectionLeads/SectionLeads';
import CompanySection from '../../Company/CompanySection/CompanySection';
import SectionTickets from '../../SectionTickets/SectionTickets';
import { ContentType, HttpVerb, sendHttpRequest } from '../../../../utils/httpRequest';
import api from '../../../api';
import EnrichmentInfo, { EnrichmentInfoType } from '../../../../classes/EnrichmentInfo';
import { Spinner, SpinnerSize } from 'office-ui-fabric-react';
import { OdooTheme } from '../../../../utils/Themes';
import './ContactPage.css';
import Lead from '../../../../classes/Lead';
import HelpdeskTicket from '../../../../classes/HelpdeskTicket';
import SectionTasks from '../../SectionTasks/SectionTasks';
import Task from '../../../../classes/Task';

type ContactPageProps = {
    partner: Partner;
    onPartnerChanged?: (Partner) => void;
    loadPartner: boolean;
};

type ContactPageState = {
    partner: Partner;
    isLoading: boolean;
};

class ContactPage extends React.Component<ContactPageProps, ContactPageState> {
    constructor(props, context) {
        super(props, context);
        this.state = { partner: props.partner, isLoading: true };
    }

    private fetchContact = () => {
        const partner = this.props.partner;

        const requestData = this.props.partner.isAddedToDatabase()
            ? { partner_id: partner.id }
            : { email: partner.email, name: partner.name };

        const partnerRequest = sendHttpRequest(
            HttpVerb.POST,
            api.baseURL + api.getPartner,
            ContentType.Json,
            this.context.getConnectionToken(),
            requestData,
            true,
        );

        this.context.addRequestCanceller(partnerRequest.cancel);

        partnerRequest.promise
            .then((response) => {
                const parsed = JSON.parse(response);
                const partner = Partner.fromJSON(parsed.result.partner);
                if (parsed.result.leads) {
                    partner.leads = parsed.result.leads.map((lead_json) => Lead.fromJSON(lead_json));
                }
                if (parsed.result.tasks) {
                    partner.tasks = parsed.result.tasks.map((task_json) => Task.fromJSON(task_json));
                }
                if (parsed.result.tickets) {
                    partner.tickets = parsed.result.tickets.map((ticket_json) => HelpdeskTicket.fromJSON(ticket_json));
                }
                if (parsed.result.user_companies) {
                    this.context.setUserCompanies(parsed.result.user_companies);
                }
                this.setState({ partner: partner, isLoading: false });
                if (parsed.result.partner['enrichment_info']) {
                    const enrichmentInfo = new EnrichmentInfo(
                        parsed.result.partner['enrichment_info'].type,
                        parsed.result.partner['enrichment_info'].info,
                    );
                    if (enrichmentInfo.type != EnrichmentInfoType.NoData)
                        this.context.showTopBarMessage(enrichmentInfo);
                }
                this.propagatePartnerInfoChange(partner);
            })
            .catch((error) => {
                this.context.showHttpErrorMessage(error);
                this.setState({ isLoading: false });
            });
    };

    private isCrmInstalled = (): boolean => {
        return this.props.partner.leads !== undefined;
    };

    private isProjectInstalled = (): boolean => {
        return this.props.partner.tasks !== undefined;
    };

    private isHelpdeskInstalled = (): boolean => {
        return this.props.partner.tickets !== undefined;
    };

    private propagatePartnerInfoChange = (partner: Partner) => {
        this.setState({ partner: partner });
        this.props.onPartnerChanged(partner);
    };

    viewContact = (partner) => {
        const cids = this.context.getUserCompaniesString();
        const url = `${api.baseURL}/web#id=${partner.id}&model=res.partner&view_type=form${cids}`;
        window.open(url, '_blank');
    };

    componentDidMount() {
        if (this.props.loadPartner && this.context.isConnected()) this.fetchContact();
        else this.setState({ isLoading: false, partner: this.props.partner });
    }

    render() {
        if (this.state.isLoading) {
            return <Spinner className="contact-spinner" size={SpinnerSize.large} theme={OdooTheme} />;
        }

        const leadsList = this.isCrmInstalled() && <SectionLeads partner={this.state.partner} />;

        const tasksList = this.isProjectInstalled() && <SectionTasks partner={this.state.partner} />;

        const ticketsList = this.isHelpdeskInstalled() && <SectionTickets partner={this.state.partner} />;

        const onItemClick = this.props.partner.isAddedToDatabase() ? this.viewContact : null;

        return (
            <div className="contact-page">
                <div className="section-card">
                    <ContactListItem partner={this.props.partner} onItemClick={onItemClick} />
                </div>
                {leadsList}
                {tasksList}
                {ticketsList}
                <CompanySection
                    partner={this.state.partner}
                    onPartnerInfoChanged={this.propagatePartnerInfoChange}
                    hideCollapseButton={!leadsList && !tasksList && !ticketsList}
                />
            </div>
        );
    }
}

ContactPage.contextType = AppContext;

export default ContactPage;
