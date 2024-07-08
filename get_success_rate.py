import argparse
import os
import json
import subprocess


def main():
    parser = argparse.ArgumentParser(description='Generate a report of status of each beamline for a python version')
    parser.add_argument("-a", "--action_run", default="9839701048", help="The ID(s) of current workflow")
    parser.add_argument("-j", "--json_name", default="workflow_info",
                        help="jsonfile containing info about previous job of current workflow")
    parser.add_argument("-o", "--org", default="StaticYolt",
                        help="organization of the repo to call GH api")
    parser.add_argument("-r", "--repo", default="nsls2-collection-tiled",
                        help="repository to find actions from")
    args = parser.parse_args()
    os.system(f'''gh api \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        /repos/{args.org}/{args.repo}/actions/runs/{args.action_run}/jobs > {args.json_name}.json''')

    relevant_jobs = []
    success_jobs = []
    def sort_by_py_version(data):
        job_name = "3."
        for element in data['jobs']:
            if element['name'][-4:-2] == job_name:
                print(element)
                relevant_jobs.append(element)

    f = open(f'{args.json_name}.json')
    data = json.load(f)
    sort_by_py_version(data)
    for element in relevant_jobs:
        conclusion = element['conclusion']
        match conclusion:
            case "success":
                success_jobs.append(element)
            case _:
                # This should never happen
                print("ERROR")

    num_total_tests = len(relevant_jobs)
    num_success_jobs = len(success_jobs)
    success_percentage = int(float(num_success_jobs / num_total_tests) * 100)
    if success_percentage > 80:
        subprocess.run(['python', 'upload_artifacts.py'])
        print("RUNNING UPLOAD ARTIFACTS")

if __name__ == "__main__":
    main()