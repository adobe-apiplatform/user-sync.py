# User Sync Tool Documentation

This documentation is built with [Hugo](https://gohugo.io/). To build the site
for local development:

```
$ hugo serve -D
```

This watches all files in the `content` directory and incrementally builds the
site when changes are detected. When working with non-English languages, this
can sometimes render pages improperly or crash the server. If that happens, kill
the server if it's still running (`ctrl+c`), start it again and refresh the
page.

**NOTE:** The root documentation branch, `user-guide`, does not share commit
history with `v2` or any other source code branches. We recommend cloning this
branch to a separate directory. Switching between `user-guide`-derived branches
and `v2`-derived branches in the same workspace may have undesirable side effects.

To clone `user-guide` to a separate directory:

```
$ git clone -b user-guide https://github.com/adobe-apiplatform/user-sync.py.git user-sync.py-docs
```

The theme is installed as a submodule, so after cloning, update it:

```
$ git submodule update --init --recursive
```
