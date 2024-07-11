import argparse
import os
import json
import subprocess
import upload_artifacts
import requests
def main():
    parser = argparse.ArgumentParser(description='Generate a report of status of each beamline for a python version')
    parser.add_argument("-p", "--python_version", default="3.10", help="The python ver for Conda")
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
                # print(element)
                relevant_jobs.append(element)

    with open(f'{args.json_name}.json') as f:
        data = json.load(f)
        sort_by_py_version(data)
        for element in relevant_jobs:
            conclusion = element['conclusion']
            match conclusion:
                case "success":
                    success_jobs.append(element)
                case _:
                    # This should never happen
                    print("OTHER")

    num_total_tests = len(relevant_jobs)
    num_success_jobs = len(success_jobs)
    success_percentage = int(float(num_success_jobs / num_total_tests) * 100)

    if success_percentage > 50:
        conceptrecid = "84205" # never changes, it's for the initial version.
        version = "2024-2.2"
        token = os.environ["ZENODO_TOKEN"]
        resp = upload_artifacts.create_new_version(
            conceptrecid=conceptrecid,
            # version=f"{version}-tiled",
            version=f"{version}",
            token=f"{token}",
            # extra_files={"README.md": "r", "LICENSE": "r"}  # used for testing purposes
            extra_files={
                # # Python 3.8 (non-tiled)
                # f"{version}-py38-md5sum.txt": "r",
                # f"{version}-py38-sha256sum.txt": "r",
                # f"{version}-py38.yml": "r",
                # f"Dockerfile-{version}-py38": "r",
                # f"runner-{version}-py38.sh": "r",
                # f"{version}-py38.tar.gz": "rb",

                # # Python 3.9 (non-tiled)
                # f"{version}-py39-md5sum.txt": "r",
                # f"{version}-py39-sha256sum.txt": "r",
                # f"{version}-py39.yml": "r",
                # f"Dockerfile-{version}-py39": "r",
                # f"runner-{version}-py39.sh": "r",
                # f"{version}-py39.tar.gz": "rb",

                # # Python 3.10 (non-tiled)
                # f"{version}-py310-md5sum.txt": "r",
                # f"{version}-py310-sha256sum.txt": "r",
                # f"{version}-py310.yml": "r",
                # f"Dockerfile-{version}-py310": "r",
                # f"runner-{version}-py310.sh": "r",
                # f"{version}-py310.tar.gz": "rb",

                # # Python 3.11 (non-tiled)
                # f"{version}-py311-md5sum.txt": "r",
                # f"{version}-py311-sha256sum.txt": "r",
                # f"{version}-py311.yml": "r",
                # f"Dockerfile-{version}-py311": "r",
                # f"runner-{version}-py311.sh": "r",
                # f"{version}-py311.tar.gz": "rb",

                # # Python 3.8 (tiled)
                # f"{version}-py38-tiled-md5sum.txt": "r",
                # f"{version}-py38-tiled-sha256sum.txt": "r",
                # f"{version}-py38-tiled.yml": "r",
                # f"Dockerfile-{version}-py38-tiled": "r",
                # f"runner-{version}-py38-tiled.sh": "r",
                # f"{version}-py38-tiled.tar.gz": "rb",

                # # Python 3.9 (tiled)
                # f"{version}-py39-tiled-md5sum.txt": "r",
                # f"{version}-py39-tiled-sha256sum.txt": "r",
                # f"{version}-py39-tiled.yml": "r",
                # f"Dockerfile-{version}-py39-tiled": "r",
                # f"runner-{version}-py39-tiled.sh": "r",
                # f"{version}-py39-tiled.tar.gz": "rb",

                # Python 3.10 (tiled)
                f"{version}-py310-tiled-md5sum.txt": "r",
                f"{version}-py310-tiled-sha256sum.txt": "r",
                f"{version}-py310-tiled.yml.txt": "r",
                f"{version}-py310-tiled.tar.gz": "rb",

                # Python 3.11 (tiled)
                f"{version}-py311-tiled-md5sum.txt": "r",
                f"{version}-py311-tiled-sha256sum.txt": "r",
                f"{version}-py311-tiled.yml.txt": "r",
                f"{version}-py311-tiled.tar.gz": "rb",

                # Python 3.12 (tiled)
                f"{version}-py312-tiled-md5sum.txt": "r",
                f"{version}-py312-tiled-sha256sum.txt": "r",
                f"{version}-py312-tiled.yml.txt": "r",
                f"{version}-py312-tiled.tar.gz": "rb",
            },
        )
        # with open('upload_artifacts.py') as file:
        #     exec(file.read())
        # print("RUNNING UPLOAD ARTIFACTS")

if __name__ == "__main__":
    main()