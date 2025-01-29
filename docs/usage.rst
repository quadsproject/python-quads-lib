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
