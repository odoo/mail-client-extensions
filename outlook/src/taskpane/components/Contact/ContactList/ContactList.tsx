import * as React from 'react';
import ContactListItem from './ContactListItem/ContactListItem';
import Partner from '../../../../classes/Partner';

type ContactListProps = {
    partners: Partner[];
    canCreatePartner: boolean;
    onItemClick?: (partner: Partner) => void;
};

/**
 * Component used for displaying search results
 */
const ContactList = (props: ContactListProps) => {
    const onPartnerClick = (partner: Partner) => {
        props.onItemClick(partner);
    };

    const contactsList = (
        <div>
            {props.partners.map((partner) => {
                return (
                    <ContactListItem
                        partner={partner}
                        canCreatePartner={props.canCreatePartner}
                        onItemClick={onPartnerClick}
                        key={partner.id}
                    />
                );
            })}
        </div>
    );

    return (
        <React.Fragment>
            <div>{contactsList}</div>
        </React.Fragment>
    );
};

export default ContactList;
