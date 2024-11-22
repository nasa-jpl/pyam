import os
import contextlib
import unittest

from yam import make_build_system


class MakeBuildSystemTestCase(unittest.TestCase):
    def setUp(self):
        """Automatically called before each test* method."""
        self.__build_system = make_build_system.MakeBuildSystem(native_operating_system="foo", site_name="fake_site")

    def test_build_with_missing_module_raises_error(self):
        from yam import yam_exception

        with self.assertRaises(yam_exception.YamException):
            self.__build_system.build(module_names=["Blah"], sandbox_directory="NonExistentSandbox")

    def test_build(self):
        module_names = ["ModuleA", "ModuleB"]
        self.assertTrue(self.__build_system.build(module_names=module_names, sandbox_directory="FakeSandbox"))
        os.remove("FakeSandbox/root")
        self.__check_file(module_names=module_names, filename="FakeSandbox/all")

    def test_build_with_progress(self):
        message_list = []
        done_list = []

        def progress_callback(message, done, rule):
            message_list.append(message)
            done_list.append(done)

        module_names = ["ModuleA", "ModuleB"]
        build_system = make_build_system.MakeBuildSystem(
            native_operating_system="foo",
            site_name="fake_site",
            progress_callback=progress_callback,
        )

        # Run the build call, which should trigger the progress callback
        self.assertTrue(build_system.build(module_names=module_names, sandbox_directory="FakeSandbox"))

        # Check progress calls
        self.assertTrue(message_list)
        self.assertTrue(done_list)

        # Make sure last done call was True
        self.assertTrue(done_list[-1])

        # Make sure build works like usual
        os.remove("FakeSandbox/root")
        self.__check_file(module_names=module_names, filename="FakeSandbox/all")

    def test_clean(self):
        module_names = ["ModuleA", "ModuleB"]
        self.assertTrue(self.__build_system.clean(module_names=module_names, sandbox_directory="FakeSandbox"))
        self.__check_file(module_names=module_names, filename="FakeSandbox/clean")

    def test_make_links(self):
        module_names = ["ModuleA", "ModuleB"]
        self.assertTrue(
            self.__build_system.make_links(
                module_names=module_names,
                sandbox_directory="FakeSandbox",
                release_directory="my_release_directory",
            )
        )
        self.__check_file(
            module_names=module_names,
            filename="FakeSandbox/mklinks",
            extra=" release_directory=my_release_directory/Module-Releases site_name=fake_site",
        )

    def test_make_links_with_site_defs(self):
        module_names = ["ModuleA", "SiteDefs"]
        self.assertTrue(
            self.__build_system.make_links(
                module_names=module_names,
                sandbox_directory="FakeSandbox",
                release_directory="my_release_directory",
            )
        )

        self.__check_file(
            module_names=module_names,
            filename="FakeSandbox/mklinks",
            extra=" release_directory=my_release_directory/Module-Releases site_name=fake_site",
        )

    def test_make_links_with_non_existent_release_directory(self):
        from yam import yam_exception

        with self.assertRaises(yam_exception.YamException):
            self.assertTrue(
                self.__build_system.make_links(
                    module_names=["ModuleA"],
                    sandbox_directory="FakeSandbox",
                    release_directory="my_non_existent_release_directory",
                )
            )

    def test_remove_links(self):
        module_names = ["ModuleA", "ModuleB"]
        self.assertTrue(
            self.__build_system.remove_links(
                module_names=module_names,
                sandbox_directory="FakeSandbox",
                release_directory=None,
            )
        )
        self.__check_file(module_names=module_names, filename="FakeSandbox/rmlinks")

    def test_yam_root_is_not_defined_by_make(self):
        module_names = ["ModuleA", "ModuleB"]
        self.assertTrue(self.__build_system.build(module_names=module_names, sandbox_directory="FakeSandbox"))

        self.assertTrue(os.path.exists("FakeSandbox/root"))
        with open("FakeSandbox/root", "r") as all_file:
            self.assertEqual(all_file.read().strip(), "YAM_ROOT is not defined")
        os.remove("FakeSandbox/root")

        self.__check_file(module_names=module_names, filename="FakeSandbox/all")

    def test_create_build_files(self):
        paths = []

        def callback(path):
            paths.append(path)

        with temporary_directory_context() as temporary_directory:
            self.__build_system.create_build_files(
                path=temporary_directory,
                release_directory="my_release_directory",
                operating_system_name="my_operating_system",
                top_level_file_callback=callback,
            )

            files = list(find_file_base_names(temporary_directory))
            self.assertIn("Drun", files)
            self.assertIn("Makefile.yam", files)
            self.assertIn("makefile-yam-tail.mk", files)
            self.assertIn("site-config-my_operating_system", files)

            self.assertIn(
                "Makefile.top",
                os.listdir(os.path.join(temporary_directory, "mkHome", "shared")),
            )

            for _, dirs, files in os.walk(temporary_directory):
                self.assertNotIn(".svn", dirs)
                for name in dirs + files:
                    self.assertFalse(
                        name.startswith("."),
                        "Hidden files should not be copied",
                    )

    def test_create_module_files(self):
        paths = []

        def callback(path):
            paths.append(path)

        with temporary_directory_context() as temporary_directory:
            self.__build_system.create_module_files(
                module_name="FakeModule",
                module_path=temporary_directory,
                top_level_file_callback=callback,
            )

            files = list(find_file_base_names(temporary_directory))
            for name in [
                "Makefile.yam",
                "ChangeLog",
                "ReleaseNotes",
                "YamVersion.h",
            ]:
                self.assertIn(name, files)

                self.assertIn(os.path.join(temporary_directory, name), paths)

    def test_make_children_executable(self):
        with temporary_directory_context() as temporary_directory:
            os.mkdir(os.path.join(temporary_directory, ".hidden"))

            script_name = os.path.join(temporary_directory, "blah.bash")
            with open(script_name, "w") as output_file:
                output_file.write("#!/bin/bash\n")

            non_script_name = os.path.join(temporary_directory, "blah.txt")
            with open(script_name, "w") as output_file:
                output_file.write("#!/bin/bash\n")

            import subprocess

            with self.assertRaises(OSError):
                subprocess.check_call([script_name])

            with self.assertRaises(OSError):
                subprocess.check_call([non_script_name])

            make_build_system.make_children_executable(temporary_directory, extensions=[".bash"])

            subprocess.check_call([script_name])

            # Should still be the case
            with self.assertRaises(OSError):
                subprocess.check_call([non_script_name])

    def test_parse_dependency_file(self):
        self.assertEqual(
            [
                "DScene_swigwrap_Py.cc",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/Base.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/Color.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/TriangleMesh.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/SceneObject.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/Base.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOAVector3.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOAVector.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/defs.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/utils.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOABase.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOAMatrix33.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOAMatrix.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOAQuaternion.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOAVector4.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOAMatrix66.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOAEuler.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOAVector3.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOAMatrix33.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOASpatialVector.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/SOA/SOAVector6.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/Light.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/SceneObject.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/TopoGeometry.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/LineString.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/Color.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/TextLabel.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/ParticleSystem.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/SceneFrame.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/PartGeometry.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/DScene/Scene.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/Dshell++Scripts/DebugLogSource.h",
                "/home/dlab2/repo/PKGBUILDS/ROAMSDshellPkg/ROAMSDshellPkg-Hourly-FC17/include/Dshell++Scripts/DebugLogVerbosity.h",
                "DScene_swigwrap_Py.h",
            ],
            make_build_system.parse_dependency_file("example.d"),
        )

    def test_parse_dependency_file_with_bad_file(self):
        self.assertEqual([], make_build_system.parse_dependency_file("bad_example.d"))

    def test_parse_dependency_file_with_fake_file(self):
        self.assertEqual([], make_build_system.parse_dependency_file("fake.d"))

    def test_parse_dependency_file_with_non_existent_file(self):
        self.assertEqual([], make_build_system.parse_dependency_file("non_existent.d"))

    def test_extract_module_dependencies(self):
        test_directory = os.path.abspath(os.path.dirname(__file__))

        self.assertEqual(
            {
                "FakeModuleB": {"Foo.h", "Foo2.h"},
                "FakeModuleC": {"Bizz.h", "Bizz2.h"},
            },
            make_build_system.extract_module_dependencies(
                dependency_paths=[
                    test_directory
                    + "/extract_test_data/my_release_directory/Module-Releases/FakeModuleB/FakeModuleB-R1-00a/Foo.h",
                    test_directory
                    + "/extract_test_data/my_release_directory/Module-Releases/FakeModuleB/FakeModuleB-R1-00a/Foo2.h",
                    test_directory + "/extract_test_data/fake_sandbox/src/FakeModuleA/Bar.h",
                    test_directory + "/extract_test_data/fake_sandbox/src/FakeModuleC/Bizz.h",
                    test_directory + "/extract_test_data/fake_sandbox/src/FakeModuleC/Bizz2.h",
                    "Local.h",
                ],
                module_name="FakeModuleA",
                sandbox_directory="extract_test_data/fake_sandbox",
                release_directory="extract_test_data/my_release_directory",
            ),
        )

    def test_find_module_dependencies(self):
        sandbox_directory = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "extract_test_data/fake_sandbox",
        )

        # Fill in a dependency file with absolute paths.
        with open(os.path.join(sandbox_directory, "src/FakeModuleA/x86/blah.d"), "w") as output_file:
            output_file.write(
                r"""
x86/DScene_swigwrap_Py.d x86/DScene_swigwrap_Py.o: DScene_swigwrap_Py.cc \
 {sandbox}/include/FakeModuleB/Foo.h \
 {sandbox}/include/FakeModuleB/Foo2.h \
 {sandbox}/include/FakeModuleC/Bizz.h \
 ../FakeModuleC/Bizz2.h""".format(
                    sandbox=sandbox_directory
                )
            )

        self.assertEqual(
            {
                "FakeModuleB": {"Foo.h", "Foo2.h"},
                "FakeModuleC": {"Bizz.h", "Bizz2.h"},
            },
            make_build_system.find_module_dependencies(
                module_name="FakeModuleA",
                sandbox_directory=sandbox_directory,
                release_directory="extract_test_data/my_release_directory",
            ),
        )

    def test_build_dependencies(self):
        sandbox_directory = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "extract_test_data/fake_sandbox",
        )

        # Fill in a dependency file with absolute paths.
        with open(os.path.join(sandbox_directory, "src/FakeModuleA/x86/blah.d"), "w") as output_file:
            output_file.write(
                r"""
x86/DScene_swigwrap_Py.d x86/DScene_swigwrap_Py.o: DScene_swigwrap_Py.cc \
 {sandbox}/include/FakeModuleB/Foo.h \
 {sandbox}/include/FakeModuleB/Foo2.h \
 {sandbox}/include/FakeModuleC/Bizz.h \
 {sandbox}/include/FakeModuleC/Bizz2.h""".format(
                    sandbox=sandbox_directory
                )
            )

        self.assertEqual(
            {
                "FakeModuleB": {"Foo.h", "Foo2.h"},
                "FakeModuleC": {"Bizz.h", "Bizz2.h"},
            },
            self.__build_system.build_dependencies(
                module_path=os.path.join(sandbox_directory, "src/FakeModuleA"),
                release_directory="extract_test_data/my_release_directory",
            ),
        )

    def test_full_split(self):
        self.assertEqual(("foo", "bar", "zip"), make_build_system.full_split("foo/bar/zip"))

        self.assertEqual(
            ("/", "foo", "bar", "zip"),
            make_build_system.full_split("/foo/bar/zip"),
        )

    def test_test_build_server(self):
        self.assertTrue(self.__build_system.check_build_server(sandbox_directory="FakeSandbox"))

    def __check_file(self, module_names, filename, extra=""):
        self.assertTrue(os.path.exists(filename))
        with open(filename) as f:
            self.assertEqual(" ".join(module_names) + extra + "\n", f.read())
        os.remove(filename)


@contextlib.contextmanager
def temporary_directory_context():
    """Return a temporary directory in a context."""
    import shutil
    import tempfile

    temporary_directory = tempfile.mkdtemp(dir=".")
    try:
        yield temporary_directory
    finally:
        shutil.rmtree(temporary_directory)


def find_file_base_names(path):
    """Return list of all files in path (recursively)."""
    for root, directories, filenames in os.walk(path):
        for f in filenames:
            yield f


if __name__ == "__main__":
    unittest.main()
