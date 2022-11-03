from pydantic import BaseModel, validator, ValidationError
from typing import Optional
from enum import Enum, unique


@unique
class States(Enum):
    AL = 'Alabama'
    AK = 'Alaska'
    AS = 'American Samoa'
    AZ = 'Arizona'
    AR = 'Arkansas'
    CA = 'California'
    CO = 'Colorado'
    CT = 'Connecticut'
    DE = 'Delaware'
    DC = 'District of Columbia'
    FL = 'Florida'
    GA = 'Georgia'
    GU = 'Guam'
    HI = 'Hawaii'
    ID = 'Idaho'
    IL = 'Illinois'
    IN = 'Indiana'
    IA = 'Iowa'
    KS = 'Kansas'
    KY = 'Kentucky'
    LA = 'Louisiana'
    ME = 'Maine'
    MD = 'Maryland'
    MA = 'Massachusetts'
    MI = 'Michigan'
    MN = 'Minnesota'
    MS = 'Mississippi'
    MO = 'Missouri'
    MT = 'Montana'
    NE = 'Nebraska'
    NV = 'Nevada'
    NH = 'New Hampshire'
    NJ = 'New Jersey'
    NM = 'New Mexico'
    NY = 'New York'
    NC = 'North Carolina'
    ND = 'North Dakota'
    MP = 'Northern Mariana Islands'
    OH = 'Ohio'
    OK = 'Oklahoma'
    OR = 'Oregon'
    PA = 'Pennsylvania'
    PR = 'Puerto Rico'
    RI = 'Rhode Island'
    SC = 'South Carolina'
    SD = 'South Dakota'
    TN = 'Tennessee'
    TX = 'Texas'
    UT = 'Utah'
    VT = 'Vermont'
    VI = 'Virgin Islands'
    VA = 'Virginia'
    WA = 'Washington'
    WV = 'West Virginia'
    WI = 'Wisconsin'
    WY = 'Wyoming'


class Field(BaseModel):
    """ This class ensures that any included input will fit within Channergy field space constraints. """
    first_name: Optional[str]
    last_name: Optional[str]
    inmate_id: Optional[str]
    inmate_id_second: Optional[str]
    facility_name: Optional[str]
    street_1: Optional[str]
    street_2: Optional[str]
    zip_code: Optional[str]
    state: Optional[str]

    @validator('first_name')
    def check_first_name(cls, field):
        assert field != '', 'First name field cannot be empty.'
        if len(field) > 15:
            raise ValueError('First name exceeds length allowed by Channergy.')
        return field

    @validator('inmate_id')
    def check_inmate_id(cls, field):
        assert field != '', 'Inmate ID field cannot be empty.'
        return field

    @validator('last_name')
    def check_last_name_and_inmate_id(cls, field, values):
        max_val = 20
        last_name_id_length = 0
        assert field != '', 'Last name or inmate ID cannot be empty.'
        if 'inmate_id' in values and field != '':
            last_name_id_length += len(values['inmate_id'])
        last_name_id_length += len(field)
        if last_name_id_length > max_val:
            raise ValueError('Length of last name and inmate ID exceeds Channergy limit; please verify data!')
        return field

    @validator('inmate_id_second')
    def check_inmate_id_second(cls, field):
        assert field != '', 'Second inmate ID cannot be empty.'
        return field

    @validator('facility_name')
    def check_facility_name(cls, field):
        if len(field) > 40:
            raise ValueError('Facility name exceeds Channergy limit; please verify data!')
        return field

    @validator('street_1')
    def check_street_1(cls, field):
        assert field != '', 'Street address cannot be empty.'
        if len(field) > 30:
            raise ValueError('Length of street exceeds Channergy limit; please verify data!')
        return field

    @validator('street_2')
    def check_street_2(cls, field):
        assert field != '', 'Second line of street address cannot be empty.'
        if len(field) > 30:
            raise ValueError('Length of address line 2 exceeds Channergy limit; please verify data!')
        return field

    @validator('zip_code')
    def check_zip_code(cls, field):
        assert field != '', 'Zip code cannot be empty.'
        if len(field) < 5:
            field = str(field).zfill(5)
        return field

    @validator('state')
    def check_state(cls, field):
        states_dict = {s.name: s.value for s in States}
        assert field != '', 'State field cannot be empty.'
        if field not in list(states_dict.keys()):
            raise ValueError('Invalid state abbreviation, please verify data!')
        return field
