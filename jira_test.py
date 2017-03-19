from jira import JIRA
import os

jira_base = os.getenv('JIRA_BASE_URL')
jira_username = os.getenv('JIRA_USERNAME')
jira_password = os.getenv('JIRA_PASSWORD')
jira = JIRA(jira_base, basic_auth=(jira_username, jira_password))

issue = jira.issue('TCAPP-8')
fields = {}
for custom_fields in jira.fields():
    fields[custom_fields['key']] = custom_fields['name']
print len(fields)

for field in issue.fields.__dict__.keys():
    if fields.has_key(field):
        print fields[field], "[", field, "]", "=",  issue.fields.__dict__[field]



# ticket in progress is not in 'done'
# ticket moved from 'to-do' was there from start of sprint
# - first item is from 'to-do' to something from start of sprint
# - last item calculate until now or end of sprint
