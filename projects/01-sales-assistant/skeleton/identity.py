"""Pseudocode: identity and authorization for the tool layer.

Design goals
- The user authorizes once; no secrets are typed into chat or prompts.
- Tool servers only hold public keys and never store secrets.
- One access service is the single source of truth for permissions.
"""

def handle_tool_call(request):
    # 1. Service identity: each entry point (messenger agent, analyst console)
    #    has its own revocable bearer credential.
    entry = verify_service_bearer(request.headers["authorization"])

    # 2. User identity: the messenger platform signs a token for the user.
    #    Verify signature, audience and expiry with the platform's public key.
    claims = verify_signed_token(request.headers["x-user-identity"],
                                 public_key=PLATFORM_PUBLIC_KEY,
                                 audience=OUR_TOOL_AUDIENCE)
    if claims is None:
        return refuse("Could not verify who you are. Please reopen the assistant.")

    # 3. Map platform user id -> our subject + territories via the access service.
    caller = access_service.lookup(claims.user_id)
    if caller is None:
        return refuse("You are not on the access list yet.")  # never guess

    # 4. Run the tool with the caller; tools apply the territory gate themselves
    #    (details in territory, counts outside).
    return run_tool(request.tool, request.args, caller, entry=entry)
