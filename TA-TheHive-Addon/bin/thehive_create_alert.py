
# encoding = utf-8
# Always put this line at the beginning of this file
import ta_thehive_addon_declare

import os
import sys

from alert_actions_base import ModularAlertBase
import modalert_thehive_create_alert_helper

class AlertActionWorkerthehive_create_alert(ModularAlertBase):

    def __init__(self, ta_name, alert_name):
        super(AlertActionWorkerthehive_create_alert, self).__init__(ta_name, alert_name)

    def validate_params(self):

        if not self.get_global_setting("thehive_url"):
            self.log_error('thehive_url is a mandatory setup parameter, but its value is None.')
            return False

        if not self.get_global_setting("thehive_key"):
            self.log_error('thehive_key is a mandatory setup parameter, but its value is None.')
            return False

        if not self.get_param("alert_source"):
            self.log_error('alert_source is a mandatory parameter, but its value is None.')
            return False

        if not self.get_param("alert_type"):
            self.log_error('alert_type is a mandatory parameter, but its value is None.')
            return False

        if not self.get_param("alert_title"):
            self.log_error('alert_title is a mandatory parameter, but its value is None.')
            return False

        if not self.get_param("alert_severity"):
            self.log_error('alert_severity is a mandatory parameter, but its value is None.')
            return False

        if not self.get_param("alert_tlp"):
            self.log_error('alert_tlp is a mandatory parameter, but its value is None.')
            return False

        if not self.get_param("alert_pap"):
            self.log_error('alert_pap is a mandatory parameter, but its value is None.')
            return False
        return True

    def process_event(self, *args, **kwargs):
        status = 0
        try:
            if not self.validate_params():
                return 3
            status = modalert_thehive_create_alert_helper.process_event(self, *args, **kwargs)
        except (AttributeError, TypeError) as ae:
            self.log_error("Error: {}. Please double check spelling and also verify that a compatible version of Splunk_SA_CIM is installed.".format(ae.message))
            return 4
        except Exception as e:
            msg = "Unexpected error: {}."
            if e.message:
                self.log_error(msg.format(e.message))
            else:
                import traceback
                self.log_error(msg.format(traceback.format_exc()))
            return 5
        return status

if __name__ == "__main__":
    exitcode = AlertActionWorkerthehive_create_alert("TA-TheHive-Addon", "thehive_create_alert").run(sys.argv)
    sys.exit(exitcode)
