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

# All git-backed remotes will live here
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
    #    '--default-repository-url="git={repo_url}"'.format(repo_url=str(module_repos_folder))#.resolve())),
    '--default-repository-url="{repo_url}"'.format(repo_url=str(svn_repo_url)),
    '--keyword-to-repository-url="git={repo_url}"'.format(repo_url=str(git_remotes)),  # .resolve())),
]

options_str = " ".join(options)

repo_dir = os.path.join(module_repos_folder, "MyNewGitModule")

# --------------------------------------------------------------------------------
print("====== CREATING NEW MyNewGitModule MODULE ")

# Run the register-new-module-command
reg_new_mod = "register-new-module MyNewGitModule --repository-keyword=git"


os.system(f"{str(pyam)} {options_str} {reg_new_mod}")

# check that above command created release directory
new_release_dir = os.path.join(release_dir, "Module-Releases", "MyNewGitModule", "MyNewGitModule-R1-00")

print("Repo tags=")
os.system(f"git -P -C {repo_dir} tag")
print("Repo branches=")
os.system(f"git -P -C {repo_dir} branch")


print("Release tag=")
os.system(f"git -P -C {new_release_dir} describe --tags")

print("Release branch=")
os.system(f"git -P -C {new_release_dir} branch")
os.system(f"git -P -C {new_release_dir} status -b")


# --------------------------------------------------------------------------------
print("====== CHECKING LATEST RELEASE ")

# check latest release
os.system(f"{str(pyam)} {options_str} latest MyNewGitModule")


# Added by Abhi (not sure if needed because the previous comment is
# saying that it should have been created
# os.system('mkdir -p %s' % new_release_dir)
if not os.path.isdir(new_release_dir):
    os.killpg(os.getpgid(mysqlpid), signal.SIGTERM)
    raise ValueError(f"ERROR: Module's release directory was not created at {release_dir}")
print("Register New Module Command Done")

# --------------------------------------------------------------------------------
print("====== CHECKING OUT MyNewGitModule-R1-00 my_branch BRANCH")

# Fill in YAM.config
config_file = os.path.join(sandbox_dir, "YAM.config")
with open(config_file, "w") as config:
    config.write("WORK_MODULES = MyNewGitModule\n")
    config.write("BRANCH_MyNewGitModule = MyNewGitModule-R1-00 my_branch")

# Check out branched module
checkout = "checkout 'MyNewGitModule'"  # --repository-keyword=git"
os.system(f"{str(pyam)} {options_str} {checkout}")

# --------------------------------------------------------------------------------
print("====== MODIFYING MyNewGitModule R1-00 branch MODULE ")

# add files to this branch in the sandbox
new_mod_dir = os.path.join(sandbox_dir, "src", "MyNewGitModule")
print("Checked out tag=")
os.system(f"git -P -C {new_mod_dir} tag")
print("Checked out branch=")
os.system(f"git -P -C {new_mod_dir} branch")
os.system(f"git -P -C {new_mod_dir} status")


os.chdir(new_mod_dir)
new_file = os.path.join(new_mod_dir, "hey.txt")
with open(new_file, "w") as f:
    f.write("Hello There")
repo = Repo(new_mod_dir)
repo.git.add("hey.txt")
repo.index.commit("Added hey.txt to branch")
repo.git.push()

os.chdir(sandbox_dir)

# remove the MyNewGitModule folder so we can check out again and see if the new file is in there
shutil.rmtree(new_mod_dir)

# --------------------------------------------------------------------------------
print("====== RE-CHECKOUT MyNewGitModule R1-00 branch ")


os.system(f"{str(pyam)} {options_str} {checkout}")

print("Checked out1 tag=")
os.system(f"git -P -C {new_mod_dir} tag")
print("Checked out1 branch=")
os.system(f"git -P -C {new_mod_dir} branch")

# hey.txt should exist in the checkout pyam directory, but it should not exist in the remote
# this is because the remote is still on master branch and hey.txt exists only on the branch that was just created
if not os.path.isfile(new_file):
    os.killpg(os.getpgid(mysqlpid), signal.SIGTERM)
    raise ValueError(f"ERROR: Files of a branch should exist after checking out that branch")
if os.path.isfile(os.path.join(module_repos_folder, "MyNewGitModule", "hey.txt")):
    os.killpg(os.getpgid(mysqlpid), signal.SIGTERM)
    raise ValueError(f"ERROR: Files added to branch should not be in master of remote until we save")

# --------------------------------------------------------------------------------
print("====== SAVING MyNewGitModule R1-00 branch as R1-00a  ")

# run save command
cwd = "./"
save_editor = f"EDITOR = {os.path.join(cwd,'fake-editor')} 'Fake message'"
save_options = [
    " --quiet",
    "--require-bug-id",
    "--no-build-server",
    '--database-connection="127.0.0.1:{port}/test"'.format(port=mysqlport),
    '--release-directory="{rel_dir}"'.format(rel_dir=str(release_dir)),
    '--keyword-to-repository-url="git={repo_url}"'.format(repo_url=str(git_remotes)),
    f'--default-repository-url="{str(git_remotes)}"',
]
save_str = " ".join(save_options)

# run the save command
final_cmd = f" {str(pyam)} {save_str} save --bug-id='' MyNewGitModule --username='somedude'"
os.system(final_cmd)

# check latest release
os.system(f"{str(pyam)} {options_str} latest MyNewGitModule")


new_release_dir = os.path.join(release_dir, "Module-Releases", "MyNewGitModule", "MyNewGitModule-R1-00a")

print("Repo tags=")
os.system(f"git -P -C {repo_dir} tag")
print("Repo branches=")
os.system(f"git -P -C {repo_dir} branch")

print("Release tags=")
os.system(f"git -P -C {new_release_dir} tag")
os.system(f"git -P -C {new_release_dir} describe --tags")
print("Release branch=")
os.system(f"git -P -C {new_release_dir} status")


print("DONE SAVING, CHECKING OUT AGAIN")

# --------------------------------------------------------------------------------
print("====== CHECKOUT SAVED MyNewGitModule MODULE ")


os.system(f"{str(pyam)} {options_str} {checkout}")

print("Checked out2 tag=")
os.system(f"git -P -C {new_mod_dir} tag")
print("Checked out2 branch=")
os.system(f"git -P -C {new_mod_dir} branch")

# --------------------------------------------------------------------------------
print("====== MODIFY MyNewGitModule MODULE ")

# add files to this branch in the sandbox
new_mod_dir = os.path.join(sandbox_dir, "src", "MyNewGitModule")
os.chdir(new_mod_dir)
new_file = os.path.join(new_mod_dir, "heythere.txt")
with open(new_file, "w") as f:
    f.write("Hey There")
repo = Repo(new_mod_dir)
repo.git.add("heythere.txt")
repo.index.commit("Added heythere.txt to branch")
repo.git.push()
os.chdir(sandbox_dir)

# --------------------------------------------------------------------------------
print("====== RE-SAVE  MyNewGitModule MODULE ")

os.system(final_cmd)

print("Repo branches=")
os.system(f"git -P -C {repo_dir} branch")
print("Repo tags=")
os.system(f"git -P -C {repo_dir} tag")


new_release_dir = os.path.join(release_dir, "Module-Releases", "MyNewGitModule", "MyNewGitModule-R1-00b")


print("Release tags=")
os.system(f"git -P -C {new_release_dir} tag")
os.system(f"git -P -C {new_release_dir} describe --tags")
print("Release branch=")
os.system(f"git -P -C {new_release_dir} status")


# --------------------------------------------------------------------------------
print("====== CHECKOUT MyNewGitModule MODULE ")

os.system(f"{str(pyam)} {options_str} scrap --remove MyNewGitModule")

check_cmd = f"{str(pyam)} {options_str} {checkout} --release R1-00a --branch -"
# print("RUNNING: ", check_cmd)
os.system(check_cmd)

# --------------------------------------------------------------------------------
print("====== CHECK LATEST MyNewGitModule MODULE RELEASE")

# check latest release
os.system(f"{str(pyam)} {options_str} latest MyNewGitModule")


print("Checked out3 tag=")
os.system(f"git -P -C {new_mod_dir} describe --tags")
print("Checked out3 branch=")
os.system(f"git -P -C {new_mod_dir} branch")


# heythere = os.path.join(,"heythere.txt")


# end test db by sending kill signal to the process group that contains it
os.killpg(os.getpgid(mysqlpid), signal.SIGTERM)

shutil.rmtree(test_folder)


print("OK")
