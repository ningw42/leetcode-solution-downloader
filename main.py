import requests
import json
import os
import time

ACCEPTED_IN_META = 'ac'
ACCEPTED_IN_DETAIL = 'Accepted'

def retrieve_solved_problems_of_active_session(session):
    resp = session.get('https://leetcode.com/api/problems/all/')
    j = json.loads(resp.text)

    # metadata
    metadata = {
        'solved': j['num_solved'],
        'total': j['num_total'],
        'easy': j['ac_easy'],
        'medium': j['ac_medium'],
        'hard': j['ac_hard'],
    }

    # solved problems
    solved_problems = []
    for problem in j['stat_status_pairs']:
        if problem['status'] == ACCEPTED_IN_META:
            solved_problems.append(problem)

    return metadata, solved_problems

def solution_retriever(language, session):
    def retriever(problem):
        url = f"https://leetcode.com/api/submissions/{problem['stat']['question__title_slug']}/"
        session.headers.update({'referer': f"https://leetcode.com/problems/{problem['stat']['question__title_slug']}"})
        resp = session.get(url)
        print(f"Downloading No.{problem['stat']['frontend_question_id']} {problem['stat']['question__title_slug']}")
        # print(resp.status_code)
        submissions = json.loads(resp.text)['submissions_dump']

        code = ''
        for submission in submissions:
            if submission['lang'] == language and submission['status_display'] == ACCEPTED_IN_DETAIL:
                code = submission['code']
                break

        return {
            'id': problem['stat']['question_id'],
            'frontend_id': problem['stat']['frontend_question_id'],
            'title': problem['stat']['question__title'],
            'title_slug': problem['stat']['question__title_slug'],
            'code': code, # may be empty
        }

    return retriever

def solution_saver(language, path):
    extensions = {
        'golang': 'go',
        'python': 'py',
    }

    if not os.path.exists(path):
        os.makedirs(path)

    def saver(solution):
        if solution['code']: 
            filename = f"{path}/{solution['frontend_id']}.{solution['title_slug']}.{extensions[language]}"
            f = open(filename, 'w')
            f.write(solution['code'])
            f.close()

    return saver


if __name__ == "__main__":
    session = requests.Session()
    session.headers.update({
        'cookie': 'COOKIE_HERE', # cookie from browser
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    })
    metadata, problems = retrieve_solved_problems_of_active_session(session)

    language = 'golang' # leetcode language id
    retriever = solution_retriever(language, session)
    saver = solution_saver(language, './solutions') # where to store solutions
    for problem in problems:
        saver(retriever(problem))
        time.sleep(5) # interval between each request, 5 seconds shoule be enough

