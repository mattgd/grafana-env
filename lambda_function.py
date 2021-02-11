import io
import json
import os
from urllib.parse import parse_qs

import requests

import grafana_env

SLACK_API_TOKEN = os.environ.get('SLACK_API_TOKEN')
SLACK_API_URL = 'https://slack.com/api/'
SLACK_VIEWS_OPEN_API = SLACK_API_URL + 'views.open'
SLACK_FILES_UPLOAD_API = SLACK_API_URL + 'files.upload'


def create_error_payload(errors: dict) -> str:
    return json.dumps(
        {
            "response_action": "errors",
            "errors": errors
        }
    )


def send_slack_api_request(api_url: str, payload: dict, files: dict = {}, content_type: str = 'application/json') -> dict:
    print(payload)

    r = requests.post(api_url, data=payload, files=files, headers={
        'Authorization': 'Bearer ' + SLACK_API_TOKEN,
        'Content-Type': content_type
    })
    return r.json()


def lambda_handler(event, context):
    payload = json.loads(parse_qs(event['body'])['payload'][0])
    request_type = payload['type']
    trigger_id = payload['trigger_id']

    if request_type == 'shortcut':
        view_payload = {
            "trigger_id": trigger_id,
            "view": {
                "type": "modal",
                "callback_id": "grafana-convert",
                "title": {
                    "type": "plain_text",
                    "text": "grafana-env Converter",
                    "emoji": True
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Convert",
                    "emoji": True
                },
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "prod_json_block",
                        "label": {
                            "type": "plain_text",
                            "text": "Production JSON Model"
                        },
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "prod_json",
                            "multiline": True,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Paste your production Grafana JSON model"
                            }
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "dev_json_block",
                        "label": {
                            "type": "plain_text",
                            "text": "Development JSON Model"
                        },
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "dev_json",
                            "multiline": True,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Paste your development Grafana JSON model"
                            }
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": "Convertion Options"
                        },
                        "accessory": {
                            "type": "checkboxes",
                            "action_id": "options",
                            "initial_options": [
                                {
                                    "value": "separate_alerts",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Separate alerts across dev/prod"
                                    }
                                }
                            ],
                            "options": [
                                {
                                    "value": "separate_alerts",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Separate alerts across dev/prod"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }

        response = send_slack_api_request(SLACK_VIEWS_OPEN_API, view_payload)
        print(response)

        return {
            'statusCode': 200,
            'body': json.dumps('Sent initial payload.')
        }
    elif request_type == 'view_submission':
        user_id = payload.get('user').get('id')
        view_state_values = payload.get('view').get('state').get('values')

        # Parse production dashboard JSON
        prod_json_str = view_state_values.get('prod_json_block').get('prod_json').get('value')
        try: 
            prod_json = json.loads(prod_json_str)
        except ValueError: 
            return {
                'statusCode': 400,
                'body': create_error_payload({'invalid-json': 'Invalid production dashboard JSON.'})
            }

        # Parse development dashboard JSON
        dev_json_str = view_state_values.get('dev_json_block').get('dev_json').get('value')
        try: 
            dev_json = json.loads(dev_json_str)
        except ValueError: 
            return {
                'statusCode': 400,
                'body': create_error_payload({'invalid-json': 'Invalid development dashboard JSON.'})
            }

        result_json = grafana_env.convert(prod_json, dev_json, separate_alerts=True)
        files_upload_payload = {
            'title': 'grafana_env_result.json',
            'filetype': 'json',
            'channels': user_id,
            'initial_comment': ':wave: Here\'s your converted Grafana dashboard JSON model:',
            'content': json.dumps(result_json)
        }
        response = send_slack_api_request(SLACK_FILES_UPLOAD_API, payload=files_upload_payload, content_type='application/x-www-form-urlencoded')
        print(response)

        return {'statusCode': 200}
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('Invalid type.')
        }
