import random
import numpy as np
import tensorflow as tf 



utt_lengths = [ 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500 ]
counts = [ 3, 10, 11, 13, 14, 13, 9, 8, 5, 4, 3, 2, 2, 2, 1 ]
label_lengths = [ 7, 17, 35, 48, 62, 78, 93, 107, 120, 134, 148, 163, 178, 193, 209 ]

freq_bins = 161
#scale_factor = 10 * 128
scale_factor = 128
extra = 1000

g_utter_counts = [x * scale_factor for x in counts]
g_batch_size = 0
g_randomness = np.zeros((1, freq_bins))
g_size = 0
g_duration = 0
g_current = 0


NUM_CLASSES = 29
NUM_PER_EPOCH_FOR_TRAIN = sum(counts)*scale_factor
#NUM_PER_EPOCH_FOR_TRAIN = 28535
NUM_PER_EPOCH_FOR_EVAL = 2703
NUM_PER_EPOCH_FOR_TEST = 2620

def  _init_data(batch_size):
    global g_batch_size
    global g_randomness
    global g_utter_counts
    global g_size
    global g_duration  
    if g_batch_size != batch_size:
        print 'set new batch_size %d' % (batch_size)
        g_current = 0
#        g_utter_counts = [x * scale_factor for x in counts]
        g_utter_counts = [x * scale_factor * batch_size for x in counts]
        g_batch_size = batch_size
        line = batch_size * (utt_lengths[-1] + extra)    
#        print g_randomness.shape
        np.resize(g_randomness, (line, freq_bins))
        g_randomness = np.random.randn(line, freq_bins)
        g_size = 0
        g_duration = 0
        for idx, val in enumerate(g_utter_counts):
            g_size = g_size + val
            g_duration = g_duration + val * utt_lengths[idx] / 100
#        print g_randomness
        print g_randomness.shape
#        print g_size
#        print g_duration

def _next(batch_size):
    _init_data(batch_size)
    global g_utter_counts
    global g_current
    if g_current >= len(g_utter_counts):
        return None
    else:
        inc = 0
        l_batch_size = 0

        if (g_utter_counts[g_current] > batch_size):
            l_batch_size = batch_size
            g_utter_counts[g_current] = g_utter_counts[g_current] - batch_size
            inc = 0
        else:
            l_batch_size = g_utter_counts[g_current]
            g_utter_counts[g_current] = 0
            inc = 1
#        print 'utter counts %d' % g_utter_counts[g_current]
        utt_length = utt_lengths[g_current]
        label_length = label_lengths[g_current]
        start_idx = random.randint(0, extra + batch_size * (utt_lengths[-1] - utt_lengths[g_current]) - 1)

        end_idx = start_idx + utt_length * l_batch_size

        g_current = g_current + inc
        label = range(label_length)
        for x in range(label_length):
            label[x] = random.randint(0, NUM_CLASSES-1)
        input = g_randomness[start_idx:end_idx, :]
#        print "next"
#        print input.shape
#        print utt_length
#        print label
        return utt_length, input, label

def _dense_to_sparse(dense):
    idx = []
    val = []
    for l in range(dense.shape[0]):
        for c in range(dense.shape[1]):
            if dense[l, c]!= 0:
                val.append(dense[l, c])
                idx.append([l, c])
    print idx, val, dense.shape
    return idx, val, dense.shape


def inputs(eval_data, data_dir, batch_size, shuffle=False):
    """Construct input for dummy data

    Returns:
      feats: MFCC. 3D tensor of [batch_size, T, F] size.
      labels: Labels. 1D tensor of [batch_size] size.
      seq_lens: SeqLens. 1D tensor of [batch_size] size.

    """
    utt_length, input, label = _next(batch_size) 
#    print utt_length
#    print input.shape
    print label

    seq_len = tf.constant(utt_length, shape=[batch_size]) 

    feats = tf.reshape(input, [batch_size, utt_length, freq_bins])
    labels = np.zeros((batch_size, len(label)))
    for x in range(batch_size):
        labels[x] = label
    idx, vals, s_shape = _dense_to_sparse(labels)
    t_labels = tf.SparseTensor(indices=idx, values=vals, shape=s_shape)
    print feats, t_labels, seq_len
    return tf.cast(feats, tf.float32), tf.cast(t_labels, tf.int32), seq_len

