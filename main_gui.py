import keyboard as kb
from pydantic import ValidationError
from validation import Field, States
from channergy import access, new_account, update_facility, retrieval
import PySimpleGUI as sg
import csv, re, time, webbrowser, subprocess, pyperclip

sg.theme('DarkTanBlue')

# creating dict using comprehension of enum class
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
                if s == check_row:
                    addr.append(row['facility_name'])
                if j == check_row:
                    addr.append(row['facility_name'])
        state_facilities[s] = addr


# first instance of this function to populate combo boxes
populate_facilities_dropdown()

options = {
    "font": ('Helvetica', 16),
    "size": (10, 5),
    "readonly": True,
    "enable_events": True
}

options2 = {
    "font": ('Helvetica', 16),
    "size": (45, 5),
    "readonly": True,
    "enable_events": True
}

# below are labels
first_name_label = sg.Text("Inmate First Name:", justification='center')
last_name_label = sg.Text("Inmate Last Name:", justification='left')
inmate_id_label = sg.Text("Inmate ID:   ", justification='left')
states_label = sg.Text("First, select state:   ", justification='left')
facility_label = sg.Text("Then, choose facility:   ", justification='left')

# these are input areas
first_name_input = sg.Input(key='first_name', tooltip='Enter first name = ', size=(30, 1))
last_name_input = sg.Input(key='last_name', tooltip='Enter last name = ', size=(30, 1))
inmate_id_input = sg.Input(key='inmate_id', tooltip='Enter inmate number =: ', size=(30, 1))

# these are buttons/clickable elements that need to be processed
create_button = sg.Button('Create Channergy Account', key="create")
quit_button = sg.Button('Quit')
clear_button = sg.Button('Clear All Data', key="clear")
verify_online_button = sg.Button('Verify Info Online', key="verify_online")
find_channergy_button = sg.Button('Locate inmate in Channergy', key="find_channergy")
update_facility_channergy_button = sg.Button('Update Address in Channergy', key="update_facility_channergy")
find_jpay_button = sg.Button('Find Inmate in JPay', key="jpay")
select_state_dropdown = sg.Combo(sorted(list(state_facilities.keys())), **options, key="state_select_dropdown",
                                 tooltip='Select state first, then facility below.')
select_facility_dropdown = sg.Combo((), **options2, key="facility_select_dropdown",
                                    tooltip='Select state above first, then facility.')

layout = [
    [first_name_label],
    [first_name_input],
    [last_name_label],
    [last_name_input],
    [inmate_id_label],
    [inmate_id_input],
    [states_label],
    [select_state_dropdown],
    [facility_label],
    [select_facility_dropdown],
    [verify_online_button],
    [find_channergy_button],
    [find_jpay_button],
    [update_facility_channergy_button],
    [create_button],
    [quit_button],
    [clear_button]
]

window = sg.Window('Synergy', layout, use_ttk_buttons=True, finalize=True, resizable=True)

if __name__ == "__main__":
    access()
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Quit'):
            break
        first_name = values['first_name'].strip().capitalize()  # pulling values, formatted, from input fields
        last_name = values['last_name'].strip().capitalize()
        inmate_id = str(values['inmate_id']).strip().upper()
        selected_state = values['state_select_dropdown']
        selected_facility = values['facility_select_dropdown']
        if event == "state_select_dropdown":
            try: # updating facility dropdown list once state has been selected
                facility_list = sorted(state_facilities[values[event]])
                window['facility_select_dropdown'].Update(value=facility_list[0], values=facility_list)
                continue
            except IndexError:
                sg.popup('No facilities present for that state/territory, please correct selection and try again.',
                         title='Error')
                continue
        if event == 'find_channergy':
            try:
                verified = Field(first_name=first_name, last_name=last_name)
                access()
                time.sleep(0.25)
                kb.send('f4, alt+f'), kb.write(verified.first_name), kb.send('tab'), kb.write(verified.last_name)
                time.sleep(0.25)
                kb.send('alt+s')  # searches Customers
                continue
            except ValidationError as ve:
                if ve.errors()[0]['type'].__contains__('assertion'):
                    sg.popup('Both first name and last name fields are required, please try again.', title='Error')
                    continue
            except NameError:
                sg.popup("Channergy was not running, starting now; please create account again.", title="Error")
                subprocess.run(["channergy"])
                continue
        if event == 'jpay':  # opening website link to URL
            if selected_state == 'NJ':
                sg.popup("New Jersey DOC not permitted.", title="Error")
                continue
            try:
                verified = Field(state=selected_state, inmate_id=inmate_id)
                url_jpay = f'https://www.jpay.com/SearchResult.aspx?searchText={verified.inmate_id}&searchState=' \
                           f'{verified.state}&returnUrl=InmateInfo.aspx'
                webbrowser.open(url_jpay, new=0, autoraise=True)
                continue
            except ValidationError as ve:
                if ve.errors()[0]['type'].__contains__('assertion'):
                    sg.popup("State and Inmate ID are both required fields, please try again.")
                    continue
        if event == 'create':  # creating new account within Channergy
            try:
                access()
                verified = Field(first_name=first_name, last_name=last_name, inmate_id=inmate_id,
                                 facility_name=selected_facility, state=selected_state)
                new_account(verified.first_name, verified.last_name, verified.inmate_id,
                            (retrieval(verified.facility_name, verified.state)))
            except ValidationError as ve:
                if ve.errors()[0]['type'].__contains__('assertion'):
                    sg.popup("All required fields must be present: first name, last name, inmate ID, facility, "
                             "and state. Please correct and try again.",
                             title="Error")
                    continue
                if ve.errors()[0]['type'].__contains__('value'):
                    sg.popup("Input data is too long, one or more fields may be shortened by Channergy, "
                             "please revise any overly-long field(s) and try again.",
                             title="Error")
                    continue
                print(ve)
                continue
            except NameError:
                sg.popup("Channergy was not running, starting now; please create account again.", title="Error")
                subprocess.run(["channergy"])
                continue
        if event == 'verify_online':
            try:
                verified = Field(first_name=first_name, last_name=last_name, inmate_id=inmate_id, state=selected_state)
                url = f'https://www.google.com/search?q={verified.state} inmate locator'
                vinelinks_states = ['LA', 'MA', 'AK']
                if verified.state in vinelinks_states:
                    url = f'https://vinelink.vineapps.com/search/persons;limit=20;offset=0;showPhotos=false' \
                          f';isPartialSearch=false;siteRefId={verified.state}SWVINE;personContext' \
                          f'RefId={verified.inmate_id};stateServed={verified.state} '
                if verified.state == 'TX':  # some states require specific length ID's, filling in zeros; or have
                    # direct ways of URL creation
                    pyperclip.copy(verified.inmate_id.zfill(8))
                elif verified.state == 'AR':
                    pyperclip.copy(verified.inmate_id.zfill(6))
                elif verified.state == 'MD':
                    url = f"https://www.dpscs.state.md.us/inmate/search.do?searchType=name&firstnm=" \
                          f"{verified.first_name}&lastnm={verified.last_name}"
                elif verified.state == 'FL':
                    url = f"http://www.dc.state.fl.us/OffenderSearch/list.aspx?Page=List&TypeSearch=AI&DataAction" \
                          f"=Filter&dcnumber={verified.inmate_id}&photosonly=0&nophotos=1&matches=20"
                elif verified.state == 'CA':
                    url = f"https://inmatelocator.cdcr.ca.gov/Details.aspx?ID={verified.inmate_id}"
                else:
                    pyperclip.copy(verified.inmate_id)
                webbrowser.open(url, new=0, autoraise=True)
            except ValidationError as ve:
                if ve.errors()[0]['type'].__contains__('assertion'):
                    sg.popup("All required fields must be present: first name, last name, inmate ID, and state. "
                             "Please correct and try again.",
                             title="Error")
                    continue
                if ve.errors()[0]['type'].__contains__('value'):
                    sg.popup("Input data is too long, one or more fields may be shortened by Channergy, "
                             "please revise any lengthy field(s) and try again.",
                             title="Error")
                    continue
        if event == 'clear':
            for key, value in window.key_dict.items():
                if key in ['first_name', 'last_name', 'inmate_id', 'selected_state', 'selected_facility']:
                    window[key].update('')
            kb.send('tab')
        if event == 'update_facility_channergy':
            try:
                verified = Field(facility_name=selected_facility, state=selected_state)
                update_facility(retrieval(verified.facility_name, verified.state))
                continue
            except ValidationError as ve:
                if ve.errors()[0]['type'].__contains__('assertion'):
                    sg.popup("All required fields must be present: first name, last name, inmate ID, facility, "
                             "and state. Please correct and try again.",
                             title="Error")
                    continue
            except NameError:
                sg.popup("Channergy was not running, starting now; please create account again.", title="Error")
                subprocess.run(["channergy"])
                continue
window.close()

"""

# 2/22/22: can now find inmate info straight from vinelink without entering any info>
#https://vinelink.vineapps.com/search/persons;limit=20;offset=0;showPhotos=false;isPartialSearch=false;siteRefId
=CASWVINE;personContextRefId=k13758;stateServed=CA
# need to modify these parts of URL = 1) "(state by 2 letter Abbrev)SWVINE", 2) personContextRefId="(inmate number 
here)", and 3) stateServed="(state by 2 letter abbrev)"

url = f'https://vinelink.vineapps.com/search/persons;limit=20;offset=0;showPhotos=false;isPartialSearch=false
;siteRefId={selected_state}SWVINE;personContextRefId={inmate_id};stateServed={selected_state}'

"""
