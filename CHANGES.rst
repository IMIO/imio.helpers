Changelog
=========

1.0.0rc4 (2024-07-08)
---------------------

- Added "empty" variables to handle empty indexes searches.
  [sgeulette]

1.0.0rc3 (2024-06-07)
---------------------

- Added `temp_disable_link` JS helper that will disable a link for 2 seconds
  and to avoid double clicks.
  [gbastien]

1.0.0rc2 (2024-04-10)
---------------------

- Added batching module.
  [sgeulette]
- Fixed the way JS function `submitFormHelperOnsuccessDefault` manages
  returned result when it is a file, now we have a correct `filename`.
  [gbastien]
- Added transmogrifier Expression and Condition classes to log expression
  compilation or interpretation errors.
  [sgeulette]
- Removed `content.safe_encode` as already defined in `imio.pyutils`.
  Import it from `imio.pyutils` in `imio.helpers.content` for temporary backward
  compatibility, to be removed.
  [gbastien]
- Overrided `@@folder_contents` to make it work with `DashboardCollection`.
  [gbastien]
- Monkeypatched `plone.app.querystring.registryreader.getVocabularyValues`
  to keep vocabulary order onloy for Plone4, behavior is correct in Plone5+.
  Manage every `HAS_PLONE_X` values.
  [gbastien]

1.0.0rc1 (2024-02-08)
---------------------

- Made compliant with Plone 4, Plone 5, Plone 6
  [boulch, laulaz, sgeulette]
- Require `pathlib2` in `setup.py`, backport `pathlib` for `py2.7`.
  [gbastien]
- Added `security.setup_app` to be used in run scripts.
  [sgeulette]
- Added `setup.load_xml_tool_only_from_package` to load only main tool xml file.
  [sgeulette]
- Added `setup.test_remove_gs_step` to remove a generic setup step.
  [sgeulette]
- Added `imio.helpers.YesNoForFacetedVocabulary`
  [sgeulette]
- Fixed `content.base_getattr` that was not returning the `default` if attribute
  not existing.
  [gbastien]

0.80 (2023-12-11)
-----------------

- Added parameter `with_user_id` to `content.get_user_fullname`, this will
  include `userid` in brackets in result like `Firstname Lastname (userid)`.
  [gbastien]
- Added parameter `userid` to `security.get_user_from_criteria`
  [sgeulette]

0.79 (2023-11-28)
-----------------

- Improved `security.get_user_from_criteria` to add email and description in ldap results.
  [sgeulette]
- Included Products.CMFCore permissions.zcml
  [sgeulette]

0.78 (2023-10-27)
-----------------

- Added `workflow.get_final_states` that will return a given WF final states.
  [gbastien]

0.77 (2023-10-19)
-----------------

- Added `xhtml.unescape_html` that will decode HTML entities of a HTML text.
  [gbastien]

0.76 (2023-09-28)
-----------------

- Added `transmogrifier.get_correct_id` to generate a unexisting id with numbered or lettered suffix.
  [sgeulette]
- Renamed `transmogrifier.correct_path` to `transmogrifier.get_correct_path`
  [sgeulette]

0.75 (2023-09-04)
-----------------

- Fixed `setup.load_type_from_package` when loading a Dexterity FTI because
  it fails to purge old values.
  Purging is disabled for `Dexterity FTI`, added new parameter `purge_actions=False`
  that will remove the actions for a `Dexterity FTI` so it is reloaded in correct order.
  [gbastien]
- Improved `transmogrifier.str_to_date` with min and max
  [sgeulette]
- Fixed `ValueError: 'value' is not in list` in `content.sort_on_vocab_order`
  when a value of given `p_values` does not exist in the given `p_vocab`.
  [gbastien]

0.74 (2023-08-24)
-----------------

- Fixed `cache.obj_modified` when checking annotations, take care that `_p_mtime`
  is not changed on `__annotations__` when a value changes in a stored annotation
  that is a `PersistentMapping`.
  Also removed parameter `asstring=False`, when `asdatetime=False`, returned
  value is float which is convenient to be used in a cachekey.
  [gbastien]
- Add `catalog` parameter on `content.uuidsToObjects`, `content.uuidsToObject`,
  `content.uuidsToCatalogBrains` and `uuidsToCatalogBrain` to allow query on
  other catalogs (e.g. uid_catalog)
  [mpeeters]


0.73 (2023-07-20)
-----------------

- Be more defensive in `content.get_user_fullname`, in some case, a userid
  is found in `mutable_properties` but there is no properties associated with it.
  [gbastien]
- Improved `transmogrifier.clean_value` giving a replacement value
  [sgeulette]

0.72 (2023-07-12)
-----------------

- In `submitFormHelperOnsuccessDefault` JS function, only manage `blob` if
  `content-type` is `application/xxx`.
  [gbastien]
- Added `content.sort_on_vocab_order` that will sort a list of `values`
  respecting a given `vocabulary` terms order. This relies on `sort_by_indexes`
  from `imio.pyutils` that is now a dependency.
  [gbastien]

0.71 (2023-07-07)
-----------------

- Modified `transmogrifier.relative_path` to add option to keep leading slash
  (True by default).
  [sgeulette]
- In `content.get_user_fullname`, if `fullname` not found at the end,
  finally fallback to `portal_membership.getMemberInfo`, this is sometimes
  necessary when using LDAP.
  [gbastien]
- Removed backward compatible imports for `get_state_infos`, `get_transitions`
  and `do_transitions` moved from `content` to `workflow`.
  [gbastien]

0.70 (2023-06-21)
-----------------

- Added `security.check_zope_admin` (moved from `Products.CPUtils`).
  [gbastien]
- Improved `transmogrifier.filter_keys`
  [sgeulette]
- Added `workflow.update_role_mappings_for` helper to update WF role mappings
  for a given object.
  [gbastien]

0.69 (2023-05-31)
-----------------

- Monkeypatch `CatalogTool._listAllowedRolesAndUsers` to add `ram.cache` decorator.
  [gbastien]

0.68 (2023-05-12)
-----------------

- Added `split_text` in transmogrifier module.
  [sgeulette]
- Added `workflow.get_leading_transitions` that will return every WF transitions
  leading to a given `state_id`.
  [gbastien]

0.67 (2023-03-29)
-----------------

- Added `clean_value`, `correct_path`, `filter_keys`, `get_obj_from_path` in transmogrifier module.
  [sgeulette]
- Added `key_val`, `pool_tuples`, `str_to_date` in transmogrifier module.
  [sgeulette]
- Renamed `text_int_to_bool` to `str_to_bool`
  [sgeulette]

0.66 (2023-02-13)
-----------------

- Added `transmogrifier` module with `get_main_path`, `relative_path` and
  `text_int_to_bool` functions.
  [sgeulette]
- Added `none_if_unfound` parameter in `get_user_fullname` function
  [sgeulette]
- Added parameter `onsuccess=false` to JS function `callViewAndReload` so it is
  possible to trigger custom JS code after a success.
  [gbastien]
- Added `xhtml.is_html` that will return True or False if given text is HTML or not.
  [gbastien]
- Raised validation error when email realname contains an accented character
  [sgeulette]

0.65 (2022-12-07)
-----------------

- Return new date when `cache.invalidate_cachekey_volatile_for` is called with
  `get_again=True`.
  [gbastien]
- Use `dict.items` instead `dict.iteritems` for Py2/Py3 compatibility.
  [gbastien]

0.64 (2022-10-28)
-----------------

- Added `workflow.remove_state_transitions` function do remove transitions on a state and clean duplicates
  [sgeulette]
- Added more tests on cached methods.
  [sgeulette]

0.63 (2022-09-01)
-----------------

- Invalidated '_users_groups_value' volatile after a call of `GroupAwareRoleManager.assignRolesToPrincipal`,
  `ZODBRoleManager.assignRoleToPrincipal` and `ZODBRoleManager.removeRoleFromPrincipal`
  [sgeulette]
- Removed duplicated classifiers.
  [sgeulette]

0.62 (2022-08-19)
-----------------

- Added `IMIORAMCache` using `IMIOStorage` to extend used cache duration and
  improve displayed statistics
  [gbastien]
- Added cache on various acl methods following `decorate_acl_methods` env variable
  [gbastien, sgeulette]
- Added IIMIOLayer BrowserLayer (need to execute upgrade step to 2).
  [gbastien]
- Override `caching-controlpanel-ramcache` to compute totals for `Hits`, `Misses`,
  `Size` and `Entries`, display `Older entry`, do not break to display statistics
  when a pickle error occurs but add a portal message.
  [gbastien]
- Added parameter `ttl=0` to `cache.get_cachekey_volatile` this way a date older
  than given `ttl` (in seconds) will be recomputed.
- Added 'none_if_no_user' param in `content.get_user_fullname`.
  [sgeulette]
- Always return unicode in `content.get_user_fullname`.
  [sgeulette]
- Added `test_helpers.ImioTestHelpers` class with useful methods from iA.delib
  [sgeulette]
- Added `vocabularies.SimplySortedUsers` and modified `vocabularies.SortedUsers`
  [sgeulette]
- Added `cache.get_users_in_plone_groups`
  [sgeulette]
- Added `setup.load_type_from_package` to reload a single type.
  Moved `workflow.load_workflow_from_package` to `setup.load_workflow_from_package`.
  [gbastien]

0.61 (2022-07-01)
-----------------

- Moved workflow related functions from content to workflow module.
  [sgeulette]
- Added `workflow.load_workflow_from_package` to reload a single workflow.
  [sgeulette]
- Be defensive in JS function `toggleDetails` if tag is not available.
  [gbastien]

0.60 (2022-06-24)
-----------------

- Handled unfound site in `set_site_from_package_config`.
  [sgeulette]

0.59 (2022-06-21)
-----------------

- Added `escaped=True` param on `xhtml.object_link`.
  [sgeulette]
- Require a version of `future` recent enough so `html.escape` is available.
  [gbastien]
- Added parameter `replace_not_found_image=True` to `xhtml.storeImagesLocally`,
  when `True` (default) and an image could not be retrieved,
  a `Not found` image will be used. This solves problem when copy/paste a private
  image from another site, available in the browser because of shared
  authentication but not retrievable.
  [gbastien]

0.58 (2022-06-14)
-----------------

- Added `get_zope_root` to get zope app.
  [sgeulette]
- Added `zope_app` parameter in `set_site_from_package_config`.
  [sgeulette]
- Fixed `xhtml.replace_content`, make sure the entire content is replaced
  including sub tags.
  [gbastien]

0.57 (2022-06-10)
-----------------

- Added `NoEscapeLinkColumn` as base for link column rendering html.
  Escape must be done in inherited column.
  [sgeulette]
- `content.uuidToObject` will now return `None` instead an empty list if uuid not found.
  [gbastien]
- Remove zope.app.publication dependency in `security.set_site_from_package_config` as it is now
  removed since Plone >= 5.2.6
  [aduchene]

0.56 (2022-05-13)
-----------------

- Added `setup_ram_cache` method.
  [sgeulette]
- Added `set_site_from_package_config` method
  [sgeulette]

0.55 (2022-05-06)
-----------------

- Improved `get_relations` to get optionally referenced objects.
  [sgeulette]

0.54 (2022-03-25)
-----------------

- Added `content.get_vocab_value` based on `content.get_vocab` but returns
  the values (`attr_name='token'` by default, may also be `value` or `title`).
  [gbastien]
- Added `EnhancedTerm` based on `SimpleTerm` providing `attrs` dict on term
  [sgeulette]
- Added `cache.cleanForeverCache` that will clear cache of functions using the
  `@forever.memoize` decorator.
  [gbastien]

0.53 (2022-03-17)
-----------------

- Refactored `get_object`
  [sgeulette]

0.52 (2022-01-12)
-----------------

- Added `cache.obj_modified` function that returns max value between
  obj.modified(), obj._p_mtime and __anotations__._p_mtime
  [sgeulette]
- Added `cache.extract_wrapped` function that returns original decorated function.
  Useful to compare cached and non cached results in tests.
  [sgeulette]
- Updated git fetch url
  [sgeulette]

0.51 (2022-01-03)
-----------------

- Added monkey patch to handle SSL mailer on port 465.
  [sgeulette]
- Added `content.base_getattr` method that will `getattr` without acquisition.
  [gbastien]

0.50 (2021-11-26)
-----------------

- Added `content.get_transitions` to be able to get available transition ids
  (as `wfTool.getTransitionsFor` returns a list of dict with transition infos).
  [gbastien]
- Added `adapters.MissingTerms`, a base `z3c.form` missing terms adapter to be
  extended by local packages.
  [gbastien]
- Added cache auto invalidation mecanism when using `cache.get_cachekey_volatile`
  the caller method can be passed, it's name is stored in the volatiles registry
  then when calling `cache.invalidate_cachekey_volatile_for` with
  `invalidate_cache=True`, every cached methods are invalidated from `ram.cache`.
  This will make stale cache be invalidated immediatelly as when a date changed,
  the existing cache is never used again.
  [gbastien]

0.49 (2021-11-08)
-----------------

- Require `plone.api>1.9.1` because we need `content._parse_object_provides_query`.
  This is necessay since we added `content.find`.
  [gbastien]

0.48 (2021-10-20)
-----------------

- Renamed `content.ur_find` to `content.find` with unrestricted parameter.
  [sgeulette]
- Fixed `content.find` to avoid error if corresponding looped object is deleted.
  [sgeulette]

0.47 (2021-10-13)
-----------------

- Fixed `content.get_user_fullname` that was breaking when user had no fullname.
  [gbastien]
- Added `content.ur_find` that's the same as api.content.find but unrestrictedly
  [sgeulette]

0.46 (2021-09-28)
-----------------

- Added `xhtml.replace_content` function that will replace the content of given
  XHTML tag with some other content. This relies on package `cssselect` that is
  added as an extra dependency thru `imio.helpers[lxml]`.
  [gbastien]

0.45 (2021-07-16)
-----------------

- Added `imio.helpers.SortedUsers`, a vocabulary listing users sorted using
  `natsort.humansorted`. We need to rely on `natsort` to handle this.
  [gbastien]
- Fixed bug in JS function `submitFormHelperOnsuccessDefault` called onsuccess
  by `submitFormHelper` to only consider response as a file to return if
  responser header `content-length` is found in request, this avoid returning
  a wrong blob object when called code returns an error message.
  [gbastien]

0.44 (2021-06-15)
-----------------

- In `xhtml.separate_images` be a bit less defensive, too complex cases are
  still ignored but when the `<p>` contains only non textual elements like
  `<br>` or `blanks`, just ignore these elements.
  [gbastien]

0.43 (2021-05-31)
-----------------

- Lowercased email address after validation.
  [sgeulette]
- Fixed `submitFormHelperOnsuccessDefault` JS function to handle binary response
  so it is possible to download the result of the ajax query.
- Added `xhtml.imagesToData` that turns the src of images used in a xhtml
  content from an `http` or equivalent URL to a data base64 value.
  [gbastien]

0.42 (2021-04-30)
-----------------

- Added parameter `filetype='PNG'` to `barcode.generate_barcode` so it is
  possible to use another supported image file format.
  [gbastien]
- Added parameter `replyto` to `emailer.send_email` so it is possible to add
  `reply-to` header in message
  [sgeulette]
- Adapted `content.object_values` and `content.object_ids` to be able to pass
  a single class name or a list of class names like it is the case for
  `objectValues/objectIds`.
  [gbastien]

0.41 (2021-04-21)
-----------------

- Corrected encoding problem in emailer.
  [sgeulette]

0.40 (2021-04-01)
-----------------

- Added `target` option in `object_link` function
  [sgeulette]
- Added a ZPublisher `:json` suffix type converter.
  [gbastien]
- Changed MockMailHost patch to avoid some problems
  [sgeulette]
- Make `xhtml.storeImagesLocally` handle images with `src` using base64 encoded
  data (like `data:image/png;base64,...)`.
  [gbastien]

0.39 (2021-02-25)
-----------------

- Added `validate_email_address` to check email address with a real name part.
  [sgeulette]
- Added `validate_email_addresses` to check email addresses, separated by a comma.
  [sgeulette]
- Added `content.get_modified_attrs`, when called in a `IObjectModifiedEvent`
  handler, will return the list of field names that were actually modified.
  [gbastien]
- Returned email sender error messages.
  [sgeulette]
- Added `content.uuidToCatalogBrain` that is a shortcut to
  `content.uuidsToCatalogBrains` but that will return a single value.
  [gbastien]
- Added `content.object_values` and `content.object_ids` method, equivalent to
  Zope's `objectValues` and `objectIds` but that will check contained element
  class name instead `meta_type` so it works with DX content types where
  `meta_type` is the same for every types.
  [gbastien]
- Added `content.uuidToObject` that is a shortcut to
  `content.uuidsToObjects` but that will return a single value.
  [gbastien]
- Corrected `has_faceted` function call in `submitFormHelperOnsuccessDefault` js
  [sgeulette]
- Reloaded page when `submitFormHelper` is used on a non faceted page
  [sgeulette]
- Added parameter `toggle_type='slide'` to JS helper `toggleDetails`,
  so it is possible to use `slideToggle` (default) or `fadeToggle`.
  `fadeToggle` behaves better when the hidden part contains a sticky element
  (table header).
  [gbastien]

0.38 (2021-01-06)
-----------------

- Added `content.normalize_name` that will normalize a given name, this is the
  code used when turning a title to an id when creating a new content.
  [gbastien]

0.37 (2020-12-21)
-----------------

- Added JS function `submitFormHelper` that will submit a given form and
  `onsuccess`, will call the function `onsuccess` in parameter
  (by default, when called in an overlay, will close the overlay and
  reload the faceted navigation).
  [gbastien]
- Added `security.fplog` helper to ease adding a `collective.fingerpointing`
  message to the log.
  [gbastien]
- Added `plone.app.relationfield` as a direct dependency.
  [gbastien]

0.36 (2020-12-07)
-----------------

- Added email functions (`create_html_email`, `add_attachment`, `send_email`)
  to create and send an email with attachments.
  [sgeulette]
- Optimized `xhtml.separate_images`, do only walk the tree if
  it contains images (`img` tag).
  [gbastien]
- Fixed `content.richtextval` `outputMimeType` parameter to use
  `text/x-html-safe` instead `text/html`.
  [gbastien]
- Renamed JS function `loadCollapsibleContent` to `loadContent` as it can be
  used outside of `collapsible` scope.
  [gbastien]

0.35 (2020-11-18)
-----------------

- Added JS helper method `canonical_url` to get the current canonical URL
  so the url of the context when on a view.
  [gbastien]
- In `toggleDetails` JS function, moved the part that does the async load in
  `loadCollapsibleContent` function so it is possible to call if from outside.
  [gbastien]
- Added `get_user_from_criteria` helper method to search users following
  email or fullname
  [sgeulette]
- Added param on `transitions` method, to not warn by default
  [sgeulette]
- Completed `appy_pod` usecases, `font-size 50%/150%`.
  [gbastien]
- Added `catalog.merge_queries` function that merges `plone.app.querystring`
  compatible catalog queries into one single query.
  [gbastien]
- Do not break in `xhtml.storeImagesLocally` if a `NotFound` occurs while
  getting an internal image.
  [gbastien]

0.34 (2020-10-16)
-----------------

- Moved JS function `setoddeven` from `listings.js` to
  `helpers.js` so it is available by default.
  [gbastien]
- Added setup_logger in security module to change logger level (when
  doing `instance run` by example)
  [sgeulette]

0.33 (2020-10-01)
-----------------

- Added `content.get_relations` and `content.get_back_relations` to easily
  get relations and back relations on an object.
  [gbastien]
- Do not break in `xhtml.storeImagesLocally` if image URL
  contains non-ASCII characters.
  [gbastien]
- Added `xhtml.separate_images` that will make sure images are separated in
  different `<p>` to avoid breaking `appy.pod` when using `LibreOffice 6.0.x`.
  [gbastien]

0.32 (2020-09-10)
-----------------

- Log every 1000 elements instead 100 in `catalog.addOrUpdateIndexes` and
  `catalog.reindexIndexes`.
  [gbastien]
- Fixed code to make except Exception syntax Python 3.8 compatible.
  [gbastien]

0.31 (2020-08-18)
-----------------

- Correctly translate a utf8 state title.
  [sgeulette]
- Added `content.safe_delattr` to avoid having to check `base_hasattr` before.
  [gbastien]
- Added JS helper function `toggleDetails` to be able to show/hide details
  using a collapsable `<div>`.
  [gbastien]
- Completed `appy_pod` usecases,
  fixed images to use https://picsum.photos/ instead https://www.imio.be
  [gbastien]

0.30 (2020-06-24)
-----------------

- In `content.uuidsToObjects`, get object with `brain._unrestrictedGetObject`
  in case parameter `unrestricted=True`.
  [gbastien]

0.29 (2020-05-28)
-----------------

- Added parameter `unrestricted=False` to `content.uuidsToCatalogBrains` and
  `content.uuidsToObjects`, when `True`, catalog search is done unrestricted.
  [gbastien]

0.28 (2020-05-26)
-----------------

- Added `outputMimeType` parameter to `richtextval` method
  [sgeulette]
- Added parameter `query={}` to `content.uuidsToCatalogBrains`, this let's you
  complete the catalog query in case you have `UIDs` and you want to filter
  it on additional index like `review_state`.
  [gbastien]
- Added new parameter `catalog_id='portal_catalog'` to methods
  `catalog.addOrUpdateIndexes`, `catalog.removeIndexes`,
  `catalog.removeColumns` and `catalog.reindexIndexes` so it is possible to
  proceed with another catalog than `portal_catalog`.
  [gbastien]
- Added parameter `check_contained_uids=False` to
  `content.uuidsToCatalogBrains` and `content.uuidsToObjects`,
  when set to `True`, if query on `UID` index returns nothing, it will query on
  `contained_uids` index if it exists in the `portal_catalog` that is a special
  index used to index `UIDs` of contained elements that are not indexed.
  [gbastien]
- Added `IContainerOfUnindexedElementsMarker` marker interface to mark objects
  containing unindexed objects.
  [gbastien]

0.27 (2020-04-20)
-----------------

- Do not break in `xhtml.imagesToPath` if `<img>` use a
  wrong `resolveuid/unknown_uid`.
  [gbastien]
- Fixed tests to not use images from site `https://www.imio.be/` but
  from site `https://i.picsum.photos/`.
  [gbastien]

0.26 (2020-02-25)
-----------------

- Added set_to_annotation method.
  [sgeulette]
- Always return something in annotations functions.
  [sgeulette]

0.25 (2019-11-26)
-----------------

- Added logging in `xhtml.storeImagesLocally` if unable to
  traverse to `img_path`.
  [gbastien]
- Fixed bug in `xhtml.storeImagesLocally` where an image stored in another
  Plone element having `absolute_url` starting with current element
  `absolute_url` was not stored locally.
  [gbastien]

0.24 (2019-11-25)
-----------------

- Removed wrong overrides of `collective.iconifiedcategory` translation file.
  [gbastien]
- Added optionally behavior prefix in get_schema_fields.
  [sgeulette]
- Fixed bug in `xhtml.storeImagesLocally._handle_internal_image` to be sure
  that traversed path to image does not starts with a `/` or it fails with
  a `KeyError`.  This is the case when the `Plone Site` is using a domain name.
  Make sure also traversed `img_path` element is actually an `Image`.
  [gbastien]

0.23 (2019-09-12)
-----------------

- Added `content.get_vocab` helper method to easily get a `IVocabularyFactory`
  vocabulary instance or only the factory when parameter `only_factory=True`.
  [gbastien]
- Added `catalog.reindexIndexes` helper method making it possible to reindex a
  specific `portal_catalog` index with `ZLogHandler` log output.
  [gbastien]
- Added javascript function to callViewAndReload with ajax. Gotten from PloneMeeting ;-)
  [sgeulette]
- Added get_state_infos (used in PM and plonetheme.imioapps).
  [sgeulette]

0.22 (2019-08-23)
-----------------

- Added parameter `update_metadata` to `catalog.addOrUpdateColumns`,
  if `True` (default), the new added metadata are updated on every
  catalogued objects.
  [gbastien]
- Added function to return html link for an object
  [sgeulette]

0.21 (2019-08-13)
-----------------

- Added parameter `get_again=False` to
  `cache.invalidate_cachekey_volatile_for`, when True, this will call
  `cache.get_cachekey_volatile` just after the cache is invalidated so we get
  a fresh date stored. This is useful to avoid write by async requests if it
  calls `cache.get_cachekey_volatile`.
  [gbastien]

0.20 (2019-07-19)
-----------------

- In `xhtml.storeImagesLocally`, do not break when a `resolveuid` is found but
  it does not find the image. This can be the case when copy/pasting HTML code
  from another instance or so.
  [gbastien]
- In `xhtml.removeBlanks`, check if content is empty by calling
  `xhtml.xhtmlContentIsEmpty` with parameter `tagWithAttributeIsNotEmpty=False`
  so empty tags with attributes are considered empty.
  [gbastien]

0.19 (2019-07-05)
-----------------

- Patch index method from collective.solr to fix an issue with partial reindex
  [mpeeters]
- Added css id on row field display in container.pt and content.pt.
  [sgeulette]

0.18 (2019-05-16)
-----------------

- Added `appy.pod` sample that show problem of wrongly defined style like
  `margin-left: opt;` using `opt` instead `0pt`.
  [gbastien]
- Added `appy.pod` sample that show problem of class not used in `<li>`
  or `<td>`.
  [gbastien]
- Added methods `content.disable_link_integrity_checks` and
  `content.restore_link_integrity_checks` to be able to disable the
  `enable_link_integrity_checks property` and to restore it to it's original
  value.  This works for Plone4 (property) and Plone5 (registry).
  [gbastien]
- Fix import of `IEditingSchema` on Plone5.
  [gbastien]

0.17 (2019-02-12)
-----------------

- Added collapsible option on container view.
  [sgeulette]
- Do not store date for get_cachekey_volatile/invalidate_cachekey_volatile_for
  in a volatile (_v_...) as it seems "stored" by thread and is computed to much
  times.
  [gbastien]
- Added JS helper method has_faceted returning true if currently on a faceted.
  [gbastien]

0.16 (2019-01-31)
-----------------

- Added `appy.pod` usecase to show problems with table optimization if
  `<td>` has a defined size.
  [gbastien]
- Added `appy.pod` usecase to show problems with table having a first empty
  `<tr></tr>` that do not render second column of following lines.
  [gbastien]
- Added `appy.pod` usecase for line-height style.
  [gbastien]
- Added `appy.pod` usecase for `<img>` without `src` that breaks generation.
  [gbastien]
- Do not break in `xhtml.imagesToPath` if `<img>` does not have a `src`.
  [gbastien]

0.15 (2018-12-18)
-----------------

- Display more logging in `content.validate_fields` when bypassing validation.
  [gbastien]
- In `catalog.addOrUpdateIndexes`, pass a `ZLogHandler` to `reindexIndex` so the
  progress is shown in the Zope log.
  [gbastien]
- In `content.add_to_annotation` and `content.del_from_annotation`, store
  annotation in a `PersistentList` instead a `set()` to avoid persistence
  problems.
  [gbastien]

0.14 (2018-10-22)
-----------------

- Improved content create to avoid creating object when defined id already exists.
  [sgeulette]
- Added methods content.uuidsToCatalogBrains and content.uuidsToObjects.
  [gbastien]
- Adapted `content.validate_fields` to bypass validation when field.required=False,
  value is None and field type is other than Bool.  Validation is also bypassed for
  field using a `source` attribute because it fails for now...
  [gbastien]
- Added parameter raise_on_errors to content.validate_fields to raise a ValueError
  when errors are found instead simply returning it.
  [gbastien]

0.13 (2018-08-31)
-----------------

- Added `content.get_schema_fields` to get schema fields (behaviors included
  by default).
  [sgeulette]
- Pep8 on imports.
  [sgeulette]
- Added appy.pod usecase for lists containing tables.
  [bleybaert]
- Added dependency on `Plone` in `setup.py`.
  [gbastien]
- Do not break in `xhtml.storeImagesLocally._handle_internal_image` if image
  src is not a path to an image but to another element (like `Folder` or
  `Plone Site`).
  [gbastien]

0.12 (2018-05-03)
-----------------

- Added appy.pod usecase for rgba().
  [gbastien]
- Improved annotation code
  [sgeulette]

0.11 (2018-01-30)
-----------------

- Use `html` instead `xml` for `lxml.html.to_string` rendering `method`.
  This avoids results like `<p><s></s></p>` turned to `<p><s/></p>`.
  [gbastien]

0.10 (2017-12-21)
-----------------

- Fixed bug in `catalog.addOrUpdateIndexes` where a new index was not reindexed
  if it was added together with an already existing index.
  [gbastien]
- Fixed bug in `xhtml.storeImagesLocally` when img uses a `resolveuid` and
  starts with the `portal_url` (this is the case when using `uploadimage plugin`
  in `collective.ckeditor`), it raised a NotFound error.
  [gbastien]
- In `xhtml.storeImagesLocally`, keep the `scale` at the end of the URL using
  `resolveuid` (like `resolveuid/content_uid/image_preview`).
  [gbastien]
- Use `PyPDF2` instead deprecated `pyPdf` to insert barcode into PDF.
  This solves `ValueError: invalid literal for int() with base 10: ''`.
  [gbastien]

0.9 (2017-11-27)
----------------

- Added appy.pod usecase for complex styles start/end on same paragraph.
  [gbastien]
- Do not break in `xhtml.storeImagesLocally` when no `<img> src` found.
  [gbastien]
- Add methods to manage annotations (Add and Remove).
  [anuyens, odelaere]
- Added method to get annotation
  [sgeulette]

0.8 (2017-10-04)
----------------

- In `xhtml.storeImagesLocally`, take into account `<img> src`
  that uses `resolveuid`.  This is the case when using `collective.ckeditor` and
  option `allow_link_byuid` is enabled.
  [gbastien]
- Do not use `/* ... */` together with `https://` in helpers.js comment or
  merged javascripts produce a wrong format and raise a JS comment unterminated
  error in the browser.
  [gbastien]

0.7 (2017-09-22)
----------------

- Added method `testing_logger` to `testing.py` that enables logging into tests.
  [gbastien]

0.6 (2017-09-15)
----------------

- Changed method `xhtml.storeExternalImagesLocally` to
  `xhtml.storeImagesLocally`, it handles now external and internal images
  retrieval so an image stored in the portal is also created in given context
  when necessary.
  [gbastien]

0.5 (2017-08-30)
----------------

- Added method to safe encode string.
  [sgeulette]
- appy.pod usecase : table using width of 0px.
  [gbastien]
- In `content.validate_fields`, added special bypass to avoid failing
  validation for `Choice` field that is `required=False` and for which given
  value is None. Validation fails because None not in vocabulary but it is
  nevertheless a correct value as it is managed by the widget while added thru
  the UI.
  [gbastien]
- Added JS fix to be able to print `<fieldset>` on several pages in Firefox,
  see https://bugzilla.mozilla.org/show_bug.cgi?id=471015.
  This makes it necessary to add a default profile to add the JS resource
  `++resource++imio.helpers/helpers.js`.
  [gbastien]

0.4.29 (2017-07-25)
-------------------

- Get intid value or create it if not found.
  [sgeulette]
- Added possibility to pass 'scale' value to pdf.BarcodeStamp.
  [gbastien]
- More appy.pod usecase : not rendered sub bullets with no parent bullet.
  [gbastien]

0.4.28 (2017-07-04)
-------------------

- Added method to create NamedBlobFile or NamedBlobImage.
  [sgeulette]

0.4.27 (2017-06-30)
-------------------

- Return portal when obj_path is / on create content.
  [bsuttor]
- Added case for appy.pod that show complex HTML structure failing
  in appy.pod 0.9.7.
  [gbastien]
- Added root attribute in fancytree
  [sgeulette]
- Changed barcode generation options, following zint 2.6
  [sgeulette]

0.4.26 (2017-03-14)
-------------------

- Set CLASS_TO_LAST_CHILDREN_NUMBER_OF_CHARS_DEFAULT = 240.
  [gbastien]

0.4.25 (2017-02-21)
-------------------

- Use same class names than appy.pod regarding the 'keep with next'
  functionnality.
  [gbastien]

0.4.24 (2017-02-14)
-------------------

- In content.validate_fields, initialize field by calling bind(obj) so
  necessary things like vocabularies are available.
  [gbastien]

0.4.23 (2017-02-14)
-------------------

- Added content module test.
  [sgeulette]
- Improved get_object, add_image, add_file, create methods
  [sgeulette]
- Added content.validate_fields that will validate fields of
  a given dexterity obj.
  [gbastien]

0.4.22 (2016-12-21)
-------------------

- Added more usecases to test appy.pod rendering : 'text-decoration: none;',
  complex and reallife table examples, ...
  [gbastien]
- Added method xhtml.removeCssClasses to be able to remove some specific Css
  classes from a given xhtmlContent.
  [gbastien]

0.4.21 (2016-12-05)
-------------------

- Added method xhtml.addClassToContent that gives the ability to add a CSS class
  to the CONTENT_TAGS (<p>, <strong>, ...) of a given xhtmlContent.
  [gbastien]
- Add @volatile_cache_without_parameters and
  @volatile_cache_with_parameters decorators
  [mpeeters]
- Store the volatile keys on a dictionary on the portal
  [mpeeters]
- Can add a file to an object.
  [sgeulette]
- Added case in 'appy_pod_sample' to check when style attribute is used to
  define italic/bold/underline/strike directly on <li> or on <li> containing
  <p> or <span>.
  [gbastien]


0.4.20 (2016-10-05)
-------------------

- Added 'path' module with method 'path_to_package' that will return the absolute
  FS path to a given package.  An extra 'filepart' can be provided to complete the
  returned path.  This is useful to get a template in a 'browser/template' folder
  for example.
  [gbastien]


0.4.19 (2016-09-26)
-------------------

- Do not pretty_print HTML returned by lxml.html.tostring or it can leads to
  weird behaviors like extra blank space in case we have nested <span> tags.
  'pretty_print' is now a parameter to relevant methods and is False by default
  [gbastien]
- Added methods to create content from a dictionary, to get object following
  criterias, to apply multiple transitions, to create a RichTextValue object
  [sgeulette]
- Added default views for Dexterity content and container that display
  fields in a table with widget label and the left and widget value on
  the right.  The view for container also includes an asynchronous
  folder_listing that lists contained elements.
  Taken from imio.project.core
  [gbastien]


0.4.18 (2016-06-17)
-------------------

- Use by default scale=2 instead of scale=4 when generating barcode.
  [gbastien]
- Added methods int2word, wordizeDate and formatDate aiming to transform
  numbers into french translation, date with only numbers into date in full
  and to format dates (with hours, with month name in full, ...).
  [DieKatze]


0.4.17 (2016-03-22)
-------------------

- Added constant CLASS_TO_LAST_CHILDREN_NUMBER_OF_CHARS_DEFAULT to define the
  default number of characters to take into account while marking last tags
  in xhtml.addClassToLastChildren.  This way it can be used in other packages.
  [gbastien]
- Fixed xhtml.imagesToPath to handle image src using 'resolveuid' correctly.
  [gbastien]


0.4.16 (2016-03-14)
-------------------

- Bugfix in xhtml.storeExternalImagesLocally if downloaded external image has
  no 'Content-Disposition' header.
  [gbastien]


0.4.15 (2016-03-14)
-------------------

- Added helper to be able to easily test appy.pod rendering by loading a full
  HTML content to any content (AT or DX) by specifying a RichText field_name.
  [gbastien]
- Added method xhtml.imagesToPath that turns the src of images used in a xhtml
  content from an 'http' or equivalent path to the absolute path on the FileSystem
  to the .blob image file.
  [gbastien]
- Added method xhtml.storeExternalImagesLocally that will ensure that externally
  referenced images are downloaded, stored locally and xhtmlContent is adapted
  accordingly.
  [gbastien]


0.4.14 (2016-02-25)
-------------------

- Added methods cache.get_cachekey_volatile and
  cache.invalidate_cachekey_volatile_for to be used with methods using
  decorator @ram.cache.  This is meant for long living cached methods that are
  invalidated manually. get_cachekey_volatile will be used in the method
  cachekey and invalidate_cachekey_volatile_for will be used to invalidate the
  cachekey.
  [gbastien]
- Add a function to generate a barcode with zint : #13100.
  [mpeeters]
- Removed initialize() call from __init__, no need to be considered
  as a Zope2 product.
  [gbastien]


0.4.13 (2016-01-22)
-------------------

- Use safe_unicode() instead of unicode(), especially in xhtml.markEmptyTags
  to avoid UnicideDecode errors.
  [gbastien]


0.4.12 (2016-01-21)
-------------------

- Added test when an uid (path) is no more in the portal_catalog,
  it does not break catalog.addOrUpdateColumns.
  [gbastien]
- In xhtml.xhtmlContentIsEmpty, do no more consider tag children in _isEmpty,
  a tag rendering nothing (text_content().strip() is empty) will be considered empty.
  [gbastien]


0.4.11 (2015-11-12)
-------------------

- Added 'cache.cleanRamCache' method that will invalidateAll ram.cache.
  [gbastien]


0.4.10 (2015-08-21)
-------------------

- Add get_environment method and test.
  [bsuttor]
- is_develop_environment method is true if global environment variable 'ENV' is equal to 'dev'.
  [bsuttor]
- Added 'cache' module with helper methods 'cleanVocabularyCacheFor' that will clean
  instance.memoize cache defined on a named vocabulary and 'cleanRamCacheFor' that
  will clean ram.cache defined on a given method.
  [gbastien]


0.4.9 (2015-04-21)
------------------

- In xhtml.addClassToLastChildren, do not define an empty class attribute.  Indeed, not
  managed tags were decorated with a 'class=""' attribute, this is no more the case.
  [gbastien]


0.4.8 (2015-04-20)
------------------

- Manage every text formatting tags in xhtml.addClassToLastChildren and
  do not break on unknwon tags.
  [gbastien]
- Replace special characters by corresponding HTML entity in xhtml.addClassToLastChildren
  so rendered content still contains original HTML entities.  This avoid HTML entities being
  rendered as UTF-8 characters and some weirdly recognized ("&nbsp;").
  [gbastien]


0.4.7 (2015-03-06)
------------------

- Adapted method xhtml.addClassToLastChildren to mark parent tag containing unhandled tags.
  [gbastien]


0.4.6 (2015-02-26)
------------------

- Added method markEmptyTags that will mark empty tags of a given
  xhtmlContent with a specific CSS class.
  [gbastien]
- Removed method security.call_as_super_user as we will rely on
  plone.api.env.adopt_roles to execute some methods as super user.
  [gbastien]


0.4.5 (2015-02-05)
------------------

- Added method to test if the buildout is in development mode (IS_DEV_ENV=True).
  [sgeulette]
- Added method to generate a password following criterias.
  [sgeulette]


0.4.4 (2015-01-29)
------------------

- Make it possible to pass specific class by tag to hxtml.addClassToLastChildren,
  this way, a specific class can be set depending on the node tag.
  [gbastien]


0.4.3 (2015-01-20)
------------------

- Added method addClassToLastChildren that will add a specific class attribute
  to last tags of a given xhtmlContent.
  [gbastien]


0.4.2 (2014-09-19)
------------------

- Do not consider xhtmlContent to easily empty : xhtmlContent is empty if it does not produce
  text, does not have attributes and does not have children.
  [gbastien]
- Use method xhtmlContentIsEmpty in method removeBlanks to avoid duplicating code and logic.
  [gbastien]

0.4.1 (2014-09-11)
------------------

- Corrected bug in 'removeBlanks' that removed children of an empty parent tag, that leaded
  to removal of complex trees like <u><li>My text</li><li>My second text</li></ul>.
  [gbastien]


0.3 (2014-09-04)
----------------

- Corrected bug in 'xhtmlContentIsEmpty' that did not managed correctly complex HTML tree.
  We use now lxml method 'text_content' to check if a HTML structure will render something or not.
  [gbastien]


0.2 (2014-08-27)
----------------

- Added xhtml.py module with helper methods for XHTML content :
    - 'removeBlanks' that will remove blank lines of a given xhtmlContent;
    - 'xhtmlContentIsEmpty' that will check if given xhtmlContent will produce something when rendered.

  [gbastien]

0.1 (2014-08-18)
----------------

- Initial release.
  [sdelcourt]
