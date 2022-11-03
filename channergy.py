from ahk import AHK
import keyboard as kb
import pandas as pd
import subprocess
import PySimpleGUI as sg

ahk = AHK()


def access():
    win_customer = ahk.win_get(title='Search for Customer')
    win_report = ahk.win_get(title='Shazam Report Wizard')
    try:
        win_report.close()
        win_customer.close()
    except AttributeError:
        pass
    kb.send('esc')
    try:
        win_main = ahk.win_get(title='Channergy 2022')
        win_main.activate()
    except AttributeError:
        subprocess.run(['Channergy 2022'])


def orient_customer(current: bool = True):
    def existing():
        kb.send('f4, esc, alt+n, alt+c')

    def new():
        kb.send('f4, esc, alt+n')

    return existing() if current is True else new()


def orient_shipping_info_screen(current: bool = True):
    def existing():
        orient_customer()
        kb.send('alt+p')  # places cursor at first name field of ship-to address, current customer

    def new():
        kb.send('alt+p')

    return existing() if current is True else new()


def initial_data_entry(first_name, last_name, inmate_number):
    kb.write(first_name)
    kb.send('tab, tab')
    kb.write(f'{last_name} #{inmate_number}')
    kb.send('tab, tab')


def new_account(first_name, last_name, inmate_number, facility):
    access()
    orient_customer(current=False)
    print('this is input to new_account = ', len(facility))
    if len(facility) == 2:  # tuple has two dict objects, [0] refers to billing, [1] to shipping
        initial_data_entry(first_name, last_name, inmate_number)
        kb.write(facility[0]['bill_company_field'])
        kb.send('tab')
        kb.write(facility[0]['bill_street_1'])
        kb.send('tab')
        try:
            kb.write(facility[0]['bill_street_2'])  # if second street line is present
        except KeyError:
            pass
        kb.send('tab, tab')
        kb.write(facility[0]['bill_zip_code'])
        kb.send('tab, tab')
        orient_shipping_info_screen(current=False)  # now cursor is at ship-to field for new customer
        initial_data_entry(first_name, last_name, inmate_number)
        kb.write(facility[1]['ship_company_field'])
        kb.send('tab')
        kb.write(facility[1]['ship_street_1'])
        kb.send('tab')
        try:
            kb.write(facility[1]['ship_street_2'])  # if second street line is present
        except KeyError:
            pass
        kb.send('tab, tab')
        kb.write(facility[1]['ship_zip_code'])
        kb.send('tab, tab')
    else:
        print('len of facility ', len(facility) )
        initial_data_entry(first_name, last_name, inmate_number)
        print('at line 87, in channergy.py', facility)
        kb.write(facility['company_field'])
        kb.send('tab')
        kb.write(facility['street_1'])
        kb.send('tab')
        try:
            kb.write(facility['street_2'])
        except KeyError:
            pass
        kb.send('tab, tab')
        kb.write(facility['zip_code'])
        kb.send('tab, tab')


def facility_entry(facility):
    if 'company_field' in facility:
        print('here at line 108')
        kb.write(facility['company_field'])
        kb.send('tab')
        kb.write(facility['street_1'])  # street address
        kb.send('tab')
        try:
            kb.write(facility['street_2'])
        except KeyError:
            pass
        kb.send('tab, tab')
        kb.write(facility['zip_code'])
        kb.send('tab, tab')
    elif 'bill_company_field' in facility:
        print('here at line 108')
        kb.write(facility['bill_company_field'])
        kb.send('tab')
        kb.write(facility['bill_street_1'])  # street address
        kb.send('tab')
        try:
            kb.write(facility['bill_street_2'])
        except KeyError:
            pass
        kb.send('tab, tab')
        kb.write(facility['bill_zip_code'])
        kb.send('tab, tab')
    elif 'ship_company_field' in facility:
        kb.write(facility['ship_company_field'])
        kb.send('tab')
        kb.write(facility['ship_street_1'])  # street address
        kb.send('tab')
        try:
            kb.write(facility['ship_street_2'])
        except KeyError:
            pass
        kb.send('tab, tab')
        kb.write(facility['ship_zip_code'])
        kb.send('tab, tab')


def update_facility(facility: dict):
    access()
    orient_customer(), kb.send('tab, tab, tab, tab')
    print('len of facility here line 119', len(facility))
    print('tuple? = ', str(isinstance(facility, tuple)))
    print('dict? = ', str(isinstance(facility, dict)))
    try:
        if isinstance(facility, tuple):
            print('got till here, 2 facs')
            facility_entry(facility[0])  # first dict object
            orient_shipping_info_screen(current=False)
            facility_entry(facility[1])  # second dict object
        elif isinstance(facility, dict):
            print('here instead, line 135')
            facility_entry(facility)
    except AttributeError as e:
        print(e, 'error line 141')
        pass
    print('still executed')



def retrieval(facility_name: str, facility_state: str):
    """ This function will match facility billing and shipping addresses from CSV database,
        while correlating that facility with its state."""
    fields = ['facility_index', 'facility_name', 'facility_state', 'is_federal', 'bill_name', 'bill_street_1',
              'bill_street_2', 'bill_city_state_zip', 'bill_zip_code', 'ship_name', 'ship_street_1',
              'ship_street_2', 'ship_city_state_zip', 'ship_zip_code', 'website']
    addresses = pd.read_csv('prison-addresses.csv', names=fields)
    check_1 = addresses[addresses['facility_name'].str.contains(facility_name)]
    check_2 = check_1['bill_street_1'].equals(check_1['ship_street_1'])
    check_3 = check_1['facility_state'].isin([facility_state]).any()
    check_4 = check_1['facility_index'].nunique()
    print(check_1)
    print(check_2)
    print(check_3)
    print(check_4)
    print('line 138 = ', check_1['bill_street_2'].values[0])
    print('line 139 = ', check_1['bill_zip_code'].values[0])
    # below is if bill-to and ship-to match completely, 1 unique match
    if len(check_1) == 1 and check_2 is True:
        result = {'company_field': check_1['bill_name'].values[0],
                  'street_1': check_1['bill_street_1'].values[0],
                  'street_2': check_1['bill_street_2'].values[0],
                  'zip_code': (str(check_1['bill_zip_code'].values[0]).zfill(5))}
        print(result)
        result_sorted_y = [y for x, y in result.items() if pd.isnull(y) is False and y != 'nan' and y != '']
        result_sorted_x = [x for x, y in result.items() if pd.isnull(y) is False and y != 'nan' and y != '']
        result_sorted_dict = dict(zip(result_sorted_x, result_sorted_y))
        print('channergy.py line 147: ', result_sorted_dict)
        return result_sorted_dict
        # return result
    # below is if bill-to and ship-to addresses are different, but still unique facility match
    if len(check_1) == 1 and check_2 is False:
        result_billing = {'bill_company_field': check_1['bill_name'].values[0],
                          'bill_street_1': check_1['bill_street_1'].values[0],
                          'bill_street_2': check_1['bill_street_2'].values[0],
                          'bill_zip_code': (str(check_1['bill_zip_code'].values[
                                                   0]).zfill(5))}
        result_billing_sorted_y = [y for x, y in result_billing.items() if pd.isnull(y) is False and y !=
                                 'nan' and y != '']
        result_billing_sorted_x = [x for x, y in result_billing.items() if pd.isnull(y) is False and y !=
                                 'nan' and y != '']
        result_billing_dict = dict(zip(result_billing_sorted_x, result_billing_sorted_y))
        result_shipping = {'ship_company_field': check_1['ship_name'].values[0],
                           'ship_street_1': check_1['ship_street_1'].values[0],
                           'ship_street_2': check_1['ship_street_2'].values[0],
                           'ship_zip_code': str(check_1['ship_zip_code'].values[
                                                    0]).zfill(5)}
        result_shipping_sorted_y = [y for x, y in result_shipping.items() if pd.isnull(y) is False and y !=
                                  'nan' and y != '']
        result_shipping_sorted_x = [x for x, y in result_shipping.items() if
                                  pd.isnull(y) is False and y !=
                                  'nan' and y != '']
        result_shipping_dict = dict(zip(result_shipping_sorted_x, result_shipping_sorted_y))
        print(result_billing_dict, result_shipping_dict)
        return result_billing_dict, result_shipping_dict
    if check_4 > 1:
        raise LookupError('Multiple unique entries found, refer to database to correct.')
    else:
        raise TypeError('not working')
