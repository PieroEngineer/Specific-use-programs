import sys
import pandas as pd
import win32com.client


# ------------------------------------------------------------------------------------------------ RPA functions
def select_to_transaction(combo_id, selection, session):
    """
    Navigates to a specific SAP transaction code.
    
    Args:
        session: The active SAP GUI session object.
        transaction_code: The SAP T-code.
    """
    try:
        # Enter the T-code in the command field
        session.findById(combo_id).text = selection
        print(f"✅🧭  Transaction selected: {selection}\n")
    except Exception as e:
        print(f"‼️  Error navigating to {selection} | {e}\n")

def set_txt(field_id, text_value, session):
    """
    Finds a text field by ID and sets its value.
    
    Args:
        session: The active SAP GUI session object.
        field_id: The SAP element ID of the text field (e.g., "wnd[0]/usr/ctxtVBAK-VKORG").
        text_value: The text to input into the field.
    """
    try:
        session.findById(field_id).text = text_value
        print(f"🖊️  Set text in field {field_id} to: {text_value}\n")
    except Exception as e:
        print(f"‼️  Error setting text in {field_id}    | {e}\n")

def click_btn(button_id, session):
    """
    Clicks a button in the SAP GUI by its ID.
    
    Args:
        session: The active SAP GUI session object.
        button_id: The SAP element ID of the button.
    """
    # try:
    session.findById(button_id).press()
    print(f"✅🖱️  Clicked button: {button_id}\n")

def select_tab(selectable_id, session):
    try:
        session.findById(selectable_id).select()
        print(f"🔹  Selecting tab: {selectable_id}\n")
    except Exception as e:
        print(f"‼️  Error selecting tab {selectable_id}   | {e}\n")

def get_text(textfield_id, session) -> str:    
    print(f"👓  ID to read is {textfield_id}")

    text_field = session.findById(textfield_id)

    print(f"✅👓  Text field successfully read\n")

    return text_field.text

def generate_sessions(username, password): # Max 5 extras
    """
    Establishes a connection to SAP GUI.
    This function launches or connects to an existing SAP GUI session,
    opens a connection to the specified system, and logs in.
    
    Returns:
        session: The active SAP GUI session object if successful, None otherwise.
    """

    
    # Get the SAP GUI application object
    sap_gui_app = win32com.client.GetObject("SAPGUI")
    if not sap_gui_app:
        print("‼️  SAP GUI is not running. Starting it...\n")
        # If not running, you might need to launch it manually or via subprocess (not shown here for simplicity)
        sys.exit(1)
    
    # Get the scripting engine
    scripting_engine = sap_gui_app.GetScriptingEngine
    
    # Open a new connection or use existing
    connection = scripting_engine.OpenConnection('ERP_Productivo', True)  # True for synchronous
    
    # Get the first session (session 0)
    session = connection.Sessions(0)
    
    # Log in
    session.findById("").text = ''
    session.findById("").text = username
    session.findById("").text = password
    session.findById("").text = ''
    session.findById("wnd[0]").sendVKey(0)  # Press Enter
    
    print("✅  Successfully connected and logged in to SAP.\n")
    
    return session

def get_credentials():
        while True:
            # Prompt for username
            username = input("Enter username: ").strip()
            
            # Use getpass to hide the password typing for security
            password = input("Enter password: ").strip()

            # Check if either field is an empty string
            if not username or not password:
                print("⚠️ Username and password cannot be empty. Please try again.\n")
                continue  # Restarts the loop
            
            return username, password

# ------------------------------------------------------------------------------------------------ Main
if __name__ == '__main__':
    window_base = 'wnd[0]/'
    user_base = window_base + 'usr/'
    sub_data = ''

    nav_collection = {
        'transaction_combo_id': window_base + '',
        'execution_button_id': window_base + '',
        'confirmation_button_id': window_base + '',
        'go_back_id': window_base + '',

        'code_textfield_id' : user_base + ''
    }

    tab_id = lambda tab_page: user_base + fr'{tab_page}/'
    tab_order = [1, 2, 3, 5]

    status_textfield_id = user_base + ''

    text_field_collection = (
        # First tab
        {
            'class': tab_id(1) + sub_data + '',
            'manufacturer': tab_id(1) + sub_data + '',
            'type_nomination': tab_id(1) + sub_data + '',
            'serie_number': tab_id(1) + sub_data + '',
            'commissioning_date': tab_id(1) + sub_data + ''
        },

        # Second tab
        {
            'site_center': tab_id(2) + sub_data + ''
        },

        # Third tab
        {
            'cost_center': tab_id(3) + sub_data + '',
            'fixed_asset': tab_id(3) + sub_data + ''
        },

        # Fifth tab
        {
            'ciber_asset_class': tab_id(5) + ''
        }
    )

    base_path = r'input\bases_with_codes.xlsx'
    base_df = pd.read_excel(base_path, engine='openpyxl')

    # Example usage
    user, pwd = get_credentials()
    print(f"\n✅ Credentials received for: {user}")

    session = generate_sessions(user, pwd)
    select_to_transaction(nav_collection['transaction_combo_id'], 'IH08', session)
    click_btn(nav_collection['confirmation_button_id'], session)

    code_column = 'Code'
    collected_data = []
    for code in base_df[code_column]:
        set_txt(nav_collection['code_textfield_id'], code, session)
        click_btn(nav_collection['execution_button_id'], session)
        
        # try:
        asset_data = {code_column: code}
        asset_data['Status'] = get_text(status_textfield_id, session)

        for tab_i, tab_content in enumerate(text_field_collection):
            select_tab(tab_id(tab_order[tab_i]), session)
            for attribute, access_id in tab_content.items():
                asset_data[attribute] = get_text(access_id, session)

        collected_data.append(asset_data)

        click_btn(nav_collection['go_back_id'], session)
        # except Exception as e:
        #         print(f"⚠️  There was a problem when trying to find {code} | {e}\nFallback: By pass\n")
        #         continue
    
    print(f"✅  Extraction finished\n")

    if collected_data:
        final_data = pd.merge(base_df, pd.DataFrame(collected_data), on = code_column, how = 'left')

        final_data.to_excel(r"output\extraction.xlsx", index=False)
    else:
        print(f"🟥 There is no data\n")
    