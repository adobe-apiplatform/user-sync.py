import os
import pytest
import pytest
import logging

from user_sync.rules import RuleProcessor


def test_log_after_mapping_hook_scope(log_stream):
    stream, logger = log_stream

    state = {
        'source_attributes': {
            'email': 'bsisko@seaofcarag.com',
            'identity_type': None,
            'username': None,
            'domain': None,
            'givenName': 'Benjamin',
            'sn': 'Sisko',
            'c': 'CA'},
        'source_groups': set(),
        'target_attributes': {
            'email': 'bsisko@seaofcarag.com',
            'username': 'bsisko@seaofcarag.com',
            'domain': 'seaofcarag.com',
            'firstname': 'Benjamin',
            'lastname': 'Sisko',
            'country': 'CA'},
        'target_groups': set(),
        'log_stream': logger,
        'hook_storage': None}

    ruleprocessor = RuleProcessor({})
    ruleprocessor.logger = logger

    ruleprocessor.after_mapping_hook_scope = state
    ruleprocessor.log_after_mapping_hook_scope(before_call=True)

    stream.flush()
    x = stream.getvalue()

    state['target_groups'] = {'One'}
    state['target_attributes'] =  {'firstname' : 'John'}
    state['source_attributes'] = {'sn': 'David'}
    state['source_groups'] = {'One'}

    ruleprocessor.after_mapping_hook_scope = state
    ruleprocessor.log_after_mapping_hook_scope(after_call=True)
