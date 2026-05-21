# Incident notes — RAW

Scratch file. Polish into proper RCA files under runbooks/ during Step 6.
One bullet dump per incident. Keep exact error strings and commands.

---

## Incident 01 — Azure SKU capacity restriction

- Date: ~May 19-20, 2026
- Layer: cloud / capacity
- Symptom: `terraform apply` failed while creating the VM resource.
- Error text: `SkuNotAvailable ... The requested VM size 'Standard_B1s' is
  currently not available in location 'CentralIndia' ... Capacity Restrictions
  ... unexpected status 409 (409 Conflict)`.
- 7 of 8 resources created successfully before the failure (RG, VNet, subnet,
  public IP, NSG, NIC, NSG-NIC association). Only the VM failed.
- Diagnosis steps:
  - `az vm list-skus --location centralindia --size Standard_B1ms` -> empty
    (B1ms also unavailable in centralindia).
  - Checked southindia and westindia for B1s, B1ms, B2s.
  - `az vm list-skus --location southindia --size Standard_B2s` returned a row:
    `Standard_B2s_v2`, no restrictions.
- Root cause: Free Trial subscriptions have restricted access to burstable
  (B-series) SKUs in capacity-constrained Indian regions. Not a config error.
- Fix: changed `location` -> `southindia` and `vm_size` -> `Standard_B2s_v2`
  in terraform.tfvars. Ran `terraform destroy` (7 resources) then
  `terraform apply` fresh -> 8 resources created.
- Cost note: B2s_v2 ~$26/month, well within the $200 free credit.
- Prevention idea: query `az vm list-skus` for availability before writing
  region/size into tfvars.

---

## Incident 02 — SSH blocked after ISP IP change

- Date: ~May 21, 2026
- Layer: network / firewall
- Symptom: `ssh` to the VM failed with `Connection timed out` (timeout, not
  "connection refused" — packet never reached the host).
- Diagnosis steps:
  - `curl.exe -4 ifconfig.me` -> `122.171.22.251` (current laptop IP).
  - `az network nsg rule show ...` -> NSG `AllowSSHFromMyIP` source was
    `122.171.19.184/32` (the old IP).
  - VM confirmed running via `az vm get-instance-view`.
  - Clear mismatch: current IP != NSG allowed source.
- Root cause: home ISP (Jio) rotated the public IP from 122.171.19.184 to
  122.171.22.251. The NSG rule was scoped to the old /32, so SSH packets from
  the new IP were dropped by the firewall.
- Fix: updated `my_ip` in terraform.tfvars to the new IP, ran `terraform apply`
  -> 1 resource changed in place (NSG rule), ~10 seconds. SSH worked after.
- Prevention idea: /32 is tight but breaks on IP rotation; could widen to /16
  for the project, or use dynamic-DNS-based allowlisting.

---

## Incident 03 — SSH key not offered to GitHub

- Date: May 21, 2026
- Layer: SSH client config
- Symptom: `ssh -T git@github.com` from the VM returned
  `Permission denied (publickey)`.
- Diagnosis steps:
  - `ls -la ~/.ssh/` -> `github_key` and `github_key.pub` both present,
    correct permissions (private key 600).
  - Public key confirmed registered on GitHub (Settings > SSH keys, entry
    `vector-search-vm`).
  - `ssh-keygen -lf ~/.ssh/github_key.pub` fingerprint
    `SHA256:CXsavYk3h/SYA9/RnyMde3dsltHcVxa+uctPkNtnF5o` == fingerprint shown
    on GitHub. So the correct key IS registered.
- Root cause: the key file has a non-default name (`github_key`). The SSH
  client only auto-discovers default-named keys (`id_rsa`, `id_ed25519`, etc.).
  With no `~/.ssh/config` and no `-i` flag, SSH had no key to present — it
  offered nothing, and GitHub returned `Permission denied (publickey)`.
- Fix: created `~/.ssh/config` with:
  - `Host github.com`
  - `IdentityFile ~/.ssh/github_key`
  - `IdentitiesOnly yes`
  - `chmod 600 ~/.ssh/config`
  `ssh -T git@github.com` then authenticated successfully.
- Prevention idea: when generating a non-default-named key, create the
  matching `~/.ssh/config` entry in the same step.

---

## (add new incidents below as they occur)
