## Decide how you will handle account deletion

- When accounts are disabled or deleted from the directory you often want the corresponding Adobe account removed, but:

  - Removing the Adobe account may delete assets, settings, etc. that are later needed

  - You can recover licenses from AdobeId accounts but the account belongs to the end user and cannot be deleted

- Choices available for handling Adobe account deletion via user sync:
  - Take no action.  Account cleanup must be handled manually.
  - Generate list of accounts to be deleted, but no action is taken.  The list can be edited and later used to drive account deletion.
  - Recover all licenses given by your org to the account, but leave it active. *
  - Recover all licenses and remove from your org, but leave account in existence.
  - Recover all licenses and delete the account. *

\* - feature coming late March, 2017

- Account deletion things to know
  - Removing the Adobe account may delete assets, settings, etc. that are later needed
  - You can only “delete” accounts if they are in a domain that your org owns.
  - You may have users in your org that are owned by other orgs.  This happens by way of requesting access to another domain owned by a different org.
    - You can recover licenses you granted such users
    - You can remove them from your org, but you cannot delete such accounts because they are owned by a different org.
    - If you try to delete such an account, it has the same effect as removing the user from your org

![orgs](images/decide_deletion_multi_org.png)
