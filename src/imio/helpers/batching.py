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
from imio.pyutils.system import dump_var
from imio.pyutils.system import hashed_filename
from imio.pyutils.system import load_pickle

import logging
import os
import transaction


logger = logging.getLogger('imio.helpers')


# 1) we get a stored dictionary containing the treated keys (using load_pickle function)
def batch_get_keys(infile, loop_length=0, a_set=None):
    """Returns the stored batched keys from the file.
    Must be used like this, before the loop:
    batch_keys, config = batch_get_keys(infile, batch_number, commit_number)

    :param infile: file name where the set is stored
    :param loop_length: the loop length number
    :param a_set: a given data structure to get the stored keys
    :return: 2 parameters: 1) a_set fulled with pickled data,
    2) a config dict {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length, 'lc': loop_count,
                      'pf': infile, 'cf': config_file}
    """
    infile = os.path.abspath(infile)
    commit_number = int(os.getenv('COMMIT', '0'))
    batch_number = int(os.getenv('BATCH', '0'))
    batch_last = bool(int(os.getenv('BATCH_LAST', '0')))
    if not batch_number:
        return None, {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length, 'lc': 0,
                      'pf': infile, 'cf': None, 'kc': 0}
    if not infile.endswith('.pkl'):
        raise Exception("The giver file '{}' must be a pickle file ending with '.pkl'".format(infile))
    if a_set is None:
        a_set = set()
    load_pickle(infile, a_set)
    dic_file = infile.replace('.pkl', '_config.txt')
    config = {'bn': batch_number, 'bl': batch_last, 'cn': commit_number, 'll': loop_length, 'lc': 0, 'pf': infile,
              'cf': dic_file, 'kc': len(a_set)}
    dump_var(dic_file, config)
    return a_set, config


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
    logger.info("BATCHED %s / %s, already done %s", config['lc'], config['ll'], len(batch_keys))
    if config['lc'] == 0:  # nothing was done
        return
    if config['cn']:
        transaction.commit()
    config['kc'] = len(batch_keys)
    dump_pickle(config['pf'], batch_keys)
    dump_var(config['cf'], config)
    if config['bl'] and not batch_globally_finished(batch_keys, config):
        logger.error('BATCHING MAYBE STOPPED TOO EARLY: %s / %s', config['kc'], config['ll'])


# 7) when all the items are treated, we can delete the dictionary file
def batch_delete_files(batch_keys, config, rename=True):
    """Deletes the file containing the batched keys.

    :param batch_keys: the treated keys set
    :param config: a config dict {'bn': batch_number, 'bl': last, 'cn': commit, 'll': loop_length, 'lc': loop_count,
                                  'pf': infile}
    :param rename: do not delete but rename
    """
    if batch_keys is None:
        return
    try:
        for key in ('pf', 'cf'):
            if config[key] and os.path.exists(config[key]):
                if rename:
                    os.rename(config[key], '{}.{}'.format(config[key], datetime.now().strftime('%Y%m%d-%H%M%S')))
                else:
                    os.remove(config[key])
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
