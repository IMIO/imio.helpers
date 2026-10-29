# -*- coding: utf-8 -*-
"""helpers.js runs without the Plone 4 JS libraries (Plone 6)."""

import json
import os
import subprocess
import unittest


try:
    from shutil import which
except ImportError:  # Python 2
    from distutils.spawn import find_executable as which


HELPERS_JS = os.path.join(os.path.dirname(__file__), "..", "browser", "static", "helpers.js")

# minimal jQuery and pat-plone-modal stubs: no prepOverlay, no qq (collective.quickupload)
RUNNER = """
var fs = require('fs'), vm = require('vm');
var modals = 0;
function jq() {
  var o = {length: 1};
  ['bind', 'on', 'filter', 'end', 'removeClass', 'addClass', 'find'].forEach(function(m) {
    o[m] = function() { return o; };
  });
  o.each = function(fn) { fn.call({}); return o; };
  o.ready = function(fn) { fn(); return o; };
  return o;
}
jq.fn = {};
jq.ajaxTransport = function() {};
globalThis.$ = jq;
globalThis.window = globalThis;
globalThis.location = {search: ''};
globalThis.document = {};
globalThis.__patternslib_registry = {'plone-modal': function() { modals += 1; }};
vm.runInThisContext(fs.readFileSync(process.argv[1], 'utf8'));
console.log(JSON.stringify({filterByName: typeof filterByName, modals: modals}));
"""


@unittest.skipIf(which("node") is None, "node is required")
class TestHelpersJS(unittest.TestCase):
    def test_helpers_js_plone6(self):
        output = subprocess.check_output(["node", "-e", RUNNER, HELPERS_JS])
        result = json.loads(output.decode("utf-8"))
        # the whole file is loaded (qq isn't defined) and the info overlays use pat-plone-modal
        self.assertEqual(result, {"filterByName": "function", "modals": 1})
