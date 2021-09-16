import * as React from 'react';
import { ProfileCard, ProfileCardProps } from '../../ProfileCard/ProfileCard';

import AppContext from '../../AppContext';
import { ContentType, HttpVerb, sendHttpRequest } from '../../../../utils/httpRequest';
import Partner from '../../../../classes/Partner';

import api from '../../../api';
import Company, { EnrichmentStatus } from '../../../../classes/Company';

import './CompanySection.css';
import {
    faBuilding,
    faDollarSign,
    faGlobeEurope,
    faIndustry,
    faInfo,
    faKey,
    faMapMarkerAlt,
    faPersonBooth,
    faPhone,
} from '@fortawesome/free-solid-svg-icons';
import CompanyInfoItem from '../CompanyInfoItem';
import CollapseSection from '../../CollapseSection/CollapseSection';
import CompanyCache from '../../../../classes/CompanyCache';
import EnrichmentInfo, { EnrichmentInfoType } from '../../../../classes/EnrichmentInfo';
import { Spinner, SpinnerSize } from 'office-ui-fabric-react';
import { OdooTheme } from '../../../../utils/Themes';
import { _t } from '../../../../utils/Translator';

type CompanySectionProps = {
    partner: Partner;
    onPartnerInfoChanged?: (partner: Partner) => void;
    hideCollapseButton: boolean;
};
type CompanySectionState = {
    company: Company;
    isCollapsed: boolean;
    isLoading: boolean;
};

class CompanySection extends React.Component<CompanySectionProps, CompanySectionState> {
    constructor(props, context) {
        super(props, context);
        const company = props.partner.company;
        this.state = {
            company: company,
            isCollapsed: false,
            isLoading: false,
        };
        this.companyCache = new CompanyCache(2, 200, 0.25);
    }

    private companyCache: CompanyCache;

    private enrichAndCreate = () => {
        if (!this.props.partner.email) {
            let enrichmentInfo = new EnrichmentInfo(
                EnrichmentInfoType.EnrichContactWithNoEmail,
                _t('This company has no email address and could not be enriched.'),
            );
            this.context.showTopBarMessage(enrichmentInfo);
            return;
        }

        this.setState({ isLoading: true });
        const enrichRequest = sendHttpRequest(
            HttpVerb.POST,
            api.baseURL + api.enrichAndCreate,
            ContentType.Json,
            this.context.getConnectionToken(),
            {
                partner_email: this.props.partner.email,
                partner_id: this.props.partner.id,
                enrich_on_not_exists: true,
            },
            true,
        );
        this.context.addRequestCanceller(enrichRequest.cancel);
        enrichRequest.promise
            .then((response) => {
                const enrichResponse = JSON.parse(response);
                if (enrichResponse.result['enrichment_info']) {
                    const enrichmentInfo = new EnrichmentInfo(
                        enrichResponse.result['enrichment_info'].type,
                        enrichResponse.result['enrichment_info'].info,
                    );
                    this.context.showTopBarMessage(enrichmentInfo);
                }

                const company = Company.fromJSON(enrichResponse.result.company);
                if (company.enrichmentStatus == EnrichmentStatus.enriched) {
                    this.companyCache.add(company);
                }
                this.setState({ isCollapsed: false, company: company, isLoading: false });
                let newPartner = this.props.partner;
                newPartner.company = company;
                this.props.onPartnerInfoChanged(newPartner);
            })
            .catch((error) => {
                console.log(error);
                this.setState({ isCollapsed: false, isLoading: false });
                this.context.showHttpErrorMessage(error);
            });
    };

    private enrichAndUpdate = () => {
        if (!this.props.partner.email) {
            let enrichmentInfo = new EnrichmentInfo(
                EnrichmentInfoType.EnrichContactWithNoEmail,
                _t('This company has no email address and it could not be enriched.'),
            );
            this.context.showTopBarMessage(enrichmentInfo);
            return;
        }

        this.setState({ isLoading: true });

        const enrichRequest = sendHttpRequest(
            HttpVerb.POST,
            api.baseURL + api.enrichAndUpdate,
            ContentType.Json,
            this.context.getConnectionToken(),
            {
                partner_id: this.props.partner.id,
            },
            true,
        );

        this.context.addRequestCanceller(enrichRequest.cancel);

        enrichRequest.promise
            .then((response) => {
                const enrichResponse = JSON.parse(response);

                let enrichmentInfo = null;

                if (enrichResponse.result['enrichment_info']) {
                    enrichmentInfo = new EnrichmentInfo(
                        enrichResponse.result['enrichment_info'].type,
                        enrichResponse.result['enrichment_info'].info,
                    );
                    this.context.showTopBarMessage(enrichmentInfo);
                    if (enrichmentInfo.type == EnrichmentInfoType.InsufficientCredit) {
                        this.setState({ isLoading: false });
                        return;
                    }
                }
                const partner = this.props.partner;
                const company = Company.fromJSON(enrichResponse.result.company, enrichmentInfo);
                this.setState({ company: company, isLoading: false, isCollapsed: false });
                //update partner information
                partner.company = company;
                partner.image = company.image;
                partner.phone = company.phone;
                this.props.onPartnerInfoChanged(partner);
            })
            .catch((error) => {
                console.log(error);
                this.setState({ isCollapsed: false, isLoading: false });
                this.context.showHttpErrorMessage(error);
            });
    };

    private getCompanyInsightsSection = () => {
        const company = this.state.company as Company;

        let addressSection = null;
        let empty = true;

        if (company.getLocation()) {
            addressSection = (
                <CompanyInfoItem
                    icon={faMapMarkerAlt}
                    title={_t('Address')}
                    value={company.getLocation()}
                    hrefContent={`http://maps.google.com/?q=${company.getLocation()}`}
                />
            );
            empty = false;
        }
        let phoneSection = null;
        if (company.getPhone() && !this.props.partner.isCompany) {
            phoneSection = (
                <CompanyInfoItem
                    icon={faPhone}
                    title={_t('Phone')}
                    value={company.getPhone()}
                    hrefContent={`tel:${company.getPhone()}`}
                />
            );
            empty = false;
        }

        let websiteSection = null;
        if (company.getDomain()) {
            websiteSection = (
                <CompanyInfoItem
                    icon={faGlobeEurope}
                    title={_t('Website')}
                    value={company.getDomain()}
                    hrefContent={company.getDomain()}
                />
            );
            empty = false;
        }

        let industrySection = null;
        if (company.getIndustry()) {
            industrySection = (
                <CompanyInfoItem icon={faIndustry} title={_t('Industry')} value={company.getIndustry()} />
            );
            empty = false;
        }

        let employeesSection = null;
        if (company.getEmployees()) {
            employeesSection = (
                <CompanyInfoItem icon={faPersonBooth} title={_t('Employees')} value={company.getEmployees() + ''} />
            );
            empty = false;
        }

        let yearFoundedSection = null;
        if (company.getYearFounded()) {
            yearFoundedSection = (
                <CompanyInfoItem icon={faInfo} title={_t('Year founded')} value={company.getYearFounded() + ''} />
            );
            empty = false;
        }

        let keywordsSection = null;
        if (company.getKeywords()) {
            keywordsSection = <CompanyInfoItem icon={faKey} title={_t('Keywords')} value={company.getKeywords()} />;
            empty = false;
        }

        let companyTypeSection = null;
        if (company.getCompanyType()) {
            companyTypeSection = (
                <CompanyInfoItem icon={faBuilding} title={_t('Company Type')} value={company.getCompanyType()} />
            );
            empty = false;
        }

        let revenueSection = null;
        if (company.getRevenue()) {
            revenueSection = (
                <CompanyInfoItem icon={faDollarSign} title={_t('Revenues')} value={company.getRevenue()} />
            );
            empty = false;
        }

        if (empty && this.props.partner.isCompany) {
            if (company.enrichmentStatus != EnrichmentStatus.enrichmentEmpty) {
                return <div className="insights-empty-info muted-text">{_t('No extra information found')}</div>;
            } else {
                return null;
            }
        }

        const profileCardData: ProfileCardProps = {
            domain: company.getDomain(),
            name: company.getName(),
            email: undefined,
            initials: company.getInitials(),
            icon: company.image ? 'data:image;base64, ' + company.image : company.getLogoURL(),
            job: undefined,
            phone: undefined,
            twitter: company.getTwitter(),
            facebook: company.getFacebook(),
            crunchbase: company.getCrunchbase(),
            linkedin: company.getLinkedin(),
            description: company.getDescription(),
            onClick: this.openInOdoo,
            isCompany: true,
            parentIsCompany: this.props.partner.isCompany,
        };

        return (
            <>
                <ProfileCard {...profileCardData} />
                <div style={{ padding: '8px' }}>
                    {addressSection}
                    {phoneSection}
                    {websiteSection}
                    {industrySection}
                    {employeesSection}
                    {yearFoundedSection}
                    {keywordsSection}
                    {companyTypeSection}
                    {revenueSection}
                </div>
            </>
        );
    };

    private getCompanyEnrichmentAvailableSection = () => {
        if (this.state.company.isAddedToDatabase()) {
            return (
                <div>
                    {this.getCompanyInsightsSection()}
                    <div>
                        <div className="odoo-secondary-button insights-button" onClick={this.enrichAndUpdate}>
                            {_t('Enrich Company')}
                        </div>
                    </div>
                </div>
            );
        } else {
            return (
                <div className="muted-text insights-info">
                    {_t('No company attached to this contact')}
                    <div className="odoo-secondary-button insights-button" onClick={this.enrichAndCreate}>
                        {_t('Create a Company')}
                    </div>
                </div>
            );
        }
    };

    private getCompanyEnrichmentEmptySection = () => {
        let insightsSection = null;
        if (this.context.isConnected()) {
            if (this.state.company.isAddedToDatabase()) {
                return (
                    <div>
                        {this.getCompanyInsightsSection()}
                        <div className="muted-text insights-info">
                            {_t('No additional insights were found for this company')}
                        </div>
                    </div>
                );
            } else {
                return (
                    <div>
                        {insightsSection}
                        <div className="muted-text insights-info">
                            {_t('No company linked to this contact could be enriched or found in Odoo')}
                        </div>
                    </div>
                );
            }
        } else {
            return (
                <div>
                    {insightsSection}
                    <div className="muted-text insights-info">
                        {_t('No company linked to this contact could be enriched')}
                    </div>
                </div>
            );
        }
    };

    //returns the right JSX element based on the enrichment status of the company
    private getCompanySection = () => {
        const company = this.state.company as Company;
        switch (company.enrichmentStatus) {
            case EnrichmentStatus.enriched:
                return this.getCompanyInsightsSection();
            case EnrichmentStatus.enrichmentAvailable:
                return this.getCompanyEnrichmentAvailableSection();
            case EnrichmentStatus.enrichmentEmpty:
                return this.getCompanyEnrichmentEmptySection();
        }
    };

    private openInOdoo = () => {
        if (!this.context.isConnected()) {
            this.context.navigation.goToLogin();
            return;
        }
        let url = api.baseURL + `/web#id=${this.props.partner.company.id}&model=res.partner&view_type=form`;
        window.open(url, '_blank');
    };

    private onCollapseClick = () => {
        this.setState({ isCollapsed: !this.state.isCollapsed });
    };

    render() {
        let content = null;

        if (this.state.isLoading) {
            content = (
                <>
                    <Spinner size={SpinnerSize.large} theme={OdooTheme} style={{ marginBottom: '16px' }} />
                </>
            );
        } else {
            content = this.getCompanySection();
        }

        return (
            <>
                <CollapseSection
                    title={_t('Company Insights')}
                    isCollapsed={this.state.isCollapsed}
                    onCollapseButtonClick={this.onCollapseClick}
                    hideCollapseButton={this.props.hideCollapseButton}>
                    {content}
                </CollapseSection>
            </>
        );
    }
}

CompanySection.contextType = AppContext;
export default CompanySection;
