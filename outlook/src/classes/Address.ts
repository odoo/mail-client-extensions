class Address {
    number: string;
    street: string;
    city: string;
    zip: string;
    country: string;

    constructor() {
        this.number = '';
        this.street = '';
        this.city = '';
        this.zip = '';
        this.country = '';
    }

    getLines(): string[] {
        const firstLine = [this.number || '', this.street || ''].join(' ').trim();
        const secondLine = [this.city || '', this.zip || ''].join(' ').trim();

        const lines = [];
        if (firstLine && firstLine.length) lines.push(firstLine);
        if (secondLine && secondLine.length) lines.push(secondLine);
        if (this.country && this.country.length) lines.push(this.country);

        return lines;
    }

    static fromJSON(o: Object): Address {
        if (!o) return new Address();
        return Object.assign(new Address(), o);
    }

    static fromRevealJSON(o: Object): Address {
        const address = new Address();
        address.number = o['street_number'];
        address.street = o['street_name'];
        address.city = o['city'];
        address.zip = o['postal_code'];
        address.country = o['country_name'];
        return address;
    }
}

export default Address;
