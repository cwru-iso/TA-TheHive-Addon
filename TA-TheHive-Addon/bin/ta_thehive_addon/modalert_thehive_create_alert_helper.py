
# encoding = utf-8

def process_event(helper, *args, **kwargs):
    """
    # IMPORTANT
    # Do not remove the anchor macro:start and macro:end lines.
    # These lines are used to generate sample code. If they are
    # removed, the sample code will not be updated when configurations
    # are updated.

    [sample_code_macro:start]

    # The following example sends rest requests to some endpoint
    # response is a response object in python requests library
    response = helper.send_http_request("http://www.splunk.com", "GET", parameters=None,
                                        payload=None, headers=None, cookies=None, verify=True, cert=None, timeout=None, use_proxy=True)
    # get the response headers
    r_headers = response.headers
    # get the response body as text
    r_text = response.text
    # get response body as json. If the body text is not a json string, raise a ValueError
    r_json = response.json()
    # get response cookies
    r_cookies = response.cookies
    # get redirect history
    historical_responses = response.history
    # get response status code
    r_status = response.status_code
    # check the response status, if the status is not sucessful, raise requests.HTTPError
    response.raise_for_status()


    # The following example gets the setup parameters and prints them to the log
    thehive_url = helper.get_global_setting("thehive_url")
    helper.log_info("thehive_url={}".format(thehive_url))
    thehive_key = helper.get_global_setting("thehive_key")
    helper.log_info("thehive_key={}".format(thehive_key))

    # The following example gets and sets the log level
    helper.set_log_level(helper.log_level)

    # The following example gets the alert action parameters and prints them to the log
    alert_source = helper.get_param("alert_source")
    helper.log_info("alert_source={}".format(alert_source))

    alert_type = helper.get_param("alert_type")
    helper.log_info("alert_type={}".format(alert_type))

    alert_title = helper.get_param("alert_title")
    helper.log_info("alert_title={}".format(alert_title))

    alert_description = helper.get_param("alert_description")
    helper.log_info("alert_description={}".format(alert_description))

    alert_tags = helper.get_param("alert_tags")
    helper.log_info("alert_tags={}".format(alert_tags))

    alert_case_template = helper.get_param("alert_case_template")
    helper.log_info("alert_case_template={}".format(alert_case_template))

    alert_severity = helper.get_param("alert_severity")
    helper.log_info("alert_severity={}".format(alert_severity))

    alert_tlp = helper.get_param("alert_tlp")
    helper.log_info("alert_tlp={}".format(alert_tlp))

    alert_pap = helper.get_param("alert_pap")
    helper.log_info("alert_pap={}".format(alert_pap))

    alert_group_by = helper.get_param("alert_group_by")
    helper.log_info("alert_group_by={}".format(alert_group_by))


    # The following example adds two sample events ("hello", "world")
    # and writes them to Splunk
    # NOTE: Call helper.writeevents() only once after all events
    # have been added
    helper.addevent("hello", sourcetype="sample_sourcetype")
    helper.addevent("world", sourcetype="sample_sourcetype")
    helper.writeevents(index="summary", host="localhost", source="localhost")

    # The following example gets the events that trigger the alert
    events = helper.get_events()
    for event in events:
        helper.log_info("event={}".format(event))

    # helper.settings is a dict that includes environment configuration
    # Example usage: helper.settings["server_uri"]
    helper.log_info("server_uri={}".format(helper.settings["server_uri"]))
    [sample_code_macro:end]
    """

    import time
    import uuid

    helper.set_log_level(helper.log_level)
    helper.log_info("Alert action 'thehive_create_alert' started.")

    # Default dataTypes
    DATA_TYPES = [
        "url",
        "other",
        "user-agent",
        "regexp",
        "mail_subject",
        "registry",
        "mail",
        "autonomous-system",
        "domain",
        "ip",
        "uri_path",
        "filename",
        "hash",
        "file",
        "fqdn",
        "account",
        "field",
        "tag"
    ]

    # Show if we're grouping alerts
    if helper.get_param("alert_group_by"):
        helper.log_info("Grouping alert by field '{}'".format(helper.get_param("alert_group_by")))

    alerts = {} # List of Alerts to be sent
    artifacts = [] # Temporary list of artifacts so duplicates aren't added
    for event in helper.get_events():
        # Generate unique sourceRef
        sourceRef = "SPK-" + str(uuid.uuid4())[:6].upper()

        # If a group_by field is provided, used it,
        # otherwise default to sourceRef
        group_by = str(event.get(helper.get_param("alert_group_by"), None))
        group_by = group_by or sourceRef

        # Create new Alert, if needed
        # Otherwise update existing one
        if not alerts.get(group_by, False):
            helper.log_info("Building new alert '{}' ...".format(sourceRef))
            alerts[group_by] = {
                "sourceRef": sourceRef,
                "date": int(time.time() * 1000),
                "type": helper.get_param("alert_type"),
                "source": helper.get_param("alert_source"),
                "title": helper.get_param("alert_title"),
                "description": helper.get_param("alert_description") or "_No description provided._",
                "tags": helper.get_param("alert_tags").split(",") or [],
                "caseTemplate": helper.get_param("alert_case_template") or None,
                "severity": int(helper.get_param("alert_severity")),
                "tlp": int(helper.get_param("alert_tlp")),
                # "pap": int(helper.get_param("alert_pap")), # Not supported in Alerts yet
                "artifacts": [],
                "customFields": {}
            }

            # Clear old artifacts list for this group
            artifacts = []

            # Set description to value of field
            desc_id = alerts[group_by]["description"]
            if desc_id in event:
                if event[desc_id]:
                    # Automatically fixes newline characters
                    alerts[group_by]["description"] = event[desc_id].replace("\\n", "\n")
                else:
                    # Don't allow empty descriptions
                    alerts[group_by]["description"] = "_No description provided._"
        else:
            # Add to the existing alert
            helper.log_info("Adding artifacts to existing alert '{}' ...".format(alerts[group_by]["sourceRef"]))

        # Loop through each field,value pair in the row,skipping those pesky __mv_ fields
        # and any fields that have empty values
        for field, value in {k: v for k, v in event.items() if v and not k.startswith("__mv_") and ":" in k}.items():
            # Parse Type and Message from field
            # and make sure Type is valid and softfail to "other"
            aType, aMsg = field.split(":", 1)
            if aType not in DATA_TYPES:
                aType = "other"

            # Parse multivalue fields, if they exist
            values = [value]
            mv_field = "__mv_" + field
            if event.get(mv_field, False):
                values = [v for v in event[mv_field].split("$") if v and v != ";"]

            # Handle multiple values
            for v in values:
                if aType == "field":
                    # Parse customField Type and Name, defaulting to string type
                    if ":" in aMsg:
                        fType, fName = aMsg.split(":", 1)
                    else:
                        fType = "string"
                        fName = aMsg

                    # Add customField to Alert if it does not exist
                    if fName not in alerts[group_by]["customFields"]:
                        alerts[group_by]["customFields"][fName] = {
                            "order": len(alerts[group_by]["customFields"]),
                            fType: v
                        }
                elif aType == "tag":
                    # Add dynamic tags if it wasn't added already
                    if v not in alerts[group_by]["tags"]:
                        alerts[group_by]["tags"].append(v)
                else:
                    # Add new Artifact if it wasn't added already
                    if v not in artifacts:
                        artifacts.append(v)
                        alerts[group_by]["artifacts"].append({
                            "message": aMsg,
                            "dataType": aType,
                            "data": v
                        })

    # Send each alert to TheHive
    thehive_url = helper.get_global_setting("thehive_url")
    thehive_key = helper.get_global_setting("thehive_key")
    for alert in alerts.values():
        helper.log_info("Sending alert '{}' to TheHive...".format(alert["sourceRef"]))

        # Build payload and headers
        payload = {k: v for k, v in alert.items() if v is not None}
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + thehive_key
        }

        # Send alert to TheHive
        response = helper.send_http_request(thehive_url + "/api/alert", "POST",
            payload=payload,
            headers=headers,
            verify=True,
            use_proxy=True)

        # Validate response from TheHive
        # 200 = Created, 201 = Updated
        if response.status_code in [200, 201]:
            r_json = response.json()
            helper.log_info("Successfully created/updated alert: {}".format(r_json["id"]))
        else: # Soft-fail
            helper.log_error("TheHive returned the following error: {}".format(response.text))

    return 0
