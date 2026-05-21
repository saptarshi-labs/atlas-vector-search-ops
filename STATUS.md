# Project Status — atlas-vector-search-ops

Last updated: 2026-05-21
Current position: Step 1 complete, Step 2 next.

## Completed

Step 1.1 — Azure Free Trial subscription created.

Step 1.2 — Terraform, Azure CLI, Git, VS Code installed on laptop via winget. Git configured with outlook.com email. VS Code extensions: hashicorp.terraform, ms-vscode-remote.remote-ssh.

Step 1.3 — GitHub repo `atlas-vector-search-ops` created. PAT generated with `repo` scope.

Step 1.4 — Repo cloned to `E:\projects\atlas-vector-search-ops`. Subfolders created (`infra`, `scripts`, `index_definitions`, `queries`, `runbooks`). Committed `.gitignore`, `README.md`, `.env.example`, `requirements.txt`, `STATUS.md`.

Step 1.5 — `az login` complete, default subscription set to `Azure subscription 1`.

Step 1.6 — Terraform configuration written (`main.tf`, `variables.tf`, `outputs.tf`, `terraform.tfvars`). VM provisioned in southindia on `Standard_B2s_v2` after a capacity restriction on `Standard_B1s`. 8 Azure resources created.

Step 1.7 — SSH from laptop to VM working. NSG rule updated after an ISP IP change.

Step 1.8 — Python 3, pip, venv, mongosh, and Atlas CLI installed on the VM.

Step 1.9 — SSH key generated on the VM and registered with GitHub. `~/.ssh/config` added so the non-default-named key is used. Repo cloned to `~/projects/atlas-vector-search-ops` on the VM.

Step 1.10 — Two-machine git workflow verified: laptop and VM both in sync with GitHub.

Step 2.1 — Atlas M0 cluster `vector-search-demo` created on AWS Mumbai (done early during account setup).

## Pending

Step 2.2 — Atlas network access, database user `vectordemo`.

Step 2.3 — load `sample_mflix` (23,530 movies).

Step 2.4 — connection string into `.env` on VM.

Step 2.5 — verify mongosh from VM.

Step 2.6 — Atlas CLI auth on VM.

Step 3.1 — Python venv on VM with pymongo, openai, python-dotenv.

Step 3.2 — OpenAI API key into `.env` on VM.

Step 3.3 — write and run `generate_embeddings.py` against 500 movie plots.

Step 3.4 — verify embeddings in mongosh.

Step 3.5 — commit script.

Step 4.1 — write `vector_index.json`.

Step 4.2 — create vector index via Atlas CLI.

Step 4.3 — first `$vectorSearch` query.

Step 4.4 — filtered vector query.

Step 4.5 — commit.

Step 5.1 — write `text_index.json`.

Step 5.2 — create text index.

Step 5.3 — hybrid query combining `$vectorSearch` and `$search`.

Step 5.4 — performance experiments (`numCandidates`, filter overhead).

Step 5.5 — commit.

Step 6.1–6.6 — README expansion, runbooks (polish incident notes into RCAs, index/embedding/cross-machine workflow), pin repo on profile.

Cleanup — `terraform destroy` before the Azure free credit window closes.

## Incidents logged

Raw notes in `runbooks/_incident-notes.md` (to be polished into RCAs in Step 6):
- Incident 01 — Azure SKU capacity restriction (B1s unavailable, switched to B2s_v2 in southindia).
- Incident 02 — SSH blocked after ISP IP change (NSG /32 rule update).
- Incident 03 — SSH key not offered to GitHub (non-default key name, fixed with `~/.ssh/config`).
