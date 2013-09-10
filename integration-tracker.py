import subprocess
import re

def run():
  config = open('integrations.txt')
  
  frombranch = tobranch = None
  exceptions = []

  outlines = []

  for line in config:
    if not line:
      continue #blank lines are skipped
    if '->' in line:
      if frombranch:
        outlines.extend(show_integrations(frombranch, tobranch, exceptions))
        exceptions = []
      (frombranch, _, tobranch) = line.split(None, 3)
    else:
      exception = from_int_line(line)
      if exception['status'] != '?':
        exceptions.append(exception)
  outlines.extend(show_integrations(frombranch, tobranch, exceptions))

  config.close()
  config = open('integrations.txt', 'w')
  config.write('\n'.join([l for l in outlines if l])) # filter out empty lines
  config.close()


def show_integrations(frombranch, tobranch, exceptions):
  outlines = [frombranch + ' -> ' + tobranch]
  ignore_hashes = set([exception['commit'] for exception in exceptions])
  fishy_commits = []

  master_commits = set(subprocess.check_output(['git', 'log', frombranch + '..' + tobranch, '--format=%H']).split('\n'))
  master_commits = filter(lambda x: x, master_commits) # filter out 

  # Find fishy commits according to 'git cherry' command
  git_cherry = subprocess.check_output(['git', 'cherry', '-v', tobranch, frombranch]).split('\n')
  for line in git_cherry[:-1]:
    (status, commit, message) = line.split(None, 2)
    if status is '+' and commit not in ignore_hashes:
      (user, date) = inspect_commit(commit)
      fishy_commits.append({'status': '?', 'user': user, 'date': date, 'commit': commit, 'message':message})

  # Filter out commits that were mentioned in the body of a tobranch commit
  mentioned_commits = set([commit_mentions(c) for c in master_commits])
  fishy_commits = filter(lambda c: c['commit'] not in mentioned_commits, fishy_commits)
  
  # Sort commits in descending order
  for commit in sorted(fishy_commits + exceptions, key=lambda c: -int(c['date'])):
    outlines.append(to_int_line(commit))

  plural = '' if len(fishy_commits) == 1 else 's'
  print '{frombranch} -> {tobranch}: Found {num} fishy commit{s} you should look at.'.format(
    frombranch=frombranch, tobranch=tobranch, num=len(fishy_commits), s=plural)

  return outlines


def inspect_commit(commit):
  (author, date) = subprocess.check_output(
    ['git', 'show', '--format=%ae %at', commit]).split('\n')[0].split(None, 1)
  return (author, date)


mentioned_commit_matcher = re.compile('\(cherry picked from commit (.*?)\)')

def commit_mentions(master_commit):
  body = subprocess.check_output(['git', 'show', '--format=%B', master_commit])
  match = mentioned_commit_matcher.search(body)
  if match and len(match.groups()):
    return match.group(1)
  else:
    return None


def from_int_line(line):
  (status, user, date, commit, message) = line.split(None, 4)
  return {'status': status, 'user': user, 'date': date, 'commit': commit, 'message': message}


def to_int_line(int_obj):
  return '{status} {user} {date} {commit} {message}'.format(**int_obj)


run()
