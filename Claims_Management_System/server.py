from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Union
import uuid

app = FastAPI()

# In-memory storage for entities
policyholders = {}
policies = {}
claims = {}

# Auto-incrementing IDs for policies and claims
policy_id_counter = 1
claim_id_counter = 1

# Models
class Policyholder(BaseModel):
    name: str
    email: str

class Policy(BaseModel):
    policyholder_id: int
    coverage: float
    status: str  # active, inactive

class Claim(BaseModel):
    policyholder_id: int
    policy_id: int
    amount: float
    status: str  # pending, approved, rejected, pending_review


def generate_policyholder_id() -> int:
    """
    Generates a unique 31-bit integer ID for a policyholder.
    
    Returns:
        int: A unique policyholder ID.
    """
    while True:
        new_id = uuid.uuid4().int & ((1 << 31) - 1)
        if new_id not in policyholders:
            policyholders[new_id] = None 
            return new_id

@app.post("/policyholder/")
def create_policyholder(policyholder: Policyholder):
    """
    Creates a new policyholder and returns the generated ID along with details.
    """
    policyholder_id = generate_policyholder_id()  # Generate a unique ID
    # Save the policyholder with the generated ID
    policyholders[policyholder_id] = policyholder
    # Return both the ID and policyholder details
    return {"id": policyholder_id, **policyholder.dict()}

@app.post("/policy/", response_model=Policy)
def create_policy(policy: Policy):
    """
    Creates a new policy and returns the policy details including the ID.
    """
    global policy_id_counter

    # Ensure the policyholder exists
    if policy.policyholder_id not in policyholders:
        raise HTTPException(status_code=404, detail="Policyholder not found.")
    
    policy_id = policy_id_counter
    policy_id_counter += 1
    policies[policy.policyholder_id] = policies.get(policy.policyholder_id, {})
    policies[policy.policyholder_id][policy_id] = policy
    # Returning policy details and the generated id
    return {"id": policy_id, **policy.dict()}

@app.post("/claim/", response_model=Claim)
def create_claim(claim: Claim):
    """
    Creates a new claim and returns the generated claim ID.
    """
    global claim_id_counter
    if claim.policyholder_id not in policyholders or claim.policyholder_id not in policies or claim.policy_id not in policies[claim.policyholder_id]:
        raise HTTPException(status_code=404, detail="Policyholder or Policy not found.")
    policy = policies[claim.policyholder_id][claim.policy_id]
    total_claims = sum(
        c.amount for c in claims.get(claim.policyholder_id, {}).get(claim.policy_id, {}).values()
        if c.status != "rejected"
    )
    if total_claims + claim.amount > policy.coverage:
        raise HTTPException(status_code=400, detail="Claim exceeds available coverage.")
    claim_id = claim_id_counter
    claim_id_counter += 1
    claims.setdefault(claim.policyholder_id, {}).setdefault(claim.policy_id, {})[claim_id] = claim
    if claim.amount > 10000:
        claim.status = "pending_review"
    else:
        claim.status = "flagged"
    return {"id": claim_id, **claim.dict()}


@app.get("/policyholder/{policyholder_id}")
def get_policyholder(policyholder_id: int):
    """
    Retrieves a policyholder by ID.
    """
    if policyholder_id not in policyholders:
        raise HTTPException(status_code=404, detail="Policyholder not found.")
    return policyholders[policyholder_id]

@app.get("/policyholder/{policyholder_id}/claims")
def get_claims_by_policyholder(policyholder_id: int):
    if policyholder_id not in claims:
        raise HTTPException(status_code=404, detail="Claims not found for this policyholder.")
    
    # Collecting claims per policyholder and policy
    filtered_claims = {}
    for policy_id, policy_claims in claims[policyholder_id].items():
        for claim_id, claim in policy_claims.items():
            filtered_claims[claim_id] = claim
    
    return filtered_claims



@app.get("/policyholder/{policyholder_id}/policies")
def get_policies_by_policyholder(policyholder_id: int):
    """
    Retrieves all policies for a given policyholder by their ID.
    """
    if policyholder_id not in policyholders:
        raise HTTPException(status_code=404, detail="Policyholder not found.")
    
    # Retrieve all policies for this policyholder
    policies_for_policyholder = policies.get(policyholder_id, {})
    
    return {
        "policyholder_id": policyholder_id,
        "policies": policies_for_policyholder
    }


@app.put("/policy/{policyholder_id}/{policy_id}")
def update_policy(policyholder_id: int, policy_id: int, policy: Policy):
    """
    Updates a specific policy by policyholder ID and policy ID.
    """
    if policyholder_id not in policies or policy_id not in policies[policyholder_id]:
        raise HTTPException(status_code=404, detail="Policy not found.")
    
    policies[policyholder_id][policy_id] = policy
    return {"detail": "Policy updated successfully."}

@app.put("/claim/{policyholder_id}/{policy_id}/{claim_id}")
def update_claim(policyholder_id: int, policy_id: int, claim_id: int, claim: Claim):
    """
    Updates a specific claim by policyholder ID, policy ID, and claim ID.
    """
    if policyholder_id not in claims or policy_id not in claims[policyholder_id] or claim_id not in claims[policyholder_id][policy_id]:
        raise HTTPException(status_code=404, detail="Claim not found.")
    
    claims[policyholder_id][policy_id][claim_id] = claim
    return {"detail": "Claim updated successfully."}

@app.put("/policyholder/{policyholder_id}")
def update_policyholder(policyholder_id: int, policyholder: Policyholder):
    """
    Updates a specific policyholder by policyholder ID.
    """
    if policyholder_id not in policyholders:
        raise HTTPException(status_code=404, detail="Policyholder not found.")
    
    policyholders[policyholder_id] = policyholder
    return {"detail": "Policyholder updated successfully."}

@app.delete("/policyholder/{policyholder_id}")
def delete_policyholder(policyholder_id: int):
    """
    Deletes a specific policyholder by ID.
    """
    if policyholder_id not in policyholders:
        raise HTTPException(status_code=404, detail="Policyholder not found.")
    
    # Check if there are active policies
    if policyholder_id in policies and any(policy.status == "active" for policy in policies[policyholder_id].values()):
        raise HTTPException(status_code=400, detail="Cannot delete policyholder with active policies.")
    
    # Delete the policyholder and their policies, if any
    del policyholders[policyholder_id]
    
    # Delete policies only if the policyholder exists in policies
    if policyholder_id in policies:
        del policies[policyholder_id]  # Delete all policies for this policyholder
    
    return {"detail": f"Policyholder {policyholder_id} deleted successfully."}


@app.delete("/policy/{policyholder_id}/{policy_id}")
def delete_policy(policyholder_id: int, policy_id: int):
    """
    Deletes a specific policy by policyholder ID and policy ID.
    """
    if policyholder_id not in policies or policy_id not in policies[policyholder_id]:
        raise HTTPException(status_code=404, detail="Policy not found.")
    
    # Check if there are linked claims
    linked_claims = [claim for claim in claims.get(policyholder_id, {}).get(policy_id, {}).values()]
    if linked_claims:
        raise HTTPException(status_code=400, detail="Cannot delete policy with linked claims.")
    
    del policies[policyholder_id][policy_id]
    return {"detail": f"Policy {policy_id} for policyholder {policyholder_id} deleted successfully."}

@app.delete("/claim/{policyholder_id}/{policy_id}/{claim_id}")
def delete_claim(policyholder_id: int, policy_id: int, claim_id: int):
    """
    Deletes a specific claim by policyholder ID, policy ID, and claim ID.
    """
    if policyholder_id not in claims or policy_id not in claims[policyholder_id] or claim_id not in claims[policyholder_id][policy_id]:
        raise HTTPException(status_code=404, detail="Claim not found.")
    
    del claims[policyholder_id][policy_id][claim_id]
    return {"detail": f"Claim {claim_id} for policyholder {policyholder_id} and policy {policy_id} deleted successfully."}

@app.put("/claim/{policyholder_id}/{policy_id}/{claim_id}/status")
def change_claim_status(policyholder_id: int, policy_id: int, claim_id: int, status: str):
    """
    Changes the status of a specific claim.
    """
    if policyholder_id not in claims or policy_id not in claims[policyholder_id] or claim_id not in claims[policyholder_id][policy_id]:
        raise HTTPException(status_code=404, detail="Claim not found.")
    
    claims[policyholder_id][policy_id][claim_id].status = status
    return {"detail": f"Claim status updated to {status}."}

@app.get("/")
def health_check():
    """
    Health check endpoint to verify server status.
    """
    return {"status": "ok"}
