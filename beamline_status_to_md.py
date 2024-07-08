import argparse
import os
import json


def main():
    parser = argparse.ArgumentParser(description='Generate a report of status of each beamline for a python version')
    parser.add_argument("-p", "--python_version", default="3.10", help="The python ver for Conda")
    parser.add_argument("-a", "--action_run", default="9839701048", help="The ID(s) of current workflow")
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

    def get_check_run_url(ele_node):
        url = ""
        os.system(f'''gh api \
                -H "Accept: application/vnd.github+json" \
                -H "X-GitHub-Api-Version: 2022-11-28" \
                /repos/{args.org}/{args.repo}/check-runs/{ele_node['id']} > {args.check_run_json}.json''')
        with open(f'{args.check_run_json}.json') as file:
            check_data = json.load(file)

            step_num = -1 # Sentinel value
            start_line = -1
            annotation_level = ""
            message = ""

            steps = ele_node['steps']
            for step in steps:
                if step['conclusion'] == 'failure':
                    step_num = step['number']
                    break
                elif step['conclusion'] == 'warning':
                    step_num = step['number']
                    break

            # ele_node['id'] represents the check run ID of the job
            os.system(f'''gh api \
                    -H "Accept: application/vnd.github+json" \
                    -H "X-GitHub-Api-Version: 2022-11-28" \
                    /repos/{args.org}/{args.repo}/check-runs/{ele_node['id']}/annotations > {args.check_run_json}.json''')
            with open(f'{args.check_run_json}.json') as file_two:
                check_data = json.load(file_two)
                if check_data:
                    cdata = check_data[0]
                    start_line = cdata['start_line']
                    annotation_level = cdata['annotation_level']
                    message = cdata['message']
                    url = f"https://github.com/{args.org}/{args.repo}/actions/runs/{args.action_run}/job/{ele_node['id']}/#step:{step_num}:{start_line}"
                    if step_num == -1:
                        url = "-"
                else:
                    message = "-"
                    url = "-"
                return {'url': url, 'message': message, 'conclusion': annotation_level}
    def sort_by_py_version(data):
        for element in data['jobs']:
            # element name would look like "version ... srx-3.xx"
            if element['name'][-4:] == chosen_python_version:
                print(element)
                relevant_jobs.append(element)

    with open(f'{args.json_name}.json') as f:
        data = json.load(f)
        sort_by_py_version(data)
        for element in relevant_jobs:
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

    with open(f"{args.markdown_name}.md", "w") as md:
        md.write("### Success Rate: " + str(success_percentage) + "%\n")
        md.write("|Beamline|Conclusion|Message|URL|\n")
        md.write("|:---:|:---:|:---:|:---:|\n")

        # looping like this to give more control over sorting
        for element in relevant_jobs:
            if element:
                # gets "csx" from "version-matrix (3.10) / csx-3.10"
                element_name = element['name'].split(" ")[3].split("-")[0]
                results = get_check_run_url(element)
                match element['conclusion']:
                    case "failure":
                        failure_msg = "failure"
                        message = results['message'].replace("\n", " ")
                        md.write(f"|{element_name}|{failure_msg}|{message}|{results['url']}|\n")
                        print("failure")
                    case "success":
                        success_msg = "success"
                        message = results['message'].replace("\n", " ")
                        md.write(f"|{element_name}|{success_msg}|{message}|{results['url']}|\n")
                        print("success")
                    case "cancelled":
                        success_msg = "cancelled"
                        message = results['message'].replace("\n", " ")
                        md.write(f"|{element_name}|{success_msg}|{message}|{results['url']}|\n")
                        print("cancelled")
        md.close()

if __name__ == "__main__":
    main()