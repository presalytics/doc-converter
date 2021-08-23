import yaml  # type: ignore
import git  # type: ignore
import os
import pathlib

if __name__ == '__main__':
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    manifests_dir = pathlib.Path(__file__).parent.absolute().parent.absolute().joinpath('manifests')
    for manifest in os.listdir(manifests_dir):
        file = manifests_dir.joinpath(manifest)
        try:
            data = {}
            with open(file) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
            if data['apiVersion'] == 'serving.knative.dev/v1' and data['kind'] == 'Service':
                data['spec']['template']['metadata']['labels']['gitHash'] = sha
            with open(file, "w") as f:
                f.write(yaml.dump(data, default_flow_style=False))
            print("gitHash label of manifest {0} updated to {1}".format(manifest, sha))
        except Exception as ex:
            print("Hash update operation failed")
            print("Error: " + ex.args[1])
            exit(1)
