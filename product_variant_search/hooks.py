# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

BATCH_SIZE = 2000
POST_INIT_CAP = 20000  # max products to process in hook


def post_init_hook(env):
    Product = env["product.product"]
    processed = 0
    last_id = 0
    while processed < POST_INIT_CAP:
        recs = Product.search(
            [("id", ">", last_id)],
            order="id asc",
            limit=min(BATCH_SIZE, POST_INIT_CAP - processed),
        )
        if not recs:
            break
        recs.assign_search_name_all_langs()
        last_id = recs[-1].id
        processed += len(recs)
