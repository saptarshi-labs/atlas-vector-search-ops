# Incident 02: SSH to the VM stopped working after the ISP changed my IP

## Issue

SSH to the VM stopped working. The connection timed out instead of being refused:

```
ssh: connect to host <vm-ip> port 22: Connection timed out
```

A timeout (not "connection refused") means the packets never reached the host at all, which points at a firewall dropping them rather than the VM rejecting them.

## Root Cause

The home ISP rotated the laptop's public IP to a new address. The NSG rule that allows SSH was scoped to the old IP as a /32, so once the IP changed, SSH packets from the new IP were dropped by the firewall.

## Troubleshooting Steps

1. Checked the current public IP of the laptop:

   ```
   curl.exe -4 ifconfig.me
   ```

   Returned a different IP than expected.

2. Checked what source IP the NSG rule actually allowed:

   ```
   az network nsg rule show ...
   ```

   The `AllowSSHFromMyIP` rule still had the old IP as its source /32.

3. Confirmed the VM itself was running, using `az vm get-instance-view`, so the VM was not the problem.

4. Clear mismatch: current laptop IP did not match the IP allowed by the NSG.

## Resolution

Updated `my_ip` in `terraform.tfvars` to the new IP and ran `terraform apply`. One resource changed in place (the NSG rule), took about 10 seconds. SSH worked again right after.

## Prevention

A /32 source is tight and breaks every time the ISP rotates the IP. Options: widen the allowed range for the project (for example a /16), or use a dynamic-DNS based allowlist so the rule follows the IP. For now the fix is just to re-run `curl.exe -4 ifconfig.me` and `terraform apply` whenever SSH starts timing out.

Note: real public IP addresses and the ISP name are intentionally left out of this document, since the repository is public.
