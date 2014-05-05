'''
Basic metrics for evaluating onset detection systems.
Based in part on this script:
    https://github.com/CPJKU/onset_detection/blob/master/onset_evaluation.py
'''

import numpy as np
import functools
import collections
from . import util
import warnings

def validate(metric):
    '''Decorator which checks that the input annotations to a metric
    look like valid onset time arrays, and throws helpful errors if not.

    :parameters:
        - metric : function
            Evaluation metric function.  First two arguments must be
            reference_onsets and estimated_onsets.

    :returns:
        - metric_validated : function
            The function with the onset locations validated
    '''
    # Retain docstring, etc
    @functools.wraps(metric)
    def metric_validated(reference_onsets, estimated_onsets, *args, **kwargs):
        '''
        Metric with input onset annotations validated
        '''
        # If reference or estimated onsets are empty, warn because metric will be 0
        if reference_onsets.size == 0:
            warnings.warn("Reference onsets are empty.")
        if estimated_onsets.size == 0:
            warnings.warn("Estimated onsets are empty.")
        for onsets in [reference_onsets, estimated_onsets]:
            util.validate_events(onsets)
        return metric(reference_onsets, estimated_onsets, *args, **kwargs)
    return metric_validated

@validate
def f_measure(reference_onsets, estimated_onsets, window=.05):
    '''
    Compute the F-measure of correct vs incorrectly predicted onsets.
    "Corectness" is determined over a small window.

    :usage:
        >>> reference_onsets = mir_eval.io.load_events('reference.txt')
        >>> estimated_onsets = mir_eval.io.load_events('estimated.txt')
        >>> f_measure = mir_eval.onset.f_measure(reference_beats, estimated_beats)

    :parameters:
        - reference_onsets : np.ndarray
            reference onset locations, in seconds
        - estimated_onsets : np.ndarray
            estimated onset locations, in seconds
        - window : float
            Window size, in seconds, default 0.05

    :returns:
        - f_measure : float
            2*precision*recall/(precision + recall)
        - precision : float
            (# true positives)/(# true positives + # false positives)
        - recall : float
            (# true positives)/(# true positives + # false negatives)
    '''
    # If either list is empty, return 0s
    if reference_onsets.size == 0 or estimated_onsets.size == 0:
        return 0., 0., 0.
    # Compute the best-case matching between reference and estimated onset locations
    matching = util.match_events(reference_onsets,
                                 estimated_onsets,
                                 window)

    precision = float(len(matching))/len(estimated_onsets)
    recall = float(len(matching))/len(reference_onsets)
    # Compute F-measure and return all statistics
    return util.f_measure(precision, recall), precision, recall

# Create a dictionary which maps the name of each metric
# to the function used to compute it
METRICS = collections.OrderedDict()
METRICS['F-measure'] = f_measure
