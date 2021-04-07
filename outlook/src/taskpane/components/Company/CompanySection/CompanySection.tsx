import * as React from "react";
import {ProfileCard, ProfileCardProps} from "../../ProfileCard/ProfileCard";

import AppContext from '../../AppContext';
import {ContentType, HttpVerb, sendHttpRequest} from "../../../../utils/httpRequest";
import Partner from "../../../../classes/Partner";

import api from "../../../api";
import Company from "../../../../classes/Company";

import "./CompanySection.css"
import {
    faBuilding,
    faDollarSign,
    faGlobeEurope,
    faIndustry,
    faInfo,
    faKey,
    faMapMarkerAlt,
    faPersonBooth,
    faPhone
} from "@fortawesome/free-solid-svg-icons";
import CompanyInfoItem from "../CompanyInfoItem";
import CollapseSection from "../../CollapseSection/CollapseSection";
import CompanyCache from "../../../../classes/CompanyCache";
import EnrichmentInfo, {EnrichmentInfoType} from "../../../../classes/EnrichmentInfo";
import {Spinner, SpinnerSize} from "office-ui-fabric-react";
import {OdooTheme} from "../../../../utils/Themes";
import { _t } from "../../../../utils/Translator";

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
            isLoading: false
        };

        this.enriched = false;

        this.companyCache = new CompanyCache(2, 200, 25);
    }

    private companyCache: CompanyCache;
    private enriched: boolean;

    private enrichCompanyForPartnerRequest = () => {

        if (!this.props.partner.email)
        {
            let enrichmentInfo = new EnrichmentInfo(EnrichmentInfoType.EnrichContactWithNoEmail,
                _t("This contact has no email address, no company could be enriched."));
            this.context.showTopBarMessage(enrichmentInfo);
            return;
        }

        this.setState({isLoading: true});
        this.enriched = true;
        const enrichRequest = sendHttpRequest(HttpVerb.POST, api.baseURL + api.enrichCompany,
            ContentType.Json, this.context.getConnectionToken(), {
                partner_email: this.props.partner.email,
                partner_id: this.props.partner.id,
                enrich_on_not_exists: true
            }, true);
        this.context.addRequestCanceller(enrichRequest.cancel);
        enrichRequest.promise.then((response) => {
            const parsed = JSON.parse(response);
            const company = Company.fromJSON(parsed.result.company);
            if (!company.isEmpty())
            {
                this.companyCache.add(company);
                this.enriched = true;
            }
            if (parsed.result['enrichment_info'])
            {
                const enrichmentInfo = new EnrichmentInfo(parsed.result['enrichment_info'].type,
                    parsed.result['enrichment_info'].info);
                if (enrichmentInfo.type != EnrichmentInfoType.NoData)
                    this.context.showTopBarMessage(enrichmentInfo);
            }
            this.setState({isCollapsed: false, company: company, isLoading: false});
            let newPartner = this.props.partner;
            newPartner.company = company;
            this.props.onPartnerInfoChanged(newPartner);

        }).catch((error) => {
            console.log(error);
            this.enriched = true;
            this.setState({isCollapsed: false, isLoading: false});
            this.context.showHttpErrorMessage(error);
        });

    }

    private getCompanyLayout= () => {
        const company = this.state.company as Company;

        if (company.isEmpty())
        {
            let enrichAndCreate = null;
            if (this.props.partner.isAddedToDatabase() && !this.enriched)
            {
                enrichAndCreate = (
                    <div>
                        <div>
                            {_t("No company attached to this contact")}
                        </div>
                        <div className="odoo-secondary-button" style={{margin: "8px auto auto auto"}} onClick={this.enrichCompanyForPartnerRequest}>
                            {_t("Create a Company")}
                        </div>
                    </div>
                );
            }
            else
            {
                if (!this.context.isConnected())
                {
                    enrichAndCreate = (
                        <div>
                            {_t("No company linked to this contact could be enriched")}
                        </div>
                    );
                }
                else
                {
                    enrichAndCreate = (
                        <div>
                            {_t("No company linked to this contact could be enriched or found in Odoo")}
                        </div>
                    );
                }
            }

            return (
                <div className={"muted-text"} style={{textAlign: "center", padding: "8px 16px 16px 16px", fontSize: "14px"}}>
                    {enrichAndCreate}
                </div>
            )
        }

        let addressSection = null;

        if (company.getLocation())
        {
            addressSection = <CompanyInfoItem
                icon={faMapMarkerAlt} title={_t("Address")} value={company.getLocation()}
                hrefContent={`http://maps.google.com/?q=${company.getLocation()}`}/>
        }
        let phoneSection = null;
        if (company.getPhone())
        {
            phoneSection = <CompanyInfoItem icon={faPhone} title={_t("Phone")} value={company.getPhone()}
                                            hrefContent={`tel:${company.getPhone()}`}/>
        }

        let websiteSection = null;
        if (company.getDomain())
        {
            websiteSection = <CompanyInfoItem icon={faGlobeEurope} title={_t("Website")} value={company.getDomain()}
                                              hrefContent={company.getDomain()}/>
        }

        let industrySection = null;
        if (company.getIndustry())
        {
            industrySection = <CompanyInfoItem icon={faIndustry} title={_t("Industry")} value={company.getIndustry()}/>
        }

        let employeesSection = null;
        if (company.getEmployees())
        {
            employeesSection = <CompanyInfoItem icon={faPersonBooth} title={_t("Employees")} value={company.getEmployees()+''}/>
        }

        let yearFoundedSection = null;
        if (company.getYearFounded())
        {
            yearFoundedSection = <CompanyInfoItem icon={faInfo} title={_t("Year founded")} value={company.getYearFounded()+""}/>
        }

        let keywordsSection = null;
        if (company.getKeywords())
        {
            keywordsSection = <CompanyInfoItem icon={faKey} title={_t("Keywords")} value={company.getKeywords()}/>
        }

        let companyTypeSection = null;
        if (company.getCompanyType())
        {
            companyTypeSection = <CompanyInfoItem icon={faBuilding} title={_t("Company Type")} value={company.getCompanyType()}/>
        }

        let revenueSection = null;
        if (company.getRevenue())
        {
            revenueSection = <CompanyInfoItem icon={faDollarSign} title={_t("Revenues")} value={company.getRevenue()}/>
        }

        const profileCardData: ProfileCardProps = {
            domain: company.getDomain(),
            name: company.getName(),
            email: undefined,
            initials: company.getInitials(),
            icon: company.image ? "data:image;base64, " + company.image : company.getLogoURL(),
            job: undefined,
            phone: undefined,
            twitter: company.getTwitter(),
            facebook: company.getFacebook(),
            crunchbase: company.getCrunchbase(),
            linkedin: company.getLinkedin(),
            description: company.getDescription(),
            onClick: this.openInOdoo
        }


        return (
            <>
                <ProfileCard {...profileCardData}/>
                <div style={{padding: "8px"}}>
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
    }

    private openInOdoo = () => {
        if (!this.context.isConnected())
        {
            this.context.navigation.goToLogin();
            return;
        }
        let url = api.baseURL+`/web#id=${this.props.partner.company.id}&model=res.partner&view_type=form`;
        window.open(url,"_blank");
    }

    private onCollapseClick = () => {
        this.setState({isCollapsed:!this.state.isCollapsed});
    }

    render() {

        let content = null;

        if (this.state.isLoading)
        {
            content = (
                <>
                    <Spinner size={SpinnerSize.large} theme={OdooTheme} style={{marginBottom: "16px"}}/>
                </>
            )
        }
        else
        {
            content = this.getCompanyLayout();
        }


        return (
            <>
                <CollapseSection title={_t("Company Insights")} isCollapsed={this.state.isCollapsed}
                                 onCollapseButtonClick={this.onCollapseClick} hideCollapseButton={this.props.hideCollapseButton}>
                    {content}
                </CollapseSection>
            </>
        );

    }
}

CompanySection.contextType = AppContext;
export default CompanySection;