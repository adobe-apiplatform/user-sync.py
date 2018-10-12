``````````# user-sync.py: User Sync Tool Test Framework from Adobe

The User Sync Tool Test Framework is a command-line tool that automates the testing of the user-sync tool. It does this
by recording the network activity and output of the User Sync Tool during a live run of the tool, and can be
subsequently run using the recorded data to ensure the tool consistently functions as expected. The goal of the User
Sync Tool Test Framework is to ensure that the tool maintains it's existing expected operating behaviour as it
undergoes development, or is expanded to new platforms.

This application is open source, maintained by Adobe, and distributed under the terms of the OSI-approved MIT license.
See the LICENSE file for details.

Copyright (c) 2016-2017 Adobe Inc.

# Requirements

* Python 2.7+
* user-sync r2.1rc1 or higher
* If running on Windows, a 64 bit version of Windows is required.

## Build Instructions

Requirements:

* Python 2.7+
* If building on Debian - `python-dev libssl-dev libffi-dev`
* GNU Make

To build, run `make pex` from the command line in the /test_framework under the main repo directory.

## Build Instructions for local execution and debugging on Windows

Builds and execution are setup for 64 bit windows versions.

To set up PyCharm for debugging,
1. Make sure you are using 64 bit python interpreter.  File Settings Project Interpreter
2. Make sure interprter isn't overridden in run configuration
3. Set up a run configuration based on Python that references the user_sync_test\app.py file as the script, and has the command line parameters you want to test with (e.g. -c test-set-config.yml).

# Basic Usage

The test framework can basically be run in either live or test mode.

In live mode, when the user-sync tool is run, the tool communicates through the framework to the live server. All requests, responses and outputs are recorded by the framework. When the user-sync tool completes execution, the framework does not test execution success or failure, the user must review the recorded data to ensure the recordings and output is correct, as this recorded data is used to ensure a subsequent non-live run of the user-sync tool responds identically.

In test mode, user-sync tool requests are fulfilled using the data recorded during the live run, and the resulting output is compared against the output generated in the live run. The test is considered a success if the output matches the output from the live run.

When comparing recorded run output against live mode output, the content must be identical except where there are timestamps.

TODO: the user-sync path in the arguments line may be different except for the executable name, need to add support for matching lines with paths that may be different when run on another environment where the framework might be placed in a different path.

## User Sync Test command line

| Parameters&nbsp;and&nbsp;argument&nbsp;specifications | Description |
|------------------------------|------------------|
| `-h`<br />`--help` | Show this help message and exit. |
| `-v`<br />`--version` | Show program's version number and exit. |
| `-c` _filename_ | The complete path to the main test suite configuration file, absolute or relative to the working folder. Default filename is "test-set-config.yml". The user may also specify -g or -t to filter the tests in which to run. If neither the -g or -t parameters are given, all the tests in the suite are run. |
| `-g` _test_group_name_ | (Optional)The name of the test group to run. The name of the test group is basically the name of the folder that the group is in. The folder must contain the test-group-config.yml configuration file, in order for user-sync-test to recognize it as a test group. If the test name (-t) parameter is also provided, the testing is isolated further to the single test. Otherwise, all the tests under this test group is run.
| `-t` _test_name_ | (Optional)The name of the test to run. The name of the test is defined as the name of the folder in which the test is in. If the -t argument is given, then the test group (-g) must also be specified.|
| `-l` | (Optional) Starts the test framework in live mode, which will record requests, responses, and output. If not set, the framework will run the user-sync tool in test mode, which runs the tests using the recorded data to respond to the tool's umapi requests. In test mode, the output text file will be compared against the live output file, to assert that the tool gives the same output as when run live. |

## Verification

Verification only occurs in test mode. When the tool is in live mode, the user must review the recorded data to confirm that the data is correct, and can be used to assert that the test mode results can be compared against it.

There are three main points of verification:

The first is the comparison of the request JSON output. Both the JSON output from the recorded live requests and the test requests are deep sorted separately, then compareed to ensure they match exactly (except for specfic paths, such as the actionID node).

Next, the user-sync command line output is compared. Markers are placed in the output, by running user-sync in --test-framework mode. The markers are used to indicate output that is platform dependent, and exempt from the output matching process. Content in the markers are cleared and the output is sorted, then matched. The sorting is used to address the possiblity that different platforms may process actions in a different order. (TODO: currently JSON's output from user-sync are not sorted, need to add support for sorting this in --test-framework mode.)

Finally, output defined in the configuration file is compared in the same manner as the command line output. The output files are copied from the configuration output path (ie. specified in user-sync-config.yml/logging/file_log_directory) to the test's output folder (see Explaination of user-sync-test configuration file options below for more details).

## Examples

To run the entire test set, navigate to the test_framework/dist folder and enter the following command:

`./user-sync-test -c ../tests/test-set-config.yml`

To run a group of tests, specify it using the -g argument:

`./user-sync-test -c ../tests/test-set-config.yml -g "01 - config"`

To run a single test, specify it using both the -g and the -t arguments:

`./user-sync-test -c ../tests/test-set-config.yml -g "01 - config" -t "01 - update single user info"`

To run a single test in live mode, use the -l argument:

`./user-sync-test -c ../tests/test-set-config.yml -g "01 - config" -t "01 - Default config file" -l`

# Configuration

The basic configuration structure of the test framework consists of a test set configuration file at the root of the test set folder, typically test-set/test-set-config.yml, and a collection of folders under the test set folder, each containing their own test-config.yml, and configuration files.

See the `tests` directory for sample configuration files, and descriptions of the possible configuration options.

user-sync configuration files used in all tests:
tests/config-common

Explaination of user-sync-test configuration file options:
tests/test-suite-config.yml
tests/01 - config/test-group-config.yml
tests/01 - config/01 - Default config file/test-config.yml
