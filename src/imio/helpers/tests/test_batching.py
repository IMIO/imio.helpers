# -*- coding: utf-8 -*-
from imio.helpers.batching import batch_delete_keys_file
from imio.helpers.batching import batch_get_keys
from imio.helpers.batching import batch_handle_key
from imio.helpers.batching import batch_hashed_filename
from imio.helpers.batching import batch_loop_else
from imio.helpers.batching import batch_skip_key

import logging
import os
import transaction
import unittest


INFILE = 'keys.pkl'
processed = {'keys': [], 'commits': 0, 'errors': 0}


def loop_process(loop_len, batch_number, commit_number, a_set, last=False):
    """Process the loop using the batching module."""

    batch_keys, config = batch_get_keys(INFILE, batch_number, last, commit_number, loop_len, a_set=a_set)
    for key in range(1, loop_len + 1):
        if batch_skip_key(key, batch_keys, config):
            continue
        processed['keys'].append(key)
        if batch_handle_key(key, batch_keys, config):
            break
    else:
        batch_loop_else(config['lc'] > 1 and key or None, batch_keys, config)
    if last:
        batch_delete_keys_file(batch_keys, config, rename=False)


def fake_transaction_commit():
    """Fake transaction commit."""
    processed['commits'] += 1


def fake_logger_error(msg, *args, **kwargs):
    """Fake logger error."""
    processed['errors'] += 1


class TestBatching(unittest.TestCase):

    def setUp(self):
        super(TestBatching, self).setUp()
        if os.path.exists(INFILE):
            os.remove(INFILE)

    def test_batching(self):
        orig_tc_func = transaction.commit
        transaction.commit = fake_transaction_commit
        logger = logging.getLogger('imio.helpers')
        orig_le_func = logger.error
        logger.error = fake_logger_error
        a_set = set()
        # no items
        loop_process(0, 0, 0, a_set)
        self.assertEqual(processed['keys'], [])
        self.assertEqual(processed['commits'], 0)
        self.assertSetEqual(a_set, set())
        self.assertFalse(os.path.exists(INFILE))
        # no batching
        loop_process(5, 0, 0, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 0)
        self.assertSetEqual(a_set, set())
        self.assertFalse(os.path.exists(INFILE))
        # no batching but commit used
        processed['keys'] = []
        processed['commits'] = 0
        loop_process(5, 0, 5, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 0)
        self.assertSetEqual(a_set, set())
        self.assertFalse(os.path.exists(INFILE))
        # batching: 2 passes with commit each item
        processed['keys'] = []
        processed['commits'] = 0
        loop_process(5, 3, 1, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3])
        self.assertEqual(processed['commits'], 3)
        self.assertSetEqual(a_set, {1, 2, 3})
        self.assertTrue(os.path.exists(INFILE))
        loop_process(5, 3, 1, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 5)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertTrue(os.path.exists(INFILE))
        # batching: 2 passes with commit each 3 items
        processed['keys'] = []
        processed['commits'] = 0
        a_set = set()
        os.remove(INFILE)
        loop_process(5, 3, 3, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3])
        self.assertEqual(processed['commits'], 1)
        self.assertSetEqual(a_set, {1, 2, 3})
        self.assertTrue(os.path.exists(INFILE))
        loop_process(5, 3, 3, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 2)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertTrue(os.path.exists(INFILE))
        loop_process(5, 3, 3, a_set, last=True)  # what if one more call ?
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 2)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertFalse(os.path.exists(INFILE))
        # batching: 1 pass with commit each 3 items
        processed['keys'] = []
        processed['commits'] = 0
        a_set = set()
        loop_process(5, 10, 3, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 2)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertTrue(os.path.exists(INFILE))
        loop_process(5, 10, 3, a_set, last=True)  # what if one more call ?
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 2)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertFalse(os.path.exists(INFILE))
        # batching: 1 pass with commit greather than items lentgh
        processed['keys'] = []
        processed['commits'] = 0
        a_set = set()
        loop_process(5, 10, 10, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 1)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertTrue(os.path.exists(INFILE))
        loop_process(5, 10, 10, a_set, last=True)  # what if one more call ?
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 1)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertFalse(os.path.exists(INFILE))
        # batching: 1 pass with 1 commit
        processed['keys'] = []
        processed['commits'] = 0
        a_set = set()
        loop_process(5, 5, 5, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 1)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertTrue(os.path.exists(INFILE))
        loop_process(5, 5, 5, a_set, last=True)  # what if one more call ?
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 1)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertFalse(os.path.exists(INFILE))
        # batching: finishing too early
        processed['keys'] = []
        processed['commits'] = 0
        a_set = set()
        loop_process(5, 3, 5, a_set, last=True)
        self.assertEqual(processed['keys'], [1, 2, 3])
        self.assertEqual(processed['commits'], 1)
        self.assertEqual(processed['errors'], 1)  # finished too early
        self.assertSetEqual(a_set, {1, 2, 3})
        self.assertFalse(os.path.exists(INFILE))

        transaction.commit = orig_tc_func
        logger.error = orig_le_func

    def test_batch_hashed_filename(self):
        nfn = batch_hashed_filename('file.txt')
        self.assertTrue(len(os.path.dirname(nfn)) > 1)
        self.assertEqual(os.path.basename(nfn), 'file_da39a3ee5e6b4b0d3255bfef95601890afd80709.txt')
