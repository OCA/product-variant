On installation, post_init_hook assigns search_name for up to 20,000 products (hard cap) to avoid
performance issues in huge DBs. Any remaining products must be processed by the “Assign product search name”
cron job. This cron is disabled by default, so an administrator should enable it when needed, then disable it
again once all products have search_name assigned.
