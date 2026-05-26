# Incident 03: Git over SSH from the VM failed with "Permission denied (publickey)"

## Issue

Testing the SSH connection to GitHub from the VM failed:

```
ssh -T git@github.com
Permission denied (publickey).
```

This blocked cloning and pushing to the repo from the VM.

## Root Cause

The SSH key on the VM has a non-default name (`github_key`). The SSH client only auto-discovers keys with default names (`id_rsa`, `id_ed25519`, and so on). With no `~/.ssh/config` entry and no `-i` flag on the command, SSH had no key to present to GitHub. It offered nothing, so GitHub rejected the connection with "Permission denied (publickey)".

## Troubleshooting Steps

1. Checked the key files were present:

   ```
   ls -la ~/.ssh/
   ```

   Both `github_key` and `github_key.pub` were there, with correct permissions (private key 600).

2. Confirmed the public key was registered on GitHub (Settings > SSH and GPG keys, entry `vector-search-vm`).

3. Compared fingerprints to be sure the registered key matched the local key:

   ```
   ssh-keygen -lf ~/.ssh/github_key.pub
   ```

   The fingerprint matched the one shown on GitHub. So the correct key was registered, the key itself was not the problem.

4. That ruled out a missing or wrong key, and pointed at the client not actually presenting the key. The key has a non-default name, and there was no config telling SSH to use it.

## Resolution

Created `~/.ssh/config` with an entry for GitHub:

```
Host github.com
    IdentityFile ~/.ssh/github_key
    IdentitiesOnly yes
```

Set permissions on the config file:

```
chmod 600 ~/.ssh/config
```

After this, `ssh -T git@github.com` authenticated successfully and Git operations from the VM worked.

## Prevention

When generating an SSH key with a non-default name, create the matching `~/.ssh/config` entry in the same step. The key name on its own is not enough, the client needs to be told which key to use for which host.
