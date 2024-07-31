import argparse
import json
import os
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description='Generate a report of status of each beamline for a python version')
    parser.add_argument("-p", "--python_version", help="The python ver for Conda")
    parser.add_argument("-a", "--action_run", help="The ID(s) of current workflow")
    parser.add_argument("-n", "--num_python_vers", help="Length of matrix containing conda python versions")
    parser.add_argument("-f", "--file_name", default="workflow_info",
                        help="jsonfile containing info about previous job of current workflow")
    # parser.add_argument("-i", "--image_name", default="report",
    #                     help="Name of report image you want to save as svg")
    parser.add_argument("-o", "--org", default="StaticYolt",
                        help="organization of the repo to call GH api")
    parser.add_argument("-r", "--repo", default="nsls2-collection-tiled",
                        help="repository to find actions from")
    args = parser.parse_args()

    job_successes = []
    job_failures = []

    os.system(f'''gh api \
      -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    /repos/{args.org}/{args.repo}/actions/runs/{args.action_run}/jobs > {args.file_name}.json''')
    python_ver = str(args.python_version)
    f = open(f'{args.file_name}.json')
    data = json.load(f)
    total_jobs = int((data['total_count'] - 1)/ int(args.num_python_vers))
    for element in data['jobs']:
        element_name = element['name'].split('-')
        if len(element_name) > 4:
            element_python_version = element_name[3]
            element_beamline_acronym = element_name[5]
            if element['conclusion'] == "success" and element_python_version == python_ver:
                job_successes.append(f'{element_beamline_acronym}-{element_python_version}')
            elif element['conclusion'] == "failure" and element_python_version == python_ver:
                job_failures.append(f'{element_beamline_acronym}-{element_python_version}')

    weight = np.array([int(float(1 / total_jobs) * 100) for i in range(total_jobs)])
    my_labels = []
    my_colors = []
    for element in job_successes:
        my_labels.append(element)
        my_colors.append("g")
    for element in job_failures:
        my_labels.append(element)
        my_colors.append("r")
    my_explode = [.1 for i in range(total_jobs)]

    pie_chart = plt.pie(weight, labels=my_labels, explode=my_explode, colors=my_colors)
    plt.savefig(f'{python_ver}-report.svg')


if __name__ == "__main__":
    main()