import shutil
import sys
import os
import tempfile
import tarfile
from git import Repo

fakedir_target_path = os.path.abspath(sys.argv[1])

fake_git_folder = fakedir_target_path  # tempfile.mkdtemp(dir=fakedir_target_path, prefix="FakeGitRepo_")
containing_folder = os.getcwd()
# cd into temp folder where fake repo will go
# os.chdir(fake_git_folder)

# create the Repo
repo = Repo.init(fake_git_folder)

common_folder = os.path.dirname(sys.argv[0])

# add and make the first commit
repo.git.add(fake_git_folder + "/.")
repo.index.commit("Initial Commit for Register New Module Test")


# os.chdir(containing_folder)


print("Done making fake git repo")
