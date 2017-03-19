from jira import JIRA
import datetime
import os

jira_base = os.getenv('JIRA_BASE_URL')
jira_username = os.getenv('JIRA_USERNAME')
jira_password = os.getenv('JIRA_PASSWORD')
jira = JIRA(jira_base, basic_auth=(jira_username, jira_password))


def status_times(issue_string):
    issue_with_log = jira.issue(issue_string, expand='changelog')
    issue_status = issue_with_log.fields.status.name.replace(" ", "")
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
    # state the issue is in - add difference to current date
    if issue_status in time_in_status:
        value = time_in_status[issue_status] + (datetime.datetime.now() - last_created)
        time_in_status.update({issue_status: value})
    #
    return time_in_status


def prepare_print_issue(issue_string, file1):
    jira_issue = jira.issue(issue_string)
    time_in_status = ""
    issue_status = jira_issue.fields.status.name.replace(" ", "")
    if issue_status != "Done":
        stati = status_times(jira_issue.key)
        if issue_status in stati:
            time_in_status = stati[issue_status]
    list = []
    list.append(issue_string)
    issue_type = jira_issue.fields.issuetype
    list.append(issue_type)
    story_points = ""
    issue_assignee = None
    if hasattr(jira_issue.fields, 'assignee'):
        issue_assignee = jira_issue.fields.assignee
    if str(issue_type) == 'Story':
        story_points = str(jira_issue.fields.customfield_10004)
    list.append("\""+jira_issue.fields.summary+"\"")
    if issue_assignee is None:
        list.append("")
    else:
        list.append("\""+issue_assignee.displayName+"\"")
    list.append(story_points)
    list.append("\""+jira_issue.fields.status.name+"\"")
    if time_in_status != "":
        list.append("\""+str(time_in_status)+"\"")
    else:
        list.append("")
    if file1 is not None:
        print >> file1, ','.join(map(str, list))
    else:
        print ','.join(map(str, list))


def get_active_sprint_from_issue(issue_string):
    jira_issue = jira.issue(issue_string)
    sprints = jira_issue.fields.customfield_10006
    for sprint in sprints:
        print sprint


def print_story(issue_string, with_tasks, file1 = None):
    story = jira.issue(issue_string)
    issue_type = story.fields.issuetype
    if str(issue_type) == 'Story':
        prepare_print_issue(issue_string, file1)
        if with_tasks:
            tasks = story.fields.subtasks
            for task_string in tasks:
                prepare_print_issue(task_string, file1)
    elif str(issue_type) == 'Task':
        prepare_print_issue(issue_string, file1)


search_string = 'project in (TCHCP, TCBE, TCADP) AND Sprint in openSprints() AND issuetype in (Story, Task)'
# search_string = 'project in (TCAPP) and Sprint in openSprints()'

issues = jira.search_issues(search_string, 0, 200)

print "'", search_string, "' [", len(issues), " issues]: "
file1 = open('./sprint.csv', 'w+')
for issue in issues:
    print_story(issue.key, True, file1)

