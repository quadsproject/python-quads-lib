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
