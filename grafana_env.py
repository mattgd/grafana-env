import argparse
import json
import os
import sys

DELETE_KEYS = ['id', 'uid', 'version', 'gnetId', 'iteration']


def is_valid_file(parser, arg):
    """Checks if a provided command line argument is a valid file."""
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

def get_dev_json_panel(panelTitle: str, dev_panels: [dict]) -> dict:
    """Gets the dev_json version of the panel."""
    for panel in dev_panels:
        if panel['title'] == panelTitle:
            return panel

    return None

def delete_keys(json: dict) -> dict:
    """Deletes keys from DELETE_KEYS found in JSON"""
    for key in DELETE_KEYS:
        if key in json:
            del json[key]

    return json

def copy_panel_alerts(panel: dict, dev_json: dict, sub_panel: dict = None) -> dict:
    dev_panel = get_dev_json_panel(panel['title'], dev_json['panels'])

    if sub_panel:
        dev_sub_panel = get_dev_json_panel(sub_panel['title'], dev_panel['panels'])

        if dev_sub_panel and 'alert' in dev_sub_panel:
            sub_panel['alert'] = dev_sub_panel['alert']
        else:
            del sub_panel['alert']
        
        return sub_panel
    elif dev_panel and 'alert' in dev_panel:
        panel['alert'] = dev_panel['alert']
    else:
        del panel['alert']

    return panel

def convert_panel(panel: dict, dev_json: dict) -> dict:
    """Converts a panel dict to the dev version, replacing the alert if necessary."""
    panel = delete_keys(panel)

    # Copy alert over if it has one
    if 'alert' in panel:
        panel = copy_panel_alerts(panel, dev_json)
    
    if 'panels' in panel:
        panel['panels'] = convert_sub_panels(panel, dev_json)

    return panel

def convert_sub_panels(panel: dict, dev_json: dict) -> [dict]:
    """Returns the converted subpanels for the given panel."""
    # Precondition: panel has 'panels' key
    sub_panels = []
    for sub_panel in panel['panels']:
        sub_panel = delete_keys(sub_panel)

        if 'alert' in panel:
            sub_panel = copy_panel_alerts(panel, dev_json, sub_panel)

        sub_panels.append(sub_panel)

    return sub_panels

def main():
    parser = argparse.ArgumentParser(description='Convert a production Grafana JSON model to the development version.')
    parser.add_argument('--prod_json', '-p', type=lambda x: is_valid_file(parser, x), metavar='PROD_FILE', required=True, help='File path to production JSON')
    parser.add_argument('--dev_json', '-d', type=lambda x: is_valid_file(parser, x), metavar='DEV_FILE', required=True, help='File path to development JSON')
    parser.add_argument('--raw', action='store_true', help='Option to print output JSON unformatted')
    args = parser.parse_args()

    prod_json = json.load(args.prod_json)
    dev_json = json.load(args.dev_json)
    result_json = prod_json

    # Delete unwanted keys
    result_json = delete_keys(result_json)

    # Convert prod panels to dev panels
    new_panels = []
    for panel in result_json['panels']:
        new_panels.append(convert_panel(panel, dev_json))

    result_json['panels'] = new_panels
    if args.raw:
        result_json = json.dumps(result_json)
    else:
        result_json = json.dumps(result_json, indent=4)

    print(result_json)


if __name__ == '__main__':
    main()
