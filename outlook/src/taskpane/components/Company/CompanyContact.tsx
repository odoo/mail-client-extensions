import * as React from 'react';
import { Separator } from "office-ui-fabric-react/lib/Separator";
import AppContext from '../AppContext';
import InfoCell from "../InfoCell/InfoCell";

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faGlobeEurope, faPhone, faMapMarkerAlt } from '@fortawesome/free-solid-svg-icons'

type CompanyContactProps = {
};
type CompanyContactState = {
};

class CompanyContact extends React.Component<CompanyContactProps, CompanyContactState> {
    constructor(props) {
        super(props);
    }

    public render(): JSX.Element {
        const {company} = this.context.partner;

        let addressSection = null;
        if (company.getLocation()) {
            // #31B3B5
            const addressIcon = <div className='company-icon'><FontAwesomeIcon icon={faMapMarkerAlt} color='darkgrey' className="fa-fw"/></div>
            addressSection = <InfoCell hrefContent={`http://maps.google.com/?q=${company.getLocation()}`} icon={addressIcon} title="Address" value={company.getLocation()} />
        }

        let phoneSection = null;
        if (company.getPhone()){
            // A24689
            const phoneIcon = <div className='company-icon'><FontAwesomeIcon icon={faPhone} color='darkgrey' className="fa-fw"/></div>
            phoneSection = <InfoCell hrefContent={`tel:${company.getPhone()}`} icon={phoneIcon} title="Phone" value={company.getPhone()} />
        }

        let websiteSection = null;
        if (company.getDomain()) {
            // 0645AD
            const websiteIcon = <div className='company-icon'><FontAwesomeIcon icon={faGlobeEurope} color='darkgrey' className="fa-fw"/></div>
            websiteSection = <InfoCell hrefContent={company.getDomain()} icon={websiteIcon} title="Website" value={company.getDomain()} />
        }


        if (!websiteSection && !phoneSection && !addressSection)
            return null;
        return (
            <div className='bounded-tile'>
                {addressSection}
                {addressSection && (phoneSection || websiteSection) ? <Separator /> : null}
                {phoneSection}
                {phoneSection && websiteSection ? <Separator /> : null}
                {websiteSection}
            </div>
        );
    }
}

CompanyContact.contextType = AppContext;
export default CompanyContact;