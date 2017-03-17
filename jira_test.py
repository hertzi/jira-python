from jira import JIRA
import datetime
import os

jira_base = os.getenv('JIRA_BASE_URL')
jira_username = os.getenv('JIRA_USERNAME')
jira_password = os.getenv('JIRA_PASSWORD')
audibene = JIRA(jira_base, basic_auth=(jira_username, jira_password))

# issue = audibene.issue('TCAPP-8')
# fields = {}
# for custom_fields in audibene.fields():
#     fields[custom_fields['key']] = custom_fields['name']
# print len(fields)
#
# for field in issue.fields.__dict__.keys():
#     if fields.has_key(field):
#         print fields[field], "[", field, "]", "=",  issue.fields.__dict__[field]
#

def status_times(issue_string):
    issue_with_log = audibene.issue(issue_string, expand='changelog')
    last_created = 0
    time_in_status = {}
    for history in issue_with_log.changelog.histories:
        for item in history.items:
            if item.field == 'status':
                created = datetime.datetime.strptime(history.created[:23], "%Y-%m-%dT%H:%M:%S.%f")
                from_key = item.fromString.replace(" ", "")
                to_key = item.toString.replace(" ", "")
                if last_created != 0:
                    value = (created - last_created)
                    if from_key in time_in_status:
                        value = time_in_status[from_key] + (created - last_created)
                    time_in_status.update({from_key: value})
                    if to_key not in time_in_status:
                        time_in_status.update({to_key: datetime.timedelta()})
                else:
                    time_in_status.update({from_key: datetime.timedelta()})  # calc from start of sprint
                    time_in_status.update({to_key: datetime.timedelta()})
                last_created = created
    return time_in_status


stati = status_times('TCHCP-296')
for status in stati:
    print(status, str(stati[status]))

# ticket in progress is not in 'done'
# ticket moved from 'to-do' was there from start of sprint
# - first item is from 'to-do' to something from start of sprint
# - last item calculate until now or end of sprint
