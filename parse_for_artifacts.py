import argparse
import os
import json


def main():
    parser = argparse.ArgumentParser(description='Parses Json and passes arguments to download-artifacts-sh')
    parser.add_argument("-o", "--organization", default="StaticYolt",
                        help="The organization the repository is under")
    parser.add_argument("-a", "--action_run", help="The ID of the workflow that was run")
    parser.add_argument("-f", "--file_name", default="artifact_info",
                        help="jsonfile containg info about all artifacts created from some repository")
    parser.add_argument("-r", "--repository", default="nsls2-collection-tiled")
    args = parser.parse_args()
    artifact_command = f'''
    gh api \\
            -H \"Accept: application/vnd.github+json\" \\
            -H \"X-GitHub-Api-Version: 2022-11-28\" \\
            /repos/{args.organization}/{args.repository}/actions/artifacts >> {args.file_name}.json
    '''
    os.system(artifact_command)
    with open(f"{args.file_name}.json") as f:
        data = json.load(f)
        for element in data['artifacts']:
            if element['workflow_run'].get('id') == int(args.action_run) and os.path.splitext(element['name'])[1] != '.yml':
                os.system(f"echo \"link: {str(element['url'])}\"")

                os.system(f"GHA_TOKEN={os.environ['GHA_TOKEN']} bash download-artifacts.sh "
                          f"{args.repository}"
                          f"{args.organization}"
                          f"{str(element['id'])}"
                          f"{str(element['name'])}")
            # print("url: " + str(element['url']))
            # print("artifact_id: " + str(element['id']))
            # print("repo_name: " + str(str(element['url']).split('/')[5]))
            # print("env_name: " + str(element['name']))

if __name__ == "__main__":
    main()