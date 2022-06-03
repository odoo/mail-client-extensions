import * as React from 'react';

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
import CompanySocialIcons from '../CompanySocialIcons';
import CollapseSection from '../../CollapseSection/CollapseSection';
import CompanyCache from '../../../../classes/CompanyCache';
import EnrichmentInfo, { EnrichmentInfoType } from '../../../../classes/EnrichmentInfo';
import { Spinner, SpinnerSize } from 'office-ui-fabric-react';
import { OdooTheme } from '../../../../utils/Themes';
import { _t } from '../../../../utils/Translator';

type CompanySectionProps = {
    partner: Partner;
    canCreatePartner: boolean;
    onPartnerInfoChanged?: (partner: Partner) => void;
    hideCollapseButton: boolean;
};
type CompanySectionState = {
    company: Company;
    isCollapsed: boolean;
    isLoading: boolean;
    hideEnrichmentButton: boolean;
};

const defaultCompanyImageSrc = 'assets/company_image.png';

class CompanySection extends React.Component<CompanySectionProps, CompanySectionState> {
    constructor(props, context) {
        super(props, context);
        const company = props.partner.company;
        this.state = {
            company: company,
            isCollapsed: false,
            isLoading: false,
            hideEnrichmentButton: false,
        };
        this.companyCache = new CompanyCache(2, 200, 0.25);
    }

    private companyCache: CompanyCache;

    private enrichAndCreate = () => {
        if (!this.props.partner.email) {
            const enrichmentInfo = new EnrichmentInfo(
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
                    if (enrichmentInfo.type == EnrichmentInfoType.InsufficientCredit) {
                        this.setState({ hideEnrichmentButton: true });
                    }
                } else if (enrichResponse.result.error && enrichResponse.result.error.length) {
                    this.context.showTopBarMessage(
                        new EnrichmentInfo(EnrichmentInfoType.OdooCustomError, enrichResponse.result.error),
                    );
                    this.setState({ isLoading: false, hideEnrichmentButton: true });
                    return;
                }

                const company = Company.fromJSON(enrichResponse.result.company);
                if (company.enrichmentStatus == EnrichmentStatus.enriched) {
                    this.companyCache.add(company);
                }
                this.setState({ isCollapsed: false, company: company, isLoading: false });
                const newPartner = this.props.partner;
                newPartner.company = company;
                this.props.onPartnerInfoChanged(newPartner);
            })
            .catch((error) => {
                this.setState({ isCollapsed: false, isLoading: false, hideEnrichmentButton: true });
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
                partner_id: this.props.partner.company.id,
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
                        this.setState({ isLoading: false, hideEnrichmentButton: true });
                        return;
                    }
                } else if (enrichResponse.result.error && enrichResponse.result.error.length) {
                    this.context.showTopBarMessage(
                        new EnrichmentInfo(EnrichmentInfoType.OdooCustomError, enrichResponse.result.error),
                    );
                    this.setState({ isLoading: false, hideEnrichmentButton: true });
                    return;
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
                this.setState({ isCollapsed: false, isLoading: false, hideEnrichmentButton: true });
                this.context.showHttpErrorMessage(error);
            });
    };

    private getCompanyInsightsSection = () => {
        const company = this.state.company as Company;
        const parentIsCompany = this.props.partner.isCompany;

        const companyInsights = [];

        const companyLocation = company.getLocation();
        if (companyLocation) {
            companyInsights.push(
                <CompanyInfoItem
                    icon={faMapMarkerAlt}
                    title={_t('Address')}
                    value={companyLocation}
                    hrefContent={`http://maps.google.com/?q=${companyLocation}`}
                />,
            );
        }

        const companyPhone = company.getPhone();
        if (companyPhone && !parentIsCompany) {
            companyInsights.push(
                <CompanyInfoItem
                    icon={faPhone}
                    title={_t('Phone')}
                    value={companyPhone}
                    hrefContent={`tel:${companyPhone}`}
                />,
            );
        }

        const companyDomain = company.getDomain();
        if (companyDomain) {
            companyInsights.push(
                <CompanyInfoItem
                    icon={faGlobeEurope}
                    title={_t('Website')}
                    value={companyDomain}
                    hrefContent={companyDomain}
                />,
            );
        }

        const companyIndustry = company.getIndustry();
        if (companyIndustry) {
            companyInsights.push(<CompanyInfoItem icon={faIndustry} title={_t('Industry')} value={companyIndustry} />);
        }

        const companyEmployees = company.getEmployees();
        if (companyEmployees) {
            companyInsights.push(
                <CompanyInfoItem icon={faPersonBooth} title={_t('Employees')} value={companyEmployees + ''} />,
            );
        }

        const companyYearFounded = company.getYearFounded();
        if (companyYearFounded) {
            companyInsights.push(
                <CompanyInfoItem icon={faInfo} title={_t('Year founded')} value={'' + company.getYearFounded()} />,
            );
        }

        const companyKeywords = company.getKeywords();
        if (companyKeywords) {
            companyInsights.push(<CompanyInfoItem icon={faKey} title={_t('Keywords')} value={companyKeywords} />);
        }

        const companyType = company.getCompanyType();
        if (companyType) {
            companyInsights.push(<CompanyInfoItem icon={faBuilding} title={_t('Company Type')} value={companyType} />);
        }

        const companyRevenue = company.getRevenue();
        if (companyRevenue) {
            companyInsights.push(<CompanyInfoItem icon={faDollarSign} title={_t('Revenues')} value={companyRevenue} />);
        }

        if (!companyInsights.length && parentIsCompany) {
            if (company.enrichmentStatus != EnrichmentStatus.enrichmentEmpty) {
                return <div className="insights-empty-info muted-text">{_t('No extra information found')}</div>;
            } else {
                return null;
            }
        }

        const icon = company.image
            ? `data:image;base64, ${company.image}`
            : company.getLogoURL() || defaultCompanyImageSrc;

        return (
            <>
                <div className="company-header" onClick={this.openInOdoo}>
                    {!parentIsCompany && (
                        <div className="company-name">
                            <img
                                src={icon}
                                onError={(ev) => {
                                    ev.currentTarget.src = defaultCompanyImageSrc;
                                }}
                            />
                            <span>{company.getName()}</span>
                        </div>
                    )}
                    <CompanySocialIcons
                        twitter={company.getTwitter()}
                        facebook={company.getFacebook()}
                        linkedin={company.getLinkedin()}
                        crunchbase={company.getCrunchbase()}
                    />
                </div>
                <div className="company-insights">
                    <span className="company-description">{company.getDescription()}</span>
                    {companyInsights}
                </div>
            </>
        );
    };

    private getCompanyEnrichmentAvailableSection = () => {
        if (this.state.company.isAddedToDatabase()) {
            return (
                <div>
                    {this.getCompanyInsightsSection()}
                    {!this.state.hideEnrichmentButton && this.props.canCreatePartner && (
                        <div>
                            <div className="odoo-secondary-button insights-button" onClick={this.enrichAndUpdate}>
                                {_t('Enrich Company')}
                            </div>
                        </div>
                    )}
                </div>
            );
        } else if (this.props.partner.isAddedToDatabase()) {
            return (
                <div className="muted-text insights-info">
                    {_t('No company attached to this contact')}
                    {!this.state.hideEnrichmentButton && this.props.canCreatePartner && (
                        <div className="odoo-secondary-button insights-button" onClick={this.enrichAndCreate}>
                            {_t('Create a Company')}
                        </div>
                    )}
                </div>
            );
        } else if (this.props.canCreatePartner) {
            return <div className="muted-text insights-info">{_t('Save the contact to create the company')}</div>;
        }
        return null;
    };

    private getCompanyEnrichmentEmptySection = () => {
        let message = null;
        if (!this.context.isConnected()) {
            message = _t('No company linked to this contact could be enriched');
        } else if (this.state.company.isAddedToDatabase()) {
            message = _t('No additional insights were found for this company');
        } else {
            message = _t('No company linked to this contact could be enriched or found in Odoo');
        }

        return (
            <div>
                {this.state.company.isAddedToDatabase() && this.getCompanyInsightsSection()}
                <div className="muted-text insights-info">{message}</div>
            </div>
        );
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
        const url = api.baseURL + `/web#id=${this.props.partner.company.id}&model=res.partner&view_type=form`;
        window.open(url, '_blank');
    };

    render() {
        let content = null;

        if (this.state.isLoading) {
            content = <Spinner size={SpinnerSize.large} theme={OdooTheme} style={{ marginBottom: '16px' }} />;
        } else {
            content = this.getCompanySection();
        }

        return (
            <CollapseSection
                title={_t('Company Insights')}
                isCollapsed={this.state.isCollapsed}
                hideCollapseButton={this.props.hideCollapseButton}>
                {content}
            </CollapseSection>
        );
    }
}

CompanySection.contextType = AppContext;
export default CompanySection;
