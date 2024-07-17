import argparse
import datetime
import os
import json
import subprocess
import time
from pprint import pprint

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
            #and os.path.splitext(element['name'])[1] != '.yml'
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
        conceptrecid = "12688274" # never changes, it's for the initial version.
        version = "2024-2.1"
        token = os.environ["ZENODO_TOKEN"]
        upload_artifacts.create_new_version(conceptrecid=conceptrecid,
                         version=version,
                         token=token,
                         extra_files={
                            # Python 3.10 (tiled)
                            f"{version}-py310-tiled-md5sum.txt": "r",
                            f"{version}-py310-tiled-sha256sum.txt": "r",
                            f"{version}-py310-tiled.tar.gz": "rb",
                            f"{version}-py310-tiled.yml.txt": "r",

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
                         })
        # resp = upload_artifacts.create_new_version(
        #     conceptrecid=conceptrecid,
        #     # version=f"{version}-tiled",
        #     version=f"{version}",
        #     token=f"{token}",
        #     # extra_files={"README.md": "r", "LICENSE": "r"}  # used for testing purposes
        #     extra_files={
        #         # Python 3.10 (tiled)
        #         f"{version}-py310-tiled-md5sum.txt": "r",
        #         f"{version}-py310-tiled-sha256sum.txt": "r",
        #         f"{version}-py310-tiled.yml.txt": "r",
        #         f"{version}-py310-tiled.tar.gz": "rb",
        #
        #         # Python 3.11 (tiled)
        #         f"{version}-py311-tiled-md5sum.txt": "r",
        #         f"{version}-py311-tiled-sha256sum.txt": "r",
        #         f"{version}-py311-tiled.yml.txt": "r",
        #         f"{version}-py311-tiled.tar.gz": "rb",
        #
        #         # Python 3.12 (tiled)
        #         f"{version}-py312-tiled-md5sum.txt": "r",
        #         f"{version}-py312-tiled-sha256sum.txt": "r",
        #         f"{version}-py312-tiled.yml.txt": "r",
        #         f"{version}-py312-tiled.tar.gz": "rb",
        #     },
        # )
        # with open('upload_artifacts.py') as file:
        #     exec(file.read())
        # print("RUNNING UPLOAD ARTIFACTS")

if __name__ == "__main__":
    main()

#     def upload_to_zenodo(conceptrecid=None, version=None, extra_files=None, token=None):
#         if extra_files is None:
#             raise ValueError(
#                 "Files cannot be None, specify a dict with file names "
#                 "as keys and access mode as values"
#             )
#         notes_urls = [
#             # # non-tiled
#             # "https://github.com/nsls2-conda-envs/nsls2-collection/pull/28",
#             # "https://github.com/nsls2-conda-envs/nsls2-collection/actions/runs/7603753363",
#             # # need this empty line to enforce line break on Zenodo:
#             # "",
#             # tiled
#             "https://github.com/nsls2-conda-envs/nsls2-collection-tiled/pull/39",
#             "https://github.com/nsls2-conda-envs/nsls2-collection-tiled/actions/runs/9762354757",
#         ]
#         notes_urls_strs = "<br>\n".join([f'<a href="{url}">{url}</a>'
#                                          if url else ""
#                                          for url in notes_urls])
#
#         unpack_instructions = """
#         Unpacking instructions:
#         <br>
#         <pre>
#         mkdir -p ~/conda_envs/&lt;env-name&gt;
#         cd ~/conda_envs/&lt;env-name&gt;
#         wget &lt;url-to&gt;/&lt;env-name&gt;.tar.gz
#         tar -xvf &lt;env-name&gt;.tar.gz
#         conda activate $PWD
#         conda-unpack
#         </pre>
#         """
#         data = {
#             "metadata": {
#                 "version": version,
#                 "title": f"NSLS-II collection conda environment version with Python 3.10, 3.11, and 3.12",
#                 "description": f"NSLS-II collection environment deployed to the experimental floor.<br><br>{notes_urls_strs}",
#                 "upload_type": "software",
#                 "publication_date": datetime.datetime.now().strftime("%Y-%m-%d"),
#                 "publisher": "NSLS-II, Brookhaven National Laboratory",
#                 "prereserve_doi": True,
#                 "keywords": [
#                     "conda",
#                     "NSLS-II",
#                     "bluesky",
#                     "data acquisition",
#                     "conda-forge",
#                     "conda-pack",
#                 ],
#                 "additional_descriptions": [
#                     {
#                         "description": unpack_instructions,
#                         "type": {
#                             "id": "notes",
#                             "title": {
#                                 "en": "Unpacking instructions"
#                             }
#                         },
#                     },
#                 ],
#                 "creators": [
#                     {
#                         'name': 'Rakitin, Max',
#                         'affiliation': 'NSLS-II, Brookhaven National Labratory',
#                         'orcid': '0000-0003-3685-852X',
#                     },
#                     {
#                         'name': 'Bischof, Garrett',
#                         'affiliation': 'NSLS-II, Brookhaven National Labratory',
#                         'orcid': '0000-0001-9351-274X',
#                     },
#                     {
#                         'name': 'Aishima, Jun',
#                         'affiliation': 'NSLS-II, Brookhaven National Labratory',
#                         'orcid': '0000-0003-4710-2461',
#                     },
#                 ],
#             }
#         }
#         ret_ver = requests.get(
#             url=f"https://sandbox.zenodo.org/api/deposit/depositions/{conceptrecid}?access_token={token}",
#             headers={"Content-Type": "application/json"})
#         pprint(ret_ver.json())
#
#         new_ver_link = ret_ver.json()['links']['newversion']
#
#         new_ver = requests.post(url=new_ver_link,
#                                 headers={"Content-Type": "application/json"},
#                                 data=json.dumps(data),
#                                 params={"access_token": token})
#         pprint(new_ver.json())
#
#         for depot_file in new_ver.json()['files']:
#             requests.delete(url=depot_file['links']['self'],
#                             params={"access_token": token})
#
#         for upload_file, mode in extra_files.items():
#             basename = os.path.basename(upload_file)
#             if mode == "rb":
#                 pass
#             elif mode == "r":
#                 r = requests.post(url=new_ver.json()['links']['files'],
#                                   data={'name': upload_file},
#                                   files={'file': open(basename, mode)},
#                                   params={'access_token': token})
#                 pprint(r.json())
#                 # Avoid error trace is misleading it should be something like "No connection could be made because the target machine actively refused it".
#             time.sleep(1)