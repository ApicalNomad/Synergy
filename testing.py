import json
import subprocess
import PySimpleGUI as sg
import pandas as pd
import numpy as np
from time import perf_counter
from validation import States
from pydantic import BaseModel, validator, ValidationError
from typing import Optional
import csv

t1 = perf_counter()
fields = ['facility_index', 'facility_name', 'facility_state', 'is_federal', 'bill_name', 'bill_street_1',
          'bill_street_2', 'bill_city_state_zip', 'bill_zip_code', 'ship_name', 'ship_street_1',
          'ship_street_2', 'ship_city_state_zip', 'ship_zip_code', 'website']
addresses = pd.read_csv('prison-addresses.csv', names=fields)

# check = addresses[addresses['facility_name'].str.contains('SCI Pine Grove')]
# check = addresses[addresses['facility_name'].str.contains('Union Correctional')]
check = addresses[addresses['facility_name'].str.contains('Anchorage Correctional Complex East')]
unchecked = addresses[addresses['facility_name'].str.contains('this dont exist')]

try:
    print(len(unchecked))
except:
    print('not found')

# check = addresses[addresses['facility_name'].str.contains('Elseweyr')]
state = 'AK'
unique_value = check['facility_name'].unique()
unique_count = check['facility_index'].nunique()
found = check['facility_state'].isin([state]).all()

print('this is checking bill and ship addr',
      check['bill_street_1'].equals(check['ship_street_1'])
      )
print('piece by piece: ',
      addresses['bill_name'].values[1],
      addresses['bill_street_1'].values[1],
      addresses['bill_zip_code'].values[1]
      )

"""
these conditions have to be true:

1) len() of check object must be exactly 1
2) bill_street_1 must .equals ship_street_1
3) found must be true of .isin(state).any()-- do .all() instead
4) unique count of index must be exactly 1

if len

"""

print('length = ', len(check))
print('unique = ', unique_value)
print('unique count = ', unique_count)
print('.isin() match = ', found)

# print(
#     'this is how many uniques versus total count:', addresses['facility_name'].nunique(), 'followed '
#                                                                                           'by this many'
#                                                                                           'total values: ',
#     addresses['facility_name'].value_counts()
# )

print(
    'this is what we are looking for = ',
    addresses.duplicated(subset=['facility_name', 'facility_state']).any()
)
duplicates = addresses[addresses.duplicated(subset=['facility_name', 'facility_state'])]
print(duplicates)
# addresses.groupby('facility_name').count()
states_dict = {s.name: s.value for s in States}

# empty dict, soon to be filled with facilities sorted by state
state_facilities = {}


def populate_facilities_dropdown():
    for s in list(states_dict.keys()):
        f = open('prison-addresses.csv', 'rt')
        csv_reader = csv.DictReader(f, escapechar='\\')
        addr = []
        for row in csv_reader:
            check_row = row['facility_state']
            if s in states_dict:
                j = states_dict[s]  # matching instances where acronym matched and also state spelled out
                # st = re.search('[^0-9]+(\,\s){1}(?P<state>[A-Z]{2}|[A-Za-z]+){1}\s([0-9]{5})',
                # check_row).groupdict()['state']
                # if s == st:
                if s == check_row:
                    addr.append(row['facility_name'])
                # if j == st:
                if j == check_row:
                    addr.append(row['facility_name'])
        state_facilities[s] = addr


populate_facilities_dropdown()


# print(state_facilities['FL'])
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

    @validator('last_name', 'inmate_id')
    def check_last_name_and_inmate_id(cls, field):
        max_val = 20
        last_name_id_length = 0
        for f in field:
            assert f != '', 'Last name or inmate ID cannot be empty.'
            if f == '':
                raise ValueError('Fields required to be included.')
            last_name_id_length += len(f)
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


try:
    test = Field(state='')
    print(test.state)
except ValidationError as e:
    print(e.__str__())
    print(e.__repr_args__())
    finding = e.errors()
    print('this is perhaps looking for: ', finding[0]['type'])
    print('this is perhaps looking for: ', e.errors()[0]['type'])
    if e.errors()[0]['type'].__contains__('assertion'):
        print('this is an Assertion Error')
    # print(e.__str__().__contains__('assertion_error'))
    # print(e.__str__().__contains__('value_error'))
    # print(e.__str__().__contains__('type_error'))
    # print(e.json())
try:
    test2 = Field(first_name='')
except ValidationError as e:
    if e.errors()[0]['type'].__contains__('assertion'):
        print('this is an Assertion Error')
# subprocess.run(["Notepad"])

"""
    Autocomplete input
    Thank you to GitHub user bonklers for supplying to basis for this demo!
    There are 3 keyboard characters to be aware of:
    * Arrow up - Change selected item in list
    * Arrow down - Change selected item in list
    * Escape - Erase the input and start over
    * Return/Enter - use the current item selected from the list
    You can easily remove the ignore case option by searching for the "Irnore Case" Check box key:
        '-IGNORE CASE-'
    The variable "choices" holds the list of strings your program will match against.
    Even though the listbox of choices doesn't have a scrollbar visible, the list is longer than shown
        and using your keyboard more of it will br shown as you scroll down with the arrow keys
    The selection wraps around from the end to the start (and vicea versa). You can change this behavior to
        make it stay at the beignning or the end
    Copyright 2021 PySimpleGUI
"""

# def main():
#     # The list of choices that are going to be searched
#     # In this example, the PySimpleGUI Element names are used
#     # choices = sorted([elem.__name__ for elem in sg.Element.__subclasses__()])
#     # choices = list(states_dict.keys())
#     choices = list(state_facilities['FL'])
#
#     input_width = 20
#     num_items_to_show = 4
#
#     layout = [
#         [sg.CB('Ignore Case', k='-IGNORE CASE-')],
#         [sg.Text('Input PySimpleGUI Element Name:')],
#         [sg.Input(size=(input_width, 1), enable_events=True, key='-IN-')],
#         [sg.pin(sg.Col([[sg.Listbox(values=[], size=(input_width, num_items_to_show), enable_events=True, key='-BOX-',
#                                     select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=False)]],
#                        key='-BOX-CONTAINER-', pad=(0, 0), visible=False))]
#     ]
#
#     window = sg.Window('AutoComplete', layout, return_keyboard_events=True, finalize=True, font=('Helvetica', 16))
#
#     list_element: sg.Listbox = window.Element(
#         '-BOX-')  # store listbox element for easier access and to get to docstrings
#     prediction_list, input_text, sel_item = [], "", 0
#
#     while True:  # Event Loop
#         event, values = window.read()
#         # print(event, values)
#         if event == sg.WINDOW_CLOSED:
#             break
#         # pressing down arrow will trigger event -IN- then aftewards event Down:40
#         elif event.startswith('Escape'):
#             window['-IN-'].update('')
#             window['-BOX-CONTAINER-'].update(visible=False)
#         elif event.startswith('Down') and len(prediction_list):
#             sel_item = (sel_item + 1) % len(prediction_list)
#             list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
#         elif event.startswith('Up') and len(prediction_list):
#             sel_item = (sel_item + (len(prediction_list) - 1)) % len(prediction_list)
#             list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
#         elif event == '\r':
#             if len(values['-BOX-']) > 0:
#                 window['-IN-'].update(value=values['-BOX-'])
#                 window['-BOX-CONTAINER-'].update(visible=False)
#         elif event == '-IN-':
#             text = values['-IN-'] if not values['-IGNORE CASE-'] else values['-IN-'].lower()
#             if text == input_text:
#                 continue
#             else:
#                 input_text = text
#             prediction_list = []
#             if text:
#                 if values['-IGNORE CASE-']:
#                     prediction_list = [item for item in choices if item.lower().__contains__(text)]
#                 else:
#                     prediction_list = [item for item in choices if item.__contains__(text)]
#
#             list_element.update(values=prediction_list)
#             sel_item = 0
#             list_element.update(set_to_index=sel_item)
#
#             if len(prediction_list) > 0:
#                 window['-BOX-CONTAINER-'].update(visible=True)
#             else:
#                 window['-BOX-CONTAINER-'].update(visible=False)
#         elif event == '-BOX-':
#             window['-IN-'].update(value=values['-BOX-'])
#             window['-BOX-CONTAINER-'].update(visible=False)
#
#     window.close()

# The list of choices that are going to be searched
# In this example, the PySimpleGUI Element names are used
# choices = sorted([elem.__name__ for elem in sg.Element.__subclasses__()])
# choices = list(states_dict.keys())



def main():
    choices = list(state_facilities['FL'])

    input_width = 20
    num_items_to_show = 4

    layout = [
        [sg.CB('Ignore Case', k='-IGNORE CASE-')],
        [sg.Text('Input PySimpleGUI Element Name:')],
        [sg.Input(size=(input_width, 1), enable_events=True, key='-IN-')],
        [sg.pin(sg.Col([[sg.Listbox(values=[], size=(input_width, num_items_to_show), enable_events=True, key='-BOX-',
                                    select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=False)]],
                       key='-BOX-CONTAINER-', pad=(0, 0), visible=False))]
    ]

    window = sg.Window('AutoComplete', layout, return_keyboard_events=True, finalize=True, font=('Helvetica', 16))

    list_element: sg.Listbox = window.Element(
        '-BOX-')  # store listbox element for easier access and to get to docstrings
    prediction_list, input_text, sel_item = [], "", 0
    while True:  # Event Loop
        event, values = window.read()
        # print(event, values)
        if event == sg.WINDOW_CLOSED:
            break
        # pressing down arrow will trigger event -IN- then aftewards event Down:40
        elif event.startswith('Escape'):
            # escape_here()
            window['-IN-'].update('')
            window['-BOX-CONTAINER-'].update(visible=False)
        elif event.startswith('Down') and len(prediction_list):
            sel_item = (sel_item + 1) % len(prediction_list)
            list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
        elif event.startswith('Up') and len(prediction_list):
            sel_item = (sel_item + (len(prediction_list) - 1)) % len(prediction_list)
            list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
        elif event == '\r':
            if len(values['-BOX-']) > 0:
                window['-IN-'].update(value=values['-BOX-'])
                window['-BOX-CONTAINER-'].update(visible=False)
        elif event == '-IN-':
            text = values['-IN-'] if not values['-IGNORE CASE-'] else values['-IN-'].lower()
            if text == input_text:
                continue
            else:
                input_text = text
            prediction_list = []
            if text:
                if values['-IGNORE CASE-']:
                    prediction_list = [item for item in choices if item.lower().__contains__(text)]
                else:
                    prediction_list = [item for item in choices if item.__contains__(text)]

            list_element.update(values=prediction_list)
            sel_item = 0
            list_element.update(set_to_index=sel_item)

            if len(prediction_list) > 0:
                window['-BOX-CONTAINER-'].update(visible=True)
            else:
                window['-BOX-CONTAINER-'].update(visible=False)
        elif event == '-BOX-':
            window['-IN-'].update(value=values['-BOX-'])
            window['-BOX-CONTAINER-'].update(visible=False)

    window.close()


if __name__ == '__main__':
    main()

t2 = perf_counter()

print('took this long: ', t2 - t1)

# addresses['check'] = np.where((addresses['bill_street_1'] == addresses['ship_street_1']) & (addresses[
#     'facility_state'] == 'CA'), addresses[
#                                                                                             'facility_name'],
#                               np.nan)
#
# print(addresses['check'])


# try:
#     tester = Field(first_name='this is real no', last_name='less long name ')
#     print('values are good')
# except ValidationError as e:
#     print(e)
#     print('nope')

# try:
#     tester = Field(zip_code='0103')
#     print(tester.zip_code)
# except ValidationError as e:
#     print(e)
