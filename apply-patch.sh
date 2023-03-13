#!/bin/bash
#
# Applies or undos a patch to a `django-reversion` migration file enabling compatibility with
# ledger user fields by changing foreign key `user` to integer field `user_id` in reversion.
# Usage: apply-patch.sh 0001_squashed_0004_auto_20160611_1202[.undo].patch
#
# Patch files are created with the diff tool, e.g.:
# diff -u 0001_squashed_0004_auto_20160611_1202.my-ledger-edits.py 0001_squashed_0004_auto_20160611_1202.py > ...
# Respectively, to create a file to undo the patch:
# diff -u 0001_squashed_0004_auto_20160611_1202.py 0001_squashed_0004_auto_20160611_1202.my-ledger-edits.py > ...
#
# Example:
# $ apply-patch.sh 0001_squashed_0004_auto_20160611_1202.patch
# $ python manage.py migrate
# $ python manage.py createinitialrevisions
# $ apply-patch.sh 0001_squashed_0004_auto_20160611_1202.undo.patch

# The migration file to patch
if [ "$(poetry env info -p)" ]; then
    target_file=.venv/lib/python3.8/site-packages/reversion/migrations/0001_squashed_0004_auto_20160611_1202.py
else
    target_file=/usr/local/lib/python3.8/site-packages/reversion/migrations/0001_squashed_0004_auto_20160611_1202.py
fi

if [ -z "$1" ]
    then
        echo "Run: $0 0001_squashed_0004_auto_20160611_1202[.undo].patch"
        exit 1
    else
        # The patch to apply to `target_file`
        patch_file=$1
fi

if [ ! -f "$patch_file" ]; then
    echo "$patch_file does not exist."
    exit 1
fi
if [ ! -f "$target_file" ]; then
    echo "$target_file does not exist."
    exit 1
fi

echo "Applying patch $patch_file to $target_file."
patch "$target_file"  < "$patch_file" && status=$?

exit "$status"
