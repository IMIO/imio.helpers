# encoding: utf-8
# IMIO <support@imio.be>
#

"""
Batching utilities methods to do a process in multiple passes (divide a for loop).
Idea: a batch number, a commit number and a loop number are considered

1) we get a stored dictionary containing the treated keys (using load_pickle function)
2) if the key is already in the dictionary, we skip it (continue)
3) if the treated items number is >= batch number, we exit the for loop, do a commit and dump the dictionary
4) otherwise, we store the corresponding key in the dictionary and increase the loop number
5) when the current loop number is a multiple of the commit number, we do a commit and dump the dictionary
6) when the for loop is globally finished, we do a commit and dump the dictionary
7) when all the items are treated, we can delete the dictionary file

See `loop_process` function in `test_batching.py` file for a complete example.
"""

from datetime import datetime
from imio.pyutils.system import dump_pickle
from imio.pyutils.system import load_pickle

import logging
import os
import transaction


logger = logging.getLogger('imio.helpers')


# 1) we get a stored dictionary containing the treated keys (using load_pickle function)
def batch_get_keys(infile, batch_number, batch_last, commit_number, loop_length=0, a_set=None):
    """Returns the stored batched keys from the file.
    Must be used like this, before the loop:
    batch_keys, config = batch_get_keys(infile, batch_number, commit_number)

    :param infile: file name where the set is stored
    :param batch_number: the batch number
    :param batch_last: boolean to know if it's the last batch run
    :param commit_number: the commit interval number
    :param loop_length: the loop length number
    :param a_set: a given data structure to get the stored keys
    :return: 2 parameters: 1) a_set fulled with pickled data,
    2) a config dict {'bn': batch_number, 'cn': commit_number, 'lc': loop_count, 'pf': infile}
    """
    infile = os.path.abspath(infile)
    if not batch_number:
        return None, {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length, 'lc': 0,
                      'pf': infile}
    if a_set is None:
        a_set = set()
    load_pickle(infile, a_set)
    return a_set, {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length, 'lc': 0, 'pf': infile}


# 2) if the key is already in the dictionary, we skip it (continue)
def batch_skip_key(key, batch_keys, config):
    """Returns True if the key is already in the batch_keys.
    Must be used like this, at the beginning of the loop:
    if batch_skip_key(key, batch_keys):
        continue

    :param key: the hashable key of the current item
    :param batch_keys: the treated keys set
    :param config: a config dict {'bn': batch_number, 'bl': last, 'cn': commit, 'll': loop_length, 'lc': loop_count,
                                  'pf': infile}
    :return: True if a "continue" must be done. False otherwise.
    """
    if batch_keys is None:
        return False
    if key not in batch_keys:
        config['lc'] += 1
        return False
    return True


# 3) if the treated items number is higher than the batch number, we exit the loop, do a commit and dump the dictionary
# 4) otherwise, we store the corresponding key in the dictionary and increase the loop number
# 5) when the current loop number is a multiple of the commit number, we do a commit and dump the dictionary
def batch_handle_key(key, batch_keys, config):
    """Returns True if the loop must be exited.
    Must be used like this, in the end of the loop:
    if batch_handle_key(key, batch_keys, config):
        break

    :param key: the hashable key of the current item
    :param batch_keys: the treated keys set
    :param config: a config dict {'bn': batch_number, 'bl': last, 'cn': commit, 'll': loop_length, 'lc': loop_count,
                                  'pf': infile}
    :return: True if the loop must be exited. False otherwise.
    """
    if batch_keys is None:
        return False
    batch_keys.add(key)
    # stopping batch ?
    if config['lc'] >= config['bn']:
        if config['cn']:
            transaction.commit()
        config['ldk'] = key
        dump_pickle(config['pf'], batch_keys)
        logger.info("Batched %s / %s", len(batch_keys), config['ll'])
        if config['bl'] and not batch_globally_finished(batch_keys, config):
            logger.error('BATCHING MAYBE STOPPED TOO EARLY: %s / %s', len(batch_keys), config['ll'])
        return True
    # commit time ?
    if config['cn'] and config['lc'] % config['cn'] == 0:
        transaction.commit()
        config['ldk'] = key
        dump_pickle(config['pf'], batch_keys)
    return False


# 6) when the loop is globally finished, we do a commit and dump the dictionary
def batch_loop_else(key, batch_keys, config):
    """Does a commit and dump the dictionary when the loop is globally finished.
    Must be used like this, in the else part of the for loop:
    batch_loop_else(batch_keys, config)

    :param key: last key (can be None)
    :param batch_keys: the treated keys set
    :param config: a config dict {'bn': batch_number, 'bl': last, 'cn': commit, 'll': loop_length, 'lc': loop_count,
                                  'pf': infile, 'ldk': last_dump_key}
    """
    if batch_keys is None:
        return
    if key is None or (config.get('ldk') is not None and config['ldk'] == key):  # avoid if already done on last key
        return
    if config['cn']:
        transaction.commit()
    dump_pickle(config['pf'], batch_keys)
    logger.info("Batched %s / %s", len(batch_keys), config['ll'])
    if config['bl'] and not batch_globally_finished(batch_keys, config):
        logger.error('BATCHING MAYBE STOPPED TOO EARLY: %s / %s', len(batch_keys), config['ll'])


# 7) when all the items are treated, we can delete the dictionary file
def batch_delete_keys_file(batch_keys, config, rename=True):
    """Deletes the file containing the batched keys.

    :param batch_keys: the treated keys set
    :param config: a config dict {'bn': batch_number, 'bl': last, 'cn': commit, 'll': loop_length, 'lc': loop_count,
                                  'pf': infile}
    :param rename: do not delete but rename
    """
    if batch_keys is None:
        return
    try:
        if rename:
            os.rename(config['pf'], '{}.{}'.format(config['pf'], datetime.now().strftime('%Y%m%d-%H%M%S')))
        else:
            os.remove(config['pf'])
    except Exception as error:
        logger.exception('Error while deleting the file %s: %s', config['pf'], error)


def batch_globally_finished(batch_keys, config):
    """Is the loop globally finished?

    :param batch_keys: the treated keys set
    :param config: a config dict {'bn': batch_number, 'bl': last, 'cn': commit, 'll': loop_length, 'lc': loop_count,
                                  'pf': infile}
    :return: True if the loop is globally finished. False otherwise.
    """
    # if not batch_keys:
    #     return True
    # finished if the treated items number is higher than the items to treat or if nothing else is treated
    if config['ll']:
        return len(batch_keys) >= config['ll'] or config['lc'] == 0
    return config['lc'] == 0
