# encoding: utf-8
# IMIO <support@imio.be>
#

"""
Batching utilities methods to do a process in multiple passes (divide a for loop).
Idea: a batch number, a commit number and a loop number are considered

1) we get a stored dictionary containing the treated keys (using load_pickle function)
2) if the key is already in the dictionary, we skip it (continue). Otherwise, we increase the loop count
3) if the treated items number is >= batch number, we exit the for loop, do a commit and dump the dictionary
4) otherwise, we store the corresponding key in the dictionary
5) when the current loop number is a multiple of the commit number, we do a commit and dump the dictionary
6) when the for loop is globally finished, we do a commit and dump the dictionary
7) when all the items are treated, we can delete the dictionary file

See `loop_process` function in `test_batching.py` file for a complete example.
"""

from imio.pyutils.batching import batch_delete_files  # noqa: F401
from imio.pyutils.system import dump_pickle
from imio.pyutils.system import dump_var
from imio.pyutils.system import hashed_filename
from imio.pyutils.system import load_pickle

import logging
import os
import transaction


logger = logging.getLogger('imio.helpers')


# 1) we get a stored dictionary containing the treated keys (using load_pickle function)
def batch_get_keys(infile, loop_length=0, a_set=None, add_files=None):
    """Returns the stored batched keys from the file.
    Must be used like this, before the loop:
    batch_keys, config = batch_get_keys(infile, batch_number, commit_number)

    :param infile: file name where the set is stored
    :param loop_length: the loop length number
    :param a_set: a given data structure to get the stored keys
    :param add_files: a list of additional files to consider when deleting files
    :return: 2 parameters: 1) a_set fulled with pickled data,
    2) a config dict {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length, 'lc': loop_count,
                      'pf': infile, 'cf': config_file, 'kc': keys_count, 'lk': last_key, 'ldk': last_dump_key,
                      'fr'; first_run_bool, 'af': add_files}
    """
    infile = os.path.abspath(infile)
    commit_number = int(os.getenv('COMMIT', '0'))
    batch_number = int(os.getenv('BATCH', '0'))
    batch_last = bool(int(os.getenv('BATCH_LAST', '0')))
    if not add_files:
        add_files = []
    if not batch_number:
        return None, {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length, 'lc': 0,
                      'pf': infile, 'cf': None, 'kc': 0, 'fr': False, 'af': add_files}
    if not infile.endswith('.pkl'):
        raise Exception("The given file '{}' must be a pickle file ending with '.pkl'".format(infile))
    if a_set is None:
        a_set = set()
    load_pickle(infile, a_set)
    dic_file = infile.replace('.pkl', '_config.txt')
    first_run = not os.path.exists(dic_file)
    config = {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length, 'lc': 0, 'pf': infile,
              'cf': dic_file, 'kc': len(a_set), 'fr': first_run, 'af': add_files}
    dump_var(dic_file, config)
    return a_set, config


# 2) if the key is already in the dictionary, we skip it (continue). Otherwise, we increase the loop count
def batch_skip_key(key, batch_keys, config):
    """Returns True if the key is already in the batch_keys.
    Must be used like this, at the beginning of the loop:
    if batch_skip_key(key, batch_keys):
        continue

    :param key: the hashable key of the current item
    :param batch_keys: the treated keys set
    :param config: a config dict {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length,
                                  'lc': loop_count, 'pf': infile, 'cf': config_file, 'kc': keys_count, 'lk': last_key,
                                  'ldk': last_dump_key, 'fr'; first_run_bool, 'af': add_files}
    :return: True if a "continue" must be done. False otherwise.
    """
    if batch_keys is None:
        return False
    if key not in batch_keys:
        config['lc'] += 1
        return False
    return True


# 3) if the treated items number is higher than the batch number, we exit the loop, do a commit and dump the dictionary
# 4) otherwise, we store the corresponding key in the dictionary
# 5) when the current loop number is a multiple of the commit number, we do a commit and dump the dictionary
def batch_handle_key(key, batch_keys, config):
    """Returns True if the loop must be exited.
    Must be used like this, in the end of the loop:
    if batch_handle_key(key, batch_keys, config):
        break

    :param key: the hashable key of the current item
    :param batch_keys: the treated keys set
    :param config: a config dict {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length,
                                  'lc': loop_count, 'pf': infile, 'cf': config_file, 'kc': keys_count, 'lk': last_key,
                                  'ldk': last_dump_key, 'fr'; first_run_bool, 'af': add_files}
    :return: True if the loop must be exited. False otherwise.
    """
    if batch_keys is None:
        return False
    batch_keys.add(key)
    config['lk'] = key
    # stopping batch ?
    if config['lc'] >= config['bn']:
        if config['cn']:
            transaction.commit()
        config['ldk'] = key
        config['kc'] = len(batch_keys)
        dump_pickle(config['pf'], batch_keys)
        dump_var(config['cf'], config)
        logger.info("BATCHED %s / %s, already done %s", config['lc'], config['ll'], config['kc'])
        if config['bl'] and not batch_globally_finished(batch_keys, config):
            logger.error('BATCHING MAYBE STOPPED TOO EARLY: %s / %s', config['kc'], config['ll'])
        return True
    # commit time ?
    if config['cn'] and config['lc'] % config['cn'] == 0:
        transaction.commit()
        config['ldk'] = key
        config['kc'] = len(batch_keys)
        dump_pickle(config['pf'], batch_keys)
        dump_var(config['cf'], config)
    return False


# 6) when the loop is globally finished, we do a commit and dump the dictionary
def batch_loop_else(batch_keys, config):
    """Does a commit and dump the dictionary when the loop is globally finished.
    Must be used like this, in the else part of the for loop:
    batch_loop_else(batch_keys, config)

    :param batch_keys: the treated keys set
    :param config: a config dict {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length,
                                  'lc': loop_count, 'pf': infile, 'cf': config_file, 'kc': keys_count, 'lk': last_key,
                                  'ldk': last_dump_key, 'fr'; first_run_bool, 'af': add_files}
    """
    if batch_keys is None:
        return
    last_key = config.get("lk")
    # avoid if nothing was done or already done on last key
    if last_key is None or (config.get('ldk') is not None and config['ldk'] == last_key):
        return
    logger.info("BATCHED %s / %s, already done %s", config['lc'], config['ll'], len(batch_keys))
    if config['cn']:
        transaction.commit()
    config['kc'] = len(batch_keys)
    dump_pickle(config['pf'], batch_keys)
    dump_var(config['cf'], config)
    if config['bl'] and not batch_globally_finished(batch_keys, config):
        logger.error('BATCHING MAYBE STOPPED TOO EARLY: %s / %s', config['kc'], config['ll'])


# 7) when all the items are treated, we can delete the dictionary file
# we use now batch_delete_files from imio.pyutils


def batch_globally_finished(batch_keys, config):
    """Is the loop globally finished?

    :param batch_keys: the treated keys set
    :param config: a config dict {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length,
                                  'lc': loop_count, 'pf': infile, 'cf': config_file, 'kc': keys_count, 'lk': last_key,
                                  'ldk': last_dump_key, 'fr'; first_run_bool, 'af': add_files}
    :return: True if the loop is globally finished. False otherwise.
    """
    # if not batch_keys:
    #     return True
    if not config["bn"]:  # no batching
        return True
    if config['lc'] == 0:  # nothing treated
        return True
    elif config['fr']:  # first run with results
        return len(batch_keys) >= config['ll']
    elif config["bl"]:
        return True
    return False


def batch_hashed_filename(filename, to_hash=(), add_dir=True):
    """Returns a hashed filename.

    :param filename: the filename
    :param to_hash: a list of values to hash
    :param add_dir: boolean to know if we must prefix with the INSTANCE_HOME directory
    :return: the hashed filename
    """
    pklfile = hashed_filename(filename, '_'.join(map(repr, to_hash)))
    if add_dir:
        pklfile = os.path.join(os.getenv('INSTANCE_HOME', '.'), pklfile)
    return pklfile


def can_delete_batch_files(batch_keys, config):
    """Returns True if the batch config files can be deleted.

    :param batch_keys: the treated keys set
    :param config: a config dict {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length,
                                  'lc': loop_count, 'pf': infile, 'cf': config_file, 'kc': keys_count, 'lk': last_key,
                                  'ldk': last_dump_key, 'fr'; first_run_bool, 'af': add_files}
    :return: boolean
    """
    if config["fr"] and os.getenv("IU_RUN1", "0") == "1":  # if first run by imio.updates, the config file is needed.
        return False
    return batch_globally_finished(batch_keys, config)
