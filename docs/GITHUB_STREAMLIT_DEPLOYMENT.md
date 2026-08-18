# GitHub and Streamlit Community Cloud deployment

## Why the original push was rejected

The former `data/project_msr_database.json` file was approximately 184 MB. GitHub rejects individual files above 100 MB before accepting a push.

Version 4.3.1 preserves the complete database as ordinary, readable JSON files:

- one core JSON file;
- five task JSON files;
- one manifest JSON file.

The largest file is approximately 44 MB. Git LFS, gzip, binary encoding, and remote downloads are not required.

## Replace a rejected first commit

The remote repository is empty because the push was rejected. The safest procedure is to replace the local unpushed history with a clean commit that contains the v4.3.1 package.

From the repository root:

```bash
# Preserve any local-only configuration first.
cp .streamlit/secrets.toml /tmp/project_msr_secrets.toml 2>/dev/null || true

# Remove the rejected local history while keeping the current working files.
git checkout --orphan clean-main
git rm -rf --cached .
git add .
git commit -m "Release Project-MSR Planner v4.3.1"
git branch -M main
git push -u origin main

# Restore local secrets if needed; this file remains ignored by Git.
cp /tmp/project_msr_secrets.toml .streamlit/secrets.toml 2>/dev/null || true
```

Before committing, confirm the oversized monolithic file is not tracked:

```bash
git ls-files data/project_msr_database.json
```

The command should print nothing.

Confirm that no tracked file approaches the GitHub limit:

```bash
find . -type f -not -path './.git/*' -size +90M -print
```

The command should also print nothing.

## Alternative when preserving local commit history matters

If the oversized file exists in multiple local commits and those commits must be retained, remove it from all local history with `git filter-repo`, then commit the JSON shards:

```bash
python -m pip install git-filter-repo
git filter-repo --path data/project_msr_database.json --invert-paths --force
git add data/project_msr_database.manifest.json \
        data/project_msr_database.core.json \
        data/project_msr_database.tasks.*.json \
        .gitignore src/data_loader.py src/database_sharding.py
git commit -m "Store complete database as GitHub-safe JSON shards"
git push -u origin main
```

For an empty remote, the orphan-branch procedure is simpler and less error-prone.

## Streamlit Community Cloud

1. Push the unpacked v4.3.1 repository to GitHub.
2. In Streamlit Community Cloud, create or update the application using `app.py` as the entry point.
3. Add the `[auth]` values already configured for the deployment, or generate a new hash with `python scripts/set_password.py` and copy it to the application's Secrets settings.
4. Reboot the application after saving secrets.

At startup, the application reads `data/project_msr_database.manifest.json`, verifies each JSON part, reconstructs all database collections, and exposes the same planner content as the former monolithic file.

## Local verification

```bash
python scripts/validate_database.py
python scripts/reconstruct_database.py --output /tmp/project_msr_database.full.json
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
streamlit run app.py
```

The reconstruction utility checks the manifest's canonical semantic checksum before writing the large local file.


## Implementation-tab deployment hotfix

Version 4.3.1 makes the database cache content-sensitive. After pushing the release, reboot the Streamlit application once. If an existing browser session still shows zero implementation records, open the Database control in the sidebar and select **Reload bundled database**. The expected bundled values are 11 playbooks, 25 chemistry experiments, 6 fuel phases, and implementation plans on all active tasks.
