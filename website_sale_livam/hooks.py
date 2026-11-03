def post_init_hook(env):
    """Create the LiVaM tenant step for already existing websites."""
    step_model = env["website.checkout.step"]
    generic = step_model.search(
        [("website_id", "=", False), ("step_href", "=", "/shop/livam_tenant")],
        limit=1,
    )
    if not generic:
        return
    for website in env["website"].search([]):
        if not step_model.search_count(
            [
                ("website_id", "=", website.id),
                ("step_href", "=", "/shop/livam_tenant"),
            ]
        ):
            generic.copy({"website_id": website.id, "is_published": True})

