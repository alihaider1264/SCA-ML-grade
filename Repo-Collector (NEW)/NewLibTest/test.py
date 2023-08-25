from pydriller import Repository

for commit in Repository('https://github.com/ishepard/pydriller').traverse_commits():
    for file in commit.modified_files:
        if file.filename.endswith(".py"):
            print(file.source_code)