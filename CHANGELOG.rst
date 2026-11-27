
Changelog
=========


0.1.20 (2026-11-27)
-------------------

* Raise ``APIUnauthorized`` on 401 responses in ``_make_request`` instead of
  returning the JSON body as a dict, matching the 400/403/404/500 behavior.
  ``register()`` posts directly like ``login()`` so its 401 validation
  responses (e.g. "User already exists") stay dicts, and ``__exit__`` no
  longer raises when ``logout()`` gets a 401 from an expired token.


0.1.19 (2026-11-25)
-------------------

* Raise ``APIForbidden`` on 403 responses in ``_make_request`` instead of
  returning the JSON body as a dict, matching the 400/404/500 behavior.
  Callers iterating a 403 body no longer crash with
  ``'str' object has no attribute 'get'``.

0.1.18 (2026-10-11)
-------------------

* Document ``get_free_clouds`` as the canonical free-cloud API (server-side
  semantics: no active assignment, future-scheduled clouds excluded, spare
  pool excluded via server config) and pin its response contract, including
  the ``last_redefined`` reservation-lock field, in tests.

0.1.17 (2026-06-08)
-------------------

* Add ``APINotFound`` exception and 404 handling in ``_make_request``.

0.1.16 (2026-06-02)
-------------------

* Add support for QUADS server polling/status API.
* Add move status API methods: ``get_all_move_status``, ``get_move_status``,
  ``start_move_batch``, ``update_move_status``.
* Align with ``MoveStatus`` enum refactor and simplified ``MoveProgress`` DB
  structure on the server side.

0.0.0 (2025-01-07)
------------------

* First release on PyPI.
