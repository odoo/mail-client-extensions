import * as React from 'react';
import { mergeStyles, mergeStyleSets } from 'office-ui-fabric-react/lib/Styling';
import { Separator } from "office-ui-fabric-react/lib/Separator";
import AppContext from '../AppContext';
import InfoCell from "../InfoCell/InfoCell";

const iconClass = mergeStyles({
    fontSize: 15,
    margin: '0 15px',
});
const classNames = mergeStyleSets({
    address: [{ color: '#31B3B5' }, iconClass],
    phone: [{color: '#A24689'}, iconClass],
    website: [{color: '#0645AD'}, iconClass]
});

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
        
        let websiteSection = null;
        if (company.getDomain()) {
            websiteSection = <InfoCell hrefContent={company.getDomain()} iconName="Link" iconClassName={classNames.website} title="Website" value={company.getDomain()} />
        }
        
        let phoneSection = null;
        if (company.getPhone()){
            phoneSection = <InfoCell hrefContent={`tel:${company.getPhone()}`} iconName="Phone" iconClassName={classNames.phone} title="Phone" value={company.getPhone()} />
        }

        let addressSection = null;
        if (company.getLocation()) {
            addressSection = <InfoCell hrefContent={`http://maps.google.com/?q=${company.getLocation()}`} iconName="MapPin" iconClassName={classNames.address} title="Address" value={company.getLocation()} />
        }

        if (!websiteSection && !phoneSection && !addressSection)
            return null;
        return (
            <div className='bounded-tile'>
                {websiteSection}
                {websiteSection && phoneSection ? <Separator /> : null}
                {phoneSection}
                {(websiteSection || phoneSection) && addressSection ? <Separator /> : null}
                {addressSection}
            </div>
        );
    }
}

CompanyContact.contextType = AppContext;
export default CompanyContact;