# -*- coding: utf-8 -*-

import glob
import yaml
import os.path
import time
import bnf
import sys
import sqlite3
import cgi
import html
import pprint
import json

if len(sys.argv) < 2:
    print("Usage: %s dbs.postgresql.v9_2" % sys.argv[0])
    sys.exit(1)

run_test = __import__(sys.argv[1], globals(), locals(), ['run_test']).run_test

def load_db_config(name):
    features_file = open("%s/config.yml" % name.replace('.', '/'), "r")
    return yaml.load(features_file)

def get_all_features(standard):
    features_file = open("standards/%s/features.yml" % standard, "r")
    all_features = yaml.load(features_file)

    for group in ('mandatory', 'optional'):
        for feature_id in all_features[group]:
            all_features[group][feature_id] = {
                'description': all_features[group][feature_id]
            }

    return all_features

def feature_id_from_file_path(file_path):
    return file_path.split('/')[-1][:-4]

def output_file(feature_file_path):
    return feature_file_path[:-4] + ".tests.yml"

def all_features_with_tests(standard):
    all_files = glob.glob("standards/%s/*/*.yml" % standard)
    feature_files = []
    for feature_file_path in sorted(all_files):
        basename = os.path.basename(feature_file_path)
        if basename[0].upper() != basename[0] or '.tests.yml' in basename:
            continue

        feature_files.append(feature_file_path)

    return feature_files

def get_rules(standard):
    raw_rules = bnf.parse_bnf_file('standards/%s/bnf.txt' % standard)
    return bnf.analyze_rules(raw_rules)

def generate_tests(feature_file_path, db_config):
    feature_file = open(feature_file_path, "r")
    tests = yaml.load_all(feature_file)
    basename = os.path.basename(feature_file_path)
    result_tests = []
    test_number = 0

    for test in tests:
        test_number += 1

        override = {}
        if 'override' in test:
            override = test['override']
        for name in override:
            if override[name] is None:
                override[name] = ''
            override[name] = bnf.ASTKeyword(str(override[name]))

        exclude = []
        if 'exclude' in test:
            exclude = test['exclude']

        if isinstance(test['sql'], list):
            test['sql'] = ';'.join(test['sql'])

        sqls = bnf.get_paths_for_rule(rules, test['sql'], override, exclude)

        for rule_number in range(0, len(sqls)):
            test_id = '%s_%02d_%02d' % (
                basename.split('.')[0].replace('-', '_').lower(),
                test_number, rule_number + 1
            )

            sqls[rule_number] = sqls[rule_number].replace('TN', 'TABLE_%s' % test_id.upper())
            sqls[rule_number] = sqls[rule_number].replace('ROLE1', 'ROLE_%s' % test_id.upper())
            sqls[rule_number] = sqls[rule_number].replace('CURSOR1', 'CUR_%s' % test_id.upper())
            sqls[rule_number] = sqls[rule_number].replace('CONSTRAINT1', 'CONST_%s' % test_id.upper())
            sqls[rule_number] = sqls[rule_number].replace('VIEW1', 'VIEW_%s' % test_id.upper())

            split_sql = sqls[rule_number].split(' ; ')
            if len(split_sql) == 1:
                split_sql = split_sql[0]

            result_tests.append({
                'id': test_id,
                'feature': basename[:-4],
                'sql': split_sql
            })

    with open(output_file(feature_file_path), "w") as f:
        f.write(yaml.dump_all(result_tests, default_flow_style=False))

# FIX ME
db_config = load_db_config(sys.argv[1])
standard = '2016'
rules = get_rules(standard)
feature_file_paths = all_features_with_tests(standard)
test_files = {}

for feature_file_path in feature_file_paths:
    feature_id = feature_id_from_file_path(feature_file_path)
    generated_file_path = output_file(feature_file_path)
    test_files[feature_id] = {
        'path': generated_file_path
    }

    #if os.path.isfile(generated_file_path):
    #   continue

    print("Generating tests for %s" % feature_id)
    generate_tests(feature_file_path, db_config)

def fix_keywords(sql):
    if 'keywords' not in db_config:
        return sql

    for keyword in db_config['keywords']:
        sql = sql.replace(keyword, db_config['keywords'][keyword])

    return sql

# Run the tests
for feature_id in sorted(test_files):
    file_path = test_files[feature_id]['path']
    test_file = open(file_path, "r")
    tests = list(yaml.load_all(test_file))

    test_files[feature_id]['pass'] = 0
    test_files[feature_id]['fail'] = 0

    for t in tests:
        print(t)

    for test in tests:
        did_pass = True

        if not isinstance(test['sql'], list):
            test['sql'] = [ test['sql'] ]

        # Fix keywords
        test['sql'] = map(fix_keywords, test['sql'])

        error = run_test(test)
        did_pass = error is None

        if did_pass:
            test_files[feature_id]['pass'] += 1
            print('\33[32m  ✓ %s\33[0m\n' % '\n    '.join(test['sql']))
        else:
            test_files[feature_id]['fail'] += 1
            print('\33[31m  ✗ %s\n    ERROR: %s\33[0m\n' % ('\n    '.join(test['sql']), error))

# Merge the rules with the original features
all_features = get_all_features(standard)
for feature_id in test_files:
    all_features['mandatory'][feature_id].update(test_files[feature_id])

# Generate YAML report

feats = {
    'mandatory': {},
    'optional': {}
}

total_tests = 0
total_passed = 0

for category in ('mandatory', 'optional'):
    for feature_id in sorted(all_features[category]):
        f = all_features[category][feature_id]

        if 'pass' in all_features[category][feature_id]:
            f['pass'] = all_features[category][feature_id]['pass']
            f['fail'] = all_features[category][feature_id]['fail']
        else:
            f['pass'] = 0
            f['fail'] = 0

        if '-' not in feature_id and ('%s-01' % feature_id) in all_features[category]:
            for fid in sorted(all_features[category]):
                if fid.startswith('%s-' % feature_id) and \
                'pass' in all_features[category][fid]:
                    f['pass'] += all_features[category][fid]['pass']
                    f['fail'] += all_features[category][fid]['fail']

        percent = '&nbsp;'
        color = 'grey'
        if 'pass' in f and (f['pass'] + f['fail']) > 0:
            if f['pass'] == 0:
                pass_rate = 0
            else:
                pass_rate = float(f['pass']) / (float(f['pass']) + float(f['fail']))

            percent = '%01.0d%% (%d/%d)' % (pass_rate * 100, f['pass'],
                int(f['pass']) + int(f['fail']))

            if '-' not in feature_id:
                total_tests += f['pass'] + f['fail']
                total_passed += f['pass']

        feats[category][feature_id] = {
            'description': html.escape(all_features[category][feature_id]['description']),
            "pass": int(f['pass']),
            "total": int(f['pass']) + int(f['fail']),
        }

# YAML is a much better format, but we use JSON so it can be easily ingested in
# JavaScript for HTML reports.
path = "%s/result/%s.json" % (sys.argv[1].replace('.', '/'), standard)
with open(path, "w") as report_file:
    db = {
        'dbname': db_config['db']['name'],
        'dbversion': str(db_config['db']['version']),
        'path': path
    }
    report_file.write('loadResults(')
    report_file.write(json.dumps({'info': db, 'features': feats}, sort_keys=True, indent=2, separators=(',', ': ')))
    report_file.write(')')
