import argparse
import os
import json

def main():
    parser = argparse.ArgumentParser(description='Generate a report of status of each beamline for a python version')
    parser.add_argument("-p", "--python_version", default="3.10", help="The python ver for Conda")
    parser.add_argument("-a", "--action_run", default="9784144631", help="The ID(s) of current workflow")
    parser.add_argument("-j", "--json_name", default="workflow_info",
                        help="jsonfile containing info about previous job of current workflow")
    parser.add_argument("-m", "--markdown_name", default="job_info",
                        help="markdown file containing info about previous job of current workflow")
    parser.add_argument("-c", "--check_run_json", default="check_run_info",
                        help="jsonfile containing info about previous check run of current workflow")
    parser.add_argument("-o", "--org", default="StaticYolt",
                        help="organization of the repo to call GH api")
    parser.add_argument("-r", "--repo", default="nsls2-collection-tiled",
                        help="repository to find actions from")
    args = parser.parse_args()
    os.system(f'''gh api \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        /repos/{args.org}/{args.repo}/actions/runs/{args.action_run}/jobs > {args.json_name}.json''')

    chosen_python_version = str(args.python_version)
    relevant_jobs = []
    success_jobs = []
    failure_jobs = []
    cancelled_jobs = []

    # Docs: https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28#get-a-check-run
    def get_check_run_info(org, repo, check_id, jfile):
        os.system(f'''gh api \
                        -H "Accept: application/vnd.github+json" \
                        -H "X-GitHub-Api-Version: 2022-11-28" \
                        /repos/{org}/{repo}/check-runs/{check_id} > {jfile}.json''')
    # Docs: https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28#list-check-run-annotations
    def get_annotation_info(org, repo, check_id, jfile):
        os.system(f'''gh api \
                            -H "Accept: application/vnd.github+json" \
                            -H "X-GitHub-Api-Version: 2022-11-28" \
                            /repos/{org}/{repo}/check-runs/{check_id}/annotations > {jfile}.json''')

    def get_check_run_url(ele_node):
        # ele_node['id'] represents the check run ID of the job
        get_check_run_info(args.org, args.repo, ele_node['id'], args.check_run_json)

        step_num = -1  # Sentinel value
        annotation_level = ""
        steps = ele_node['steps']
        for step in steps:
            if step['conclusion'] == 'failure':
                step_num = step['number']
                break
            elif step['conclusion'] == 'warning':
                step_num = step['number']

        get_annotation_info(args.org, args.repo, ele_node['id'], args.check_run_json)

        with open(f'{args.check_run_json}.json') as file_two:
            check_data = json.load(file_two)
            if check_data:
                cdata = check_data[0]
                start_line = cdata['start_line']
                annotation_level = cdata['annotation_level']
                msg = cdata['message']
                url = f"https://github.com/{args.org}/{args.repo}/actions/runs/{args.action_run}/job/{ele_node['id']}/#step:{step_num}:{start_line}"
                if step_num == -1:
                    url = "-"
            else:
                msg = "-"
                url = "-"
            return {'url': url, 'message': msg, 'conclusion': annotation_level}
    def sort_by_py_version(data):
        for element in data['jobs']:
            # element name would look like "version...srx-3.xx" so you try to get the "3.xx"
            if element['name'][-4:] == chosen_python_version:
                print(element)
                relevant_jobs.append(element)

    with open(f'{args.json_name}.json') as f:
        data = json.load(f)
        sort_by_py_version(data)
        for element in relevant_jobs:
            print(element)
            conclusion = element['conclusion']
            match conclusion:
                case "success":
                    success_jobs.append(element)
                case "failure":
                    failure_jobs.append(element)
                case "cancelled":
                    cancelled_jobs.append(element)
                case _:
                    # This should never happen because element['conclusion'] can only be success/failure/cancelled
                    print("ERROR")
        f.close()
    num_total_tests = len(relevant_jobs)
    num_success_jobs = len(success_jobs)
    success_percentage = int(float(num_success_jobs / num_total_tests) * 100)

    md_str = ""
    with open(f"{args.markdown_name}.md", "w") as md:

        md_str += "### Success Rate: " + str(success_percentage) + "%\n"
        md_str += "|Beamline|Conclusion|Message|URL|\n"
        md_str += "|:---:|:---:|:---:|:---:|\n"

        # looping more generally through relevant_jobs allows for potential sorting
        for element in relevant_jobs:
            if element:
                # gets "csx" from "version-matrix (3.10) / csx-3.10"
                element_name = element['name'].split(" ")[-1].split("-")[0].upper()
                results = get_check_run_url(element)
                match element['conclusion']:
                    case "failure":
                        failure_msg = "failure"
                        message = results['message'].replace("\n", " ")
                        md_str += f"|{element_name}|{failure_msg}|{message}|{results['url']}|\n"
                        print("failure")
                    case "success":
                        success_msg = "success"
                        message = results['message'].replace("\n", " ")
                        md_str += f"|{element_name}|{success_msg}|{message}|{results['url']}|\n"
                        print("success")
                    case "cancelled":
                        cancelled_msg = "cancelled"
                        message = results['message'].replace("\n", " ")
                        md_str += f"|{element_name}|{cancelled_msg}|{message}|{results['url']}|\n"
                        print("cancelled")
        md.write(md_str)
        md.close()

if __name__ == "__main__":
    main()