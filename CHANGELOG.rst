
Changelog
=========

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
