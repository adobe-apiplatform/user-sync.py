##Make a test run to check configuration

[Previous Section](before_you_start.md) | [Back to Contents](Contents.md) |  [Next Section](monitoring.md)

To invoke user sync:

Windows:      **python user-sync.pex ….**

Unix, OSX:     **./user-sync ….**

Try to run at all:

	./user-sync –v              report version of user sync tool
	./user-sync –h             help: list available command line options
	
	./user-sync -t --users all --process-groups      run in test mode for users and groups 
	
	./user-sync -t --users all                       run in test mode for users only 

This test run should connect to the directory and read all users, connect to Adobe and read all users, setup creation or addition of new users and setup group memberships (first line only)

This may run for a really long time.  **Need simpler test.**


	user-sync –v            Report version
	user-sync –h            Help on command line args

![img](images/test_run_screen.png)


[Previous Section](before_you_start.md) | [Back to Contents](Contents.md) |  [Next Section](monitoring.md)

