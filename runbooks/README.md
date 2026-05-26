# Runbooks

Incident write-ups (RCAs) for problems hit while building this project.
Each one follows the same format: Issue, Root Cause, Troubleshooting
Steps, Resolution, Prevention. These are real incidents that came up
during setup, not hypothetical examples.

## Incidents

- [01 - Terraform apply failed, VM SKU not available](01-azure-sku-capacity-restriction.md)
  A Free Trial subscription could not get the requested burstable VM
  size in the chosen Azure region. Fixed by switching region and size.

- [02 - SSH to the VM stopped working after the ISP changed my IP](02-ssh-blocked-after-ip-change.md)
  The home ISP rotated the laptop's public IP, and the NSG rule still
  allowed only the old IP, so SSH timed out. Fixed by updating the
  allowed IP in Terraform.

- [03 - Git over SSH from the VM failed with "Permission denied (publickey)"](03-ssh-key-not-offered-to-github.md)
  The SSH key had a non-default name and was not auto-discovered by the
  SSH client. Fixed by adding a ~/.ssh/config entry.
