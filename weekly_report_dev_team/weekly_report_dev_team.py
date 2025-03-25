#!/usr/bin/env python
"""
This script generates and sends weekly report for dev team under KAM process.

Usage: weekly_report_dev_team.py -h
"""

import os
import json
import argparse

from pathlib import Path
from datetime import datetime, timedelta
from jira import JIRA
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

if __name__ == '__main__':
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-js',
                        '--jiraserver',
                        help='address of the jira server',
                        type=str,
                        default='none')
    parser.add_argument('-jt',
                        '--jiratoken',
                        help='authentication token for the jira server',
                        type=str,
                        default='none')
    parser.add_argument('-bid',
                        '--boardid',
                        help='id of the project board',
                        type=str,
                        default='none')
    parser.add_argument('-tm',
                        '--teammembers',
                        help='name of team members to obtain and send info about',
                        type=list[str],
                        default=['nxg03754', 'nxg01989', 'nxg00008'])
    parser.add_argument('-etf',
                        '--emailtemplatefile',
                        help='name of the email template file',
                        type=str,
                        default='weekly_report_dev_team_outlook_template.htm')
    parser.add_argument('-etd',
                        '--emailtemplatedir',
                        help='name of the directory where the email template file is stored',
                        type=str,
                        default='templates')
    parser.add_argument('-ef',
                        '--emailfile',
                        help='name of the generated email file',
                        type=str,
                        default='weekly_report_dev_team_outlook_template.htm')
    parser.add_argument('-ed',
                        '--emaildir',
                        help='name of the directory where the generated email file is stored',
                        type=str,
                        default='output')
    args = parser.parse_args()

    # Parse .env file
    load_dotenv()
    JIRA_SERVER = os.getenv('JIRA_SERVER')
    JIRA_TOKEN = os.getenv('JIRA_TOKEN')
    BOARD_ID = os.getenv('BOARD_ID')
    TEAM_MEMBERS = json.loads(os.getenv('TEAM_MEMBERS'))

    if JIRA_SERVER is None:
        JIRA_SERVER = args.jiraserver
    if JIRA_TOKEN is None:
        JIRA_TOKEN = args.jiratoken
    if BOARD_ID is None:
        BOARD_ID = args.boardid
    if TEAM_MEMBERS is None:
        TEAM_MEMBERS = args.teammembers

    jira = JIRA(server=JIRA_SERVER, token_auth=JIRA_TOKEN)
    # Use this line instead if your board is well populated.
    # jira_sprints = jira.sprints(BOARD_ID, maxResults=1000, state='active')
    jira_sprints = jira.sprints(BOARD_ID, state='active')
    team_issues = []
    for jira_sprint in jira_sprints:
        sprint_issues = jira.search_issues(f'sprint={jira_sprint.id}', maxResults=False)
        for sprint_issue in sprint_issues:
            if sprint_issue.fields.assignee:
                assigned_to = sprint_issue.fields.assignee.name
                for team_member in TEAM_MEMBERS:
                    if assigned_to == team_member:
                        team_issues.append(sprint_issue)
                        break

    open_issues = []
    in_analysis_issues = []
    in_progress_issues = []
    in_review_issues = []
    resolved_issues = []
    for team_issue in team_issues:
        issue_status = team_issue.fields.status.name
        if issue_status == 'Open':
            open_issues.append(team_issue)
        elif issue_status == 'Analysis':
            in_analysis_issues.append(team_issue)
        elif issue_status == 'In Progress':
            in_progress_issues.append(team_issue)
        elif issue_status == 'In Review':
            in_review_issues.append(team_issue)
        elif issue_status == 'Resolved':
            resolved_issues.append(team_issue)
        else:
            pass

    open_issues_links = ''
    in_analysis_issues_links = ''
    in_progress_issues_links = ''
    in_review_issues_links = ''
    resolved_issues_links = ''
    for open_issue in open_issues:
        task_original_estimate = open_issue.fields.timetracking.originalEstimate if hasattr(open_issue.fields.timetracking, "originalEstimate") else "None"
        task_remaining_estimate = open_issue.fields.timetracking.remainingEstimate if hasattr(open_issue.fields.timetracking, "remainingEstimate") else "None"
        task_time_summary = f'{task_remaining_estimate} of estimated {task_original_estimate} remain'
        open_issues_links += f'<p class=MsoNormal><a href="https://jira.sw.nxp.com/browse/{open_issue.key}">[{open_issue.key}]</a><o:p> {open_issue.fields.summary} ({task_time_summary})</o:p></p>\n'
    for in_analysis_issue in in_analysis_issues:
        task_original_estimate = in_analysis_issue.fields.timetracking.originalEstimate if hasattr(in_analysis_issue.fields.timetracking, "originalEstimate") else "None"
        task_remaining_estimate = in_analysis_issue.fields.timetracking.remainingEstimate if hasattr(in_analysis_issue.fields.timetracking, "remainingEstimate") else "None"
        task_time_summary = f'{task_remaining_estimate} of estimated {task_original_estimate} remain'
        in_analysis_issues_links += f'<p class=MsoNormal><a href="https://jira.sw.nxp.com/browse/{in_analysis_issue.key}">[{in_analysis_issue.key}]</a><o:p> {in_analysis_issue.fields.summary} ({task_time_summary})</o:p></p>\n'
    for in_progress_issue in in_progress_issues:
        task_original_estimate = in_progress_issue.fields.timetracking.originalEstimate if hasattr(in_progress_issue.fields.timetracking, "originalEstimate") else "None"
        task_remaining_estimate = in_progress_issue.fields.timetracking.remainingEstimate if hasattr(in_progress_issue.fields.timetracking, "remainingEstimate") else "None"
        task_time_summary = f'{task_remaining_estimate} of estimated {task_original_estimate} remain'
        in_progress_issues_links += f'<p class=MsoNormal><a href="https://jira.sw.nxp.com/browse/{in_progress_issue.key}">[{in_progress_issue.key}]</a><o:p> {in_progress_issue.fields.summary} ({task_time_summary})</o:p></p>\n'
    for in_review_issue in in_review_issues:
        task_original_estimate = in_review_issue.fields.timetracking.originalEstimate if hasattr(in_review_issue.fields.timetracking, "originalEstimate") else "None"
        task_remaining_estimate = in_review_issue.fields.timetracking.remainingEstimate if hasattr(in_review_issue.fields.timetracking, "remainingEstimate") else "None"
        task_time_summary = f'{task_remaining_estimate} of estimated {task_original_estimate} remain'
        in_review_issues_links += f'<p class=MsoNormal><a href="https://jira.sw.nxp.com/browse/{in_review_issue.key}">[{in_review_issue.key}]</a><o:p> {in_review_issue.fields.summary} ({task_time_summary})</o:p></p>\n'
    for resolved_issue in resolved_issues:
        task_original_estimate = resolved_issue.fields.timetracking.originalEstimate if hasattr(resolved_issue.fields.timetracking, "originalEstimate") else "None"
        task_remaining_estimate = resolved_issue.fields.timetracking.remainingEstimate if hasattr(resolved_issue.fields.timetracking, "remainingEstimate") else "None"
        task_time_summary = f'{task_remaining_estimate} of estimated {task_original_estimate} remain'
        resolved_issues_links += f'<p class=MsoNormal><a href="https://jira.sw.nxp.com/browse/{resolved_issue.key}">[{resolved_issue.key}]</a><o:p> {resolved_issue.fields.summary} {(task_time_summary)}</o:p></p>\n'

    team_tempo = {}
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=4)
    for team_member in TEAM_MEMBERS:
        jql_query = f"""
            worklogAuthor = {team_member}
            AND worklogDate >= startOfWeek()
            AND worklogDate <= endOfWeek()
        """
        worklog_issues = jira.search_issues(jql_query, maxResults=1000)
        for worklog_issue in worklog_issues:
            issue_worklogs = jira.worklogs(worklog_issue.key)
            for worklog in issue_worklogs:
                if worklog.author.name == team_member:
                    # Sadly there is no support withing jql for time reporting.
                    # worklog_date = worklog.started.split("T")[0]
                    # if jira.jql(f"worklogDate = {worklog_date} AND worklogDate >= StartOfWeek() AND worklogDate <= endOfWeek()"):
                    worklog_date = datetime.strptime(worklog.started.split("T")[0], "%Y-%m-%d")
                    if start_of_week.date() <= worklog_date.date() <= end_of_week.date():
                        if team_member not in team_tempo:
                            team_tempo[team_member] = 0
                        team_tempo[team_member] += worklog.timeSpentSeconds / 3600
                        # print(f'Adding {worklog.timeSpentSeconds / 3600}h to {team_member} from issue {worklog_issue.key}')

    # Use this block if you want to know precise time for each team member.
    # print('\nTotal time logged for team:')
    # for team_member in TEAM_MEMBERS:
    #     print(f'{team_member}: {team_tempo[team_member]}h')
    # print('------------------------------')
    # print(f'total: {sum(team_tempo.values())}')

    open_issues_cnt = len(open_issues)
    if open_issues_cnt == 0:
        open_issues_text = "tickets are not yet started."
    elif open_issues_cnt > 1:
        open_issues_text = "tickets are not yet started, either awaiting prioritization or dependent on other tasks."
    else:
        open_issues_text = "ticket is not yet started, either awaiting prioritization or dependent on other tasks."

    in_analysis_issues_cnt = len(in_analysis_issues)
    if in_analysis_issues_cnt == 0:
        in_analysis_issues_text = "tickets are in the analysis phase."
    elif in_analysis_issues_cnt > 1:
        in_analysis_issues_text = "tickets are in the analysis phase to clarify requirements and identify potential dependencies."
    else:
        in_analysis_issues_text = "ticket is in the analysis phase to clarify requirements and identify potential dependencies."

    in_progress_issues_cnt = len(in_progress_issues)
    if in_progress_issues_cnt == 0:
        in_progress_issues_text = "tickets are actively being worked on and are on."
    elif in_progress_issues_cnt > 1:
        in_progress_issues_text = "tickets are actively being worked on and are on track for completion."
    else:
        in_progress_issues_text = "ticket is actively being worked on and is on track for completion."

    in_review_issues_cnt = len(in_review_issues)
    if in_review_issues_cnt == 0:
        in_review_issues_text = "tickets are currently under review."
    elif in_review_issues_cnt > 1:
        in_review_issues_text = "tickets are currently under review by the team/stakeholders."
    else:
        in_review_issues_text = "ticket is currently under review by the team/stakeholders."

    resolved_issues_cnt = len(resolved_issues)
    if resolved_issues_cnt == 0:
        resolved_issues_text = "tickets have been completed."
    elif resolved_issues_cnt > 1:
        resolved_issues_text = "tickets have been completed and are marked as done."
    else:
        resolved_issues_text = "ticket has been completed and is marked as done."

    jinja_env = Environment(loader=FileSystemLoader(args.emailtemplatedir))
    email_template = jinja_env.get_template(args.emailtemplatefile)
    email = email_template.render({
        "OPEN_COUNT": open_issues_cnt,
        "OPEN_TEXT": open_issues_text,
        "OPEN_LINKS": open_issues_links,
        "ANALYSIS_COUNT": in_analysis_issues_cnt,
        "ANALYSIS_TEXT": in_analysis_issues_text,
        "ANALYSIS_LINKS": in_analysis_issues_links,
        "IN_PROGRESS_COUNT": in_progress_issues_cnt,
        "IN_PROGRESS_TEXT": in_progress_issues_text,
        "IN_PROGRESS_LINKS": in_progress_issues_links,
        "IN_REVIEW_COUNT": in_review_issues_cnt,
        "IN_REVIEW_TEXT": in_review_issues_text,
        "IN_REVIEW_LINKS": in_review_issues_links,
        "RESOLVED_COUNT": resolved_issues_cnt,
        "RESOLVED_TEXT": resolved_issues_text,
        "RESOLVED_LINKS": resolved_issues_links,
        "HOURS_SPENT": round(sum(team_tempo.values()), 2)
    })

    with open(Path(args.emaildir) / args.emailfile, 'w', encoding='utf-8') as email_file:
        email_file.write(email)
