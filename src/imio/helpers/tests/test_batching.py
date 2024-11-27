# -*- coding: utf-8 -*-
from imio.helpers.batching import batch_get_keys
from imio.helpers.batching import batch_handle_key
from imio.helpers.batching import batch_hashed_filename
from imio.helpers.batching import batch_loop_else
from imio.helpers.batching import batch_skip_key
from imio.helpers.batching import can_delete_batch_files
from imio.pyutils.batching import batch_delete_files

import logging
import os
import transaction
import unittest


KEYS_PKL_FILE = 'keys.pkl'
CONFIG_FILE = 'keys_config.txt'
processed = {'keys': [], 'commits': 0, 'errors': 0}


def loop_process(loop_len, batch_number, commit_number, a_set, last=False, add_files=()):
    """Process the loop using the batching module."""
    os.environ['BATCH'] = str(batch_number)
    os.environ['COMMIT'] = str(commit_number)
    os.environ['BATCH_LAST'] = str(int(last))
    batch_keys, config = batch_get_keys(KEYS_PKL_FILE, loop_len, a_set=a_set, add_files=add_files)
    for key in range(1, loop_len + 1):
        if batch_skip_key(key, batch_keys, config):
            continue
        processed['keys'].append(key)
        if batch_handle_key(key, batch_keys, config):
            break
    else:
        batch_loop_else(batch_keys, config)
    if can_delete_batch_files(batch_keys, config):
        batch_delete_files(batch_keys, config, rename=False)
    return batch_keys, config


def fake_transaction_commit():
    """Fake transaction commit."""
    processed['commits'] += 1


def fake_logger_error(msg, *args, **kwargs):
    """Fake logger error."""
    processed['errors'] += 1


def remove_files():
    for fil in (KEYS_PKL_FILE, CONFIG_FILE):
        if os.path.exists(fil):
            os.remove(fil)


def reset_processed():
    processed['keys'] = []
    processed['commits'] = 0
    processed['errors'] = 0


class TestBatching(unittest.TestCase):

    def setUp(self):
        super(TestBatching, self).setUp()
        remove_files()

    def test_batching(self):
        orig_tc_func = transaction.commit
        transaction.commit = fake_transaction_commit
        logger = logging.getLogger('imio.helpers')
        orig_le_func = logger.error
        logger.error = fake_logger_error
        a_set = set()
        # no items
        keys, conf = loop_process(0, 0, 0, a_set)  # ll, bn, cn
        self.assertEqual(processed['keys'], [])
        self.assertEqual(processed['commits'], 0)
        self.assertSetEqual(a_set, set())
        self.assertEqual(conf['kc'], 0)
        self.assertEqual(conf['lc'], 0)
        self.assertEqual(conf.get('lk'), None)
        self.assertListEqual(conf["af"], [])
        self.assertIsNone(keys)
        self.assertFalse(os.path.exists(KEYS_PKL_FILE))
        self.assertFalse(os.path.exists(CONFIG_FILE))
        # no batching
        keys, conf = loop_process(5, 0, 0, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 0)
        self.assertSetEqual(a_set, set())
        self.assertEqual(conf['kc'], 0)
        self.assertEqual(conf['lc'], 0)
        self.assertEqual(conf.get('lk'), None)
        self.assertIsNone(keys)
        self.assertFalse(os.path.exists(KEYS_PKL_FILE))
        self.assertFalse(os.path.exists(CONFIG_FILE))
        # no batching but commit used
        reset_processed()
        keys, conf = loop_process(5, 0, 5, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 0)
        self.assertSetEqual(a_set, set())
        self.assertEqual(conf['kc'], 0)
        self.assertEqual(conf['lc'], 0)
        self.assertEqual(conf.get('lk'), None)
        self.assertIsNone(keys)
        self.assertFalse(os.path.exists(KEYS_PKL_FILE))
        self.assertFalse(os.path.exists(CONFIG_FILE))
        # batching: 2 passes with commit each item
        reset_processed()
        with open("various.pkl", 'w'):
            pass
        keys, conf = loop_process(5, 3, 1, a_set, add_files=["various.pkl"])
        self.assertEqual(processed['keys'], [1, 2, 3])
        self.assertEqual(processed['commits'], 3)
        self.assertSetEqual(a_set, {1, 2, 3})
        self.assertEqual(conf['kc'], 3)
        self.assertEqual(conf['lc'], 3)
        self.assertEqual(conf.get('lk'), 3)
        self.assertSetEqual(keys, a_set)
        self.assertTrue(os.path.exists(KEYS_PKL_FILE))
        self.assertTrue(os.path.exists(CONFIG_FILE))
        self.assertEqual(len(conf["af"]), 1)
        self.assertTrue(os.path.exists("various.pkl"))
        keys, conf = loop_process(5, 3, 1, a_set, last=True, add_files=["various.pkl"])
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 5)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertEqual(conf['kc'], 5)
        self.assertEqual(conf['lc'], 2)
        self.assertEqual(conf.get('lk'), 5)
        self.assertSetEqual(keys, a_set)
        self.assertFalse(os.path.exists(KEYS_PKL_FILE))
        self.assertFalse(os.path.exists(CONFIG_FILE))
        self.assertFalse(os.path.exists("various.pkl"))
        # batching: 2 passes with commit each 3 items
        reset_processed()
        a_set = set()
        remove_files()
        keys, conf = loop_process(5, 3, 3, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3])
        self.assertEqual(processed['commits'], 1)
        self.assertSetEqual(a_set, {1, 2, 3})
        self.assertEqual(conf['kc'], 3)
        self.assertEqual(conf['lc'], 3)
        self.assertEqual(conf.get('lk'), 3)
        self.assertSetEqual(keys, a_set)
        self.assertTrue(os.path.exists(KEYS_PKL_FILE))
        self.assertTrue(os.path.exists(CONFIG_FILE))
        keys, conf = loop_process(5, 3, 3, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 2)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertEqual(conf['kc'], 5)
        self.assertSetEqual(keys, a_set)
        self.assertTrue(os.path.exists(KEYS_PKL_FILE))
        self.assertTrue(os.path.exists(CONFIG_FILE))
        keys, conf = loop_process(5, 3, 3, a_set, last=True)  # what if one more call ?
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 2)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertEqual(conf['kc'], 5)
        self.assertEqual(conf['lc'], 0)
        self.assertEqual(conf.get('lk'), None)
        self.assertSetEqual(keys, a_set)
        self.assertFalse(os.path.exists(KEYS_PKL_FILE))
        self.assertFalse(os.path.exists(CONFIG_FILE))
        # batching: 1 pass with commit each 3 items by imio.updates
        reset_processed()
        os.environ["IU_RUN1"] = "1"
        remove_files()
        a_set = set()
        keys, conf = loop_process(5, 10, 3, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 2)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertEqual(conf['kc'], 5)
        self.assertEqual(conf['lc'], 5)
        self.assertEqual(conf.get('lk'), 5)
        self.assertSetEqual(keys, a_set)
        self.assertTrue(os.path.exists(KEYS_PKL_FILE))
        self.assertTrue(os.path.exists(CONFIG_FILE))
        # batching: 1 pass with commit each 3 items
        reset_processed()
        del os.environ["IU_RUN1"]
        remove_files()
        a_set = set()
        keys, conf = loop_process(5, 10, 3, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 2)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertEqual(conf['kc'], 5)
        self.assertEqual(conf['lc'], 5)
        self.assertEqual(conf.get('lk'), 5)
        self.assertSetEqual(keys, a_set)
        self.assertFalse(os.path.exists(KEYS_PKL_FILE))
        self.assertFalse(os.path.exists(CONFIG_FILE))
        # batching: 1 pass with commit greather than items lentgh
        reset_processed()
        a_set = set()
        keys, conf = loop_process(5, 10, 10, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 1)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertEqual(conf['kc'], 5)
        self.assertEqual(conf['lc'], 5)
        self.assertEqual(conf.get('lk'), 5)
        self.assertSetEqual(keys, a_set)
        self.assertFalse(os.path.exists(KEYS_PKL_FILE))
        self.assertFalse(os.path.exists(CONFIG_FILE))
        # batching: 1 pass with 1 commit
        reset_processed()
        a_set = set()
        keys, conf = loop_process(5, 5, 5, a_set)
        self.assertEqual(processed['keys'], [1, 2, 3, 4, 5])
        self.assertEqual(processed['commits'], 1)
        self.assertSetEqual(a_set, {1, 2, 3, 4, 5})
        self.assertEqual(conf['kc'], 5)
        self.assertEqual(conf['lc'], 5)
        self.assertEqual(conf.get('lk'), 5)
        self.assertSetEqual(keys, a_set)
        self.assertFalse(os.path.exists(KEYS_PKL_FILE))
        self.assertFalse(os.path.exists(CONFIG_FILE))
        # batching: finishing too early
        reset_processed()
        a_set = set()
        keys, conf = loop_process(5, 3, 5, a_set, last=True)
        self.assertEqual(processed['keys'], [1, 2, 3])
        self.assertEqual(processed['commits'], 1)
        self.assertEqual(processed['errors'], 1)  # finished too early
        self.assertSetEqual(a_set, {1, 2, 3})
        self.assertEqual(conf['kc'], 3)
        self.assertEqual(conf['lc'], 3)
        self.assertEqual(conf.get('lk'), 3)
        self.assertSetEqual(keys, a_set)
        self.assertTrue(os.path.exists(KEYS_PKL_FILE))
        self.assertTrue(os.path.exists(CONFIG_FILE))

        transaction.commit = orig_tc_func
        logger.error = orig_le_func

    def test_batch_hashed_filename(self):
        nfn = batch_hashed_filename('file.txt')
        self.assertTrue(len(os.path.dirname(nfn)) > 1)
        self.assertEqual(os.path.basename(nfn), 'file.txt')
