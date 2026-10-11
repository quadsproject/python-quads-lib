=====
Usage
=====

To use the project:

.. code-block:: python

    from quads_lib import QuadsApi
    quads = QuadsApi(username, password, base_url)
    quads.login()
    hosts = quads.get_hosts()
    quads.logout()

Or using a context manager:

.. code-block:: python

    from quads_lib import QuadsApi
    with QuadsApi(username, password, base_url) as quads:
        hosts = quads.get_hosts()

TLS Certificate Verification
----------------------------

By default, TLS certificate verification is disabled (``verify=False``) for backward compatibility.
You can control certificate verification using the ``verify`` parameter:

.. code-block:: python

    # Disable verification (default)
    quads = QuadsApi(username, password, base_url, verify=False)

    # Enable verification with default CA bundle
    quads = QuadsApi(username, password, base_url, verify=True)

    # Use a custom CA bundle file
    quads = QuadsApi(username, password, base_url, verify="/path/to/ca-bundle.pem")

Tracking Move Status
--------------------

Query the 12-stage provisioning pipeline for active host moves:

.. code-block:: python

    with QuadsApi(username, password, base_url) as quads:
        # All active moves, optionally filtered by cloud or status
        moves = quads.get_all_move_status(cloud="cloud02")

        # Single host status
        progress = quads.get_move_status("host01.example.com")
        print(f"{progress['host']}: {progress['status']}")

Finding Free Clouds
-------------------

``get_free_clouds()`` is the canonical free-cloud detection API. It calls the
server's ``GET /clouds/free/`` and returns the raw JSON list, so the server
decides what "free" means instead of each client reimplementing schedule
logic. A cloud is free when it has no active assignment, which also excludes
clouds with future schedules, and the spare pool is excluded server-side via
the server's ``spare_pool_name`` config (no client-side cloud name to keep
in sync):

.. code-block:: python

    with QuadsApi(username, password, base_url) as quads:
        for cloud in quads.get_free_clouds():
            print(cloud["name"])

Each cloud dict carries ``last_redefined`` as an RFC 1123 GMT string, so a
client can render the same reservation-lock hint the quads server CLI shows.
The lock window itself (``cloud_reservation_lock`` hours) is server-side
config and is not exposed over the API, so keep it in client config:

.. code-block:: python

    from datetime import datetime, timedelta
    from email.utils import parsedate_to_datetime

    lock_hours = 48  # mirror the server's cloud_reservation_lock
    for cloud in quads.get_free_clouds():
        last_redefined = parsedate_to_datetime(cloud["last_redefined"])
        lock_release = last_redefined + timedelta(hours=lock_hours)
        if lock_release > datetime.now(tz=last_redefined.tzinfo):
            remaining = lock_release - datetime.now(tz=last_redefined.tzinfo)
            hours = remaining.total_seconds() // 3600
            minutes = (remaining.total_seconds() % 3600) // 60
            print(f"{cloud['name']} (reserved: {hours:.0f}hr {minutes:.0f}min remaining)")

Both snippets assume a live ``quads`` session, e.g. from the ``with`` block
above.

Older QUADS servers (before 2.1) do not expose ``/clouds/free/``; the call
then raises ``APINotFound``.
