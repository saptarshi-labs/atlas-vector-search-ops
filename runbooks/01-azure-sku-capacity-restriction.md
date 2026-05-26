# Incident 01: Terraform apply failed, VM SKU not available

## Issue

`terraform apply` failed while creating the VM. 7 of the 8 resources were created fine (resource group, vnet, subnet, public IP, NSG, NIC, NSG-NIC association). Only the VM failed, with this error:

```
SkuNotAvailable ... The requested VM size 'Standard_B1s' is currently not
available in location 'CentralIndia' ... Capacity Restrictions ...
unexpected status 409 (409 Conflict)
```

## Root Cause

Azure Free Trial subscriptions have restricted access to burstable (B-series) VM sizes in the capacity-constrained Indian regions. `centralindia` had no B1s/B1ms capacity available for a Free Trial account. The Terraform config was correct. This was an Azure-side capacity restriction tied to the subscription type.

## Troubleshooting Steps

1. First assumed the size name in tfvars was wrong. Confirmed it wasn't. `Standard_B1s` is a valid size. The error means "not available here", not "invalid size".

2. Checked a neighbouring size in the same region:

   ```
   az vm list-skus --location centralindia --size Standard_B1ms
   ```

   Returned empty, so B1ms was also unavailable in centralindia.

3. Checked other regions for B1/B2 sizes:

   ```
   az vm list-skus --location southindia --size Standard_B2s
   ```

   Returned `Standard_B2s_v2` with no restrictions.

## Resolution

Updated `terraform.tfvars`: set `location` to `southindia` and `vm_size` to `Standard_B2s_v2`. Ran `terraform destroy` to clear the 7 half-created resources, then `terraform apply` again. All 8 resources created.

## Prevention

Check SKU availability before setting region/size in tfvars, using `az vm list-skus --location <region> --size <size>`. With a Free Trial account, expect B-series availability to be patchy across regions.
