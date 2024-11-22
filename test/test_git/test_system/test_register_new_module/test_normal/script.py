import os
import sys
import shutil
from pathlib import Path
import tempfile
import subprocess
from git import Repo
import signal

import os

# remove existing environment variables
del os.environ["YAM_PROJECT"]
del os.environ["YAM_PROJECT_CONFIG_DIR"]

# cwd = Path(os.getcwd())
# pyam = str(cwd.parents[3]) + "/pyam"
# common_folder = os.path.join(str(cwd.parents[2]),"common")
pyam = "pyam"
yam_root = os.getenv("YAM_ROOT")
common_folder = os.path.join(yam_root, "src", "pyam", "test", "common")

# create outer temp folder that holds everything
test_folder = Path(tempfile.mkdtemp(dir=".", prefix="TestContainerFolder_")).resolve()
# fakedatatar = '/home/atbe/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC34-2/src/tmp/pyamfakedata.tar.gz'
fakedatatar = "../../../../common/pyamfakedata.tar.gz"
os.system(f"tar zxf {fakedatatar}  -C {test_folder}")
os.system(f"mv  {test_folder}/pyamfakedata/* {test_folder}")

sandbox_dir = os.path.join(test_folder, "FakeSandbox")

git_remotes = os.path.join(test_folder, "fake_git_repositories")
svn_repo_folder = os.path.join(test_folder, "fake_svn_repository")
svn_repo_url = f"file://{svn_repo_folder}"
release_dir = os.path.join(test_folder, "fake_release")
module_repos_folder = os.path.join(git_remotes, "Modules")

# #create outer temp folder that holds everything
# test_folder = Path(tempfile.mkdtemp(dir=".",prefix="TestContainerFolder_")).resolve()
#
# #All git-backed remotes will live here
# git_remotes = os.path.join(test_folder, "GitRemotes")
# os.mkdir(git_remotes)
#
# #create directory to hold all repos and create release directory
# module_repos_folder = os.path.join(git_remotes, "Modules")
# release_dir = os.path.join(git_remotes, "Releases")
# os.mkdir(release_dir)
# os.mkdir(module_repos_folder)
#
# #make the sandbox
# sandbox_dir = os.path.join(test_folder, "Sandbox")
# os.mkdir(sandbox_dir)
# os.system(os.path.join(common_folder, "sandbox", "make_fake_sandbox.bash")+f" {sandbox_dir}")

# Begin MySQL DB
returnval = (
    subprocess.check_output(["python3", common_folder + "/mysql/runmysql.py", common_folder]).decode("UTF-8").split()
)
# returnval = returnval.decode('UTF-8').split()
mysqlpid, mysqlport = int(returnval[0]), int(returnval[1])
# print("pid, port", mysqlpid, mysqlport)

os.chdir(sandbox_dir)


# choose register-new-module parameters
options = [
    "--quiet",
    '--release-directory="{rel_dir}"'.format(rel_dir=str(release_dir)),  # .resolve())),
    "--no-build-server",
    '--database-connection="127.0.0.1:{port}/test"'.format(port=mysqlport),
    '--default-repository-url="{repo_url}"'.format(repo_url=str(svn_repo_url)),
    '--keyword-to-repository-url="git={repo_url}"'.format(repo_url=str(git_remotes)),
]

options_str = " ".join(options)

# --------------------------------------------------------------------------------
print("====== CREATING NEW MyNewGitModule MODULE ")

# Run the register-new-module-command
reg_new_mod = "register-new-module MyNewGitModule --repository-keyword=git"

os.system(f"{str(pyam)} {options_str} {reg_new_mod}")


new_release_dir = os.path.join(release_dir, "Module-Releases", "MyNewGitModule", "MyNewGitModule-R1-00")

# check that above command created release directory
if not os.path.isdir(new_release_dir):
    os.killpg(os.getpgid(mysqlpid), signal.SIGTERM)
    raise ValueError(f"ERROR: Module's release directory was not created at {release_dir}")

# it should also have made the repo in the remotes folder
repo_dir = os.path.join(module_repos_folder, "MyNewGitModule")
if not os.path.isdir(repo_dir):
    os.killpg(os.getpgid(mysqlpid), signal.SIGTERM)
    raise ValueError(f"ERROR: Module's repo directory was not created at {repo_dir}")

print("Register New Module Command Done")

# --------------------------------------------------------------------------------
print("====== CHECKING OUT MyNewGitModule-R1-00 my_branch BRANCH")

# Fill in YAM.config
config_file = os.path.join(sandbox_dir, "YAM.config")
with open(config_file, "w") as config:
    config.write("WORK_MODULES = MyNewGitModule Dshell++\n")
    config.write("BRANCH_MyNewGitModule = MyNewGitModule-R1-00\n ")
    config.write("BRANCH_Dshell++ = Dshell++-R4-06g ")

# Check out branched module
checkout = "checkout 'MyNewGitModule'"  # --repository-keyword=git"
os.system(f"{str(pyam)} {options_str} {checkout}")

checkout = "checkout 'Dshell++'"  # --repository-keyword=git"
os.system(f"{str(pyam)} {options_str} {checkout}")

# --------------------------------------------------------------------------------
print("====== CHECK LATEST MyNewGitModule RELEASE ")

# Check the latest release value
cmd = "latest 'MyNewGitModule'  Dshell++"
os.system(f"{str(pyam)} {options_str} {cmd}")

print("Repo tags=")
os.system(f"git -C {repo_dir} tag")
print("Release tags in release dir=")
os.system(f"git -C {new_release_dir} tag")
print("Branch in release dir (should be none)")
os.system(f"git -C {new_release_dir} tag")

# end test db by sending kill signal to the process group that contains it
os.killpg(os.getpgid(mysqlpid), signal.SIGTERM)

# delete temp test folder
shutil.rmtree(test_folder)
print("OK")
