import * as React from 'react';
import Partner from '../../../../classes/Partner';

import ContactListItem from '../ContactList/ContactListItem/ContactListItem';

import api from '../../../api';
import AppContext from '../../AppContext';

type ContactSectionProps = {
    partner: Partner;
    canCreatePartner: boolean;
    onPartnerInfoChanged?: (partner: Partner) => void;
};

class ContactSection extends React.Component<ContactSectionProps, {}> {
    viewContact = (partner) => {
        const cids = this.context.getUserCompaniesString();
        const url = `${api.baseURL}/web#id=${partner.id}&model=res.partner&view_type=form${cids}`;
        window.open(url, '_blank');
    };

    render() {
        const onItemClick = this.props.partner.isAddedToDatabase() ? this.viewContact : null;

        return (
            <div className="section-card">
                <ContactListItem
                    partner={this.props.partner}
                    canCreatePartner={this.props.canCreatePartner}
                    onItemClick={onItemClick}
                />
            </div>
        );
    }
}
ContactSection.contextType = AppContext;

export default ContactSection;
