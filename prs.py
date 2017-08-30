# -*- coding: utf-8 -*-

import json, requests, sys, csv
from collections import defaultdict

def add_header():
    with open("output.csv", "wb") as myfile:
        myfile.write("login,name,email,company,blog,location,public_repos,followers,following,created_at,repo,pr_url,pr_created_at,pr_closed_at,pr_merged_at\n")

def str_en(att):
    try:
        if att == None or att == '':
            return "\"" + "None" + "\""
        if isinstance(att, int):
            return str(att)
        return "\"" + str(att.replace("\"", "''")) + "\""
    except UnicodeEncodeError, e:
        return "\"" + "None" + "\""
        #print att

class NoMorePagesAvailable(Exception):
    pass

class Casual():
    def __init__(self, **kwargs):
         vars(self).update(kwargs)

    def get_login(self):
        return self.login

    def get_pr(self):
        return self.pr

    def __repr__(self):
        return str(self.login + ", " + self.pr)

class PullRequest():
    def __init__(self, **kwargs):
        vars(self).update(kwargs)

    def get_login(self):
        return self.login

    def get_url(self):
        return self.url[29:]

    def get_created_at(self):
        return self.created_at

    def get_closed_at(self):
        return self.created_at

    def get_merged_at(self):
        return self.created_at

    def get_repo(self):
        return self.repo

    def __str__(self):
        return str(self.login)

    def __repr__(self):
        return str(self.login)

    def __eq__(self, other):
        return self.login == other.login


def formatter(casuals):
    items = []
    for casual in casuals:
        pr = casual.get_pr()
        personal = read_data(casual.get_login(), "users/")

        items.append([str_en(casual.get_login()),
                    str_en(personal['name']),
                    str_en(personal['email']),
                    str_en(personal['company']),
                    str_en(personal['blog']),
                    str_en(personal['location']),
                    str_en(personal['public_repos']),
                    str_en(personal['followers']),
                    str_en(personal['following']),
                    str_en(personal['created_at']),
                    str_en(pr.get_repo()),
                    str_en(pr.get_url()),
                    str_en(pr.get_created_at()),
                    str_en(pr.get_closed_at()),
                    str_en(pr.get_merged_at())])

    #add_header()
    for item in items:
        with open("output.csv", "a") as myfile:
            myfile.write(",".join(item) + "\n")


def read_data(repo, type = "repos/"):
    base = "https://api.github.com/" + type
    concat = "?" if type == "users/" else "&"
    token = concat + "&access_token=a63cf8ddeebd4c203477677c6a1aae53ba15aaa0"

    url = "%s%s%s" % (base, repo, token)

    resp = requests.get(url)
    if len(resp.text) == 2:
        raise NoMorePagesAvailable()
    else:
      return json.loads(resp.text)

def navigate_prs(project):
    print "Project: " + project
    max_pages = 100000
    prs = []

    for page in range(1, max_pages):
        repo = "%s/pulls?page=%s&state=closed&per_page=100" % (project, page)

        try:
            prs.extend([PullRequest(
                login=pr['user']['login'],
                url=pr['url'],
                created_at=pr['created_at'],
                closed_at=pr['closed_at'],
                merged_at=pr['merged_at'],
                repo=pr['base']['repo']['full_name']) for pr in read_data(repo) if pr['merged_at'] is not None])

            print "Total of accepted PRs found so far: " + str(len(prs))

        except NoMorePagesAvailable:
            print("We are done downloading PRs for " +project + "!")
            break

    casuals = find_casuals(prs)
    print "Total casuals found: " + str(len(casuals))

    formatter(casuals)

def find_casuals(prs):
    d = defaultdict(int)
    casuals = []

    for pr in prs:
        d[pr.get_login()] += 1

    for key, value in d.items():
        if value == 1:
            for pr in prs:
                if pr.get_login() == key:
                    casuals.append(Casual(login=key, pr=pr))
                    break
    return casuals


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        print "No arguments provided!"
        exit(0)

    lines = open("repo-domains.csv").readlines()

    f, t = int(sys.argv[1]), int(sys.argv[2])

    for line in lines[f:t]:
        columns = line.split(";")
        #print columns[0]
        navigate_prs(columns[0])
