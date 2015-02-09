# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from mock import patch
import unittest

import ocw_evaluation_from_config as config_runner
import ocw.metrics

import yaml

class TestMetricLoad(unittest.TestCase):
    def test_valid_metric_load(self):
        config = yaml.safe_load("""
            metrics:
                - Bias
        """)
        loaded_metrics = [config_runner._load_metric(m)()
                          for m in config['metrics']]
        self.assertTrue(isinstance(loaded_metrics[0], ocw.metrics.Bias))

    @patch('ocw_evaluation_from_config.logger')
    def test_invalid_metric_load(self, mock_logger):
        config = yaml.safe_load("""
            metrics:
                - ocw.metrics.Bias
        """)
        config_runner._load_metric(config['metrics'][0])
        error = (
            'User-defined metrics outside of the ocw.metrics module '
            'cannot currently be loaded. If you just wanted a metric '
            'found in ocw.metrics then do not specify the full '
            'package and module names. See the documentation for examples.'
        )
        mock_logger.error.assert_called_with(error)


class TestRCMEDDatasetConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.required_rcmed_keys = set([
            'dataset_id',
            'parameter_id',
            'min_lat',
            'max_lat',
            'min_lon',
            'max_lon',
            'start_time',
            'end_time'
        ])
        example_config_yaml = """
            - data_source: rcmed
              dataset_id: 4
              parameter_id: 4
              min_lat: -40
              max_lat: 40
              min_lon: -50
              max_lon: 50
              start_time: YYYY-MM-DDThh:mm:ss
              end_time: YYYY-MM-DDThh:mm:ss

            - data_source: rcmed
        """
        conf = yaml.safe_load(example_config_yaml)
        self.valid_rcmed = conf[0]
        self.invalid_rcmed = conf[1]

    def test_valid_rcmed_config(self):
        ret = config_runner._valid_dataset_config_data(self.valid_rcmed)
        self.assertTrue(ret)

    @patch('ocw_evaluation_from_config.logger')
    def test_invalid_rcmed_config(self, mock_logger):
        config_runner._valid_dataset_config_data(self.invalid_rcmed)

        present_keys = set(self.invalid_rcmed.keys())
        missing_keys = self.required_rcmed_keys - present_keys
        missing = sorted(list(missing_keys))

        error = (
            'Dataset does not contain required keys. '
            'The following keys are missing: {}'.format(', '.join(missing))
        )
        mock_logger.error.assert_called_with(error)


class TestLocalDatasetConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.required_local_keys = set(['data_source', 'file_count', 'path', 'variable'])
        example_config_yaml = """
            - data_source: local
              file_count: 1
              path: /a/fake/path
              variable: pr
              optional_args:
                  name: Target1

            - data_source: local

            - data_source: local
              file_count: 5
              file_glob_pattern: something for globbing files here
              variable: pr
              path: /a/fake/path
              optional_args:
                  name: Target1

            - data_source: local
              file_count: 5
              variable: pr
              path: /a/fake/path
        """

        conf = yaml.safe_load(example_config_yaml)
        self.valid_local_single = conf[0]
        self.invalid_local_single = conf[1]
        self.valid_local_multi = conf[2]
        self.invalid_local_multi = conf[1]
        self.invalid_local_multi_file_glob = conf[3]

    def test_valid_local_config_single_file(self):
        ret = config_runner._valid_dataset_config_data(self.valid_local_single)
        self.assertTrue(ret)

    def test_valid_local_config_multi_file(self):
        ret = config_runner._valid_dataset_config_data(self.valid_local_multi)
        self.assertTrue(ret)

    @patch('ocw_evaluation_from_config.logger')
    def test_invalid_local_config(self, mock_logger):
        config_runner._valid_dataset_config_data(self.invalid_local_single)

        present_keys = set(self.invalid_local_single.keys())
        missing_keys = self.required_local_keys - present_keys
        missing = sorted(list(missing_keys))

        error = (
            'Dataset does not contain required keys. '
            'The following keys are missing: {}'.format(', '.join(missing))
        )
        mock_logger.error.assert_called_with(error)

    @patch('ocw_evaluation_from_config.logger')
    def test_invalid_local_config_multi_file(self, mock_logger):
        # mutlifile config is handled slightly differently. We should see the
        # same missing keys in this situation as we would on the single file
        # local config. We will test for a missing file_glob_pattern in a
        # different test.
        config_runner._valid_dataset_config_data(self.invalid_local_multi)

        present_keys = set(self.invalid_local_multi.keys())
        missing_keys = self.required_local_keys - present_keys
        missing = sorted(list(missing_keys))

        error = (
            'Dataset does not contain required keys. '
            'The following keys are missing: {}'.format(', '.join(missing))
        )
        mock_logger.error.assert_called_with(error)

    @patch('ocw_evaluation_from_config.logger')
    def test_invalid_local_config_multi_file_missing_file_glob(self, mock_logger):
        # We can't check for the file_glob_pattern pattern until after we have
        # verified that the single local file config has been met.
        config_runner._valid_dataset_config_data(self.invalid_local_multi_file_glob)

        mock_logger.error.assert_called_with(
            'Multi-file local dataset is missing key: file_glob_pattern'
        )


class TestESGFDatasetConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.required_esgf_keys = set([
            'data_source',
            'dataset_id',
            'variable',
            'esgf_username',
            'esgf_password'
        ])
        example_config_yaml = """
           - data_source: esgf
             dataset_id: fake dataset id
             variable: pr
             esgf_username: my esgf username
             esgf_password: my esgf password

           - data_source: esgf
        """
        conf = yaml.safe_load(example_config_yaml)
        self.valid_esgf = conf[0]
        self.invalid_esgf = conf[1]

    def test_valid_esgf_conf(self):
        ret = config_runner._valid_dataset_config_data(self.valid_esgf)
        self.assertTrue(ret)

    @patch('ocw_evaluation_from_config.logger')
    def test_invalid_esgf_conf(self, mock_logger):
        config_runner._valid_dataset_config_data(self.invalid_esgf)

        present_keys = set(self.invalid_esgf.keys())
        missing_keys = self.required_esgf_keys - present_keys
        missing = sorted(list(missing_keys))

        error = (
            'Dataset does not contain required keys. '
            'The following keys are missing: {}'.format(', '.join(missing))
        )
        mock_logger.error.assert_called_with(error)


class TestDAPDatasetConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.required_dap_keys = set(['url', 'variable'])
        example_config_yaml = """
           - data_source: dap
             url: afakeurl.com
             variable: pr

           - data_source: dap
        """
        conf = yaml.safe_load(example_config_yaml)
        self.valid_dap = conf[0]
        self.invalid_dap = conf[1]

    def test_valid_dap_config(self):
        ret = config_runner._valid_dataset_config_data(self.valid_dap)
        self.assertTrue(ret)

    @patch('ocw_evaluation_from_config.logger')
    def test_invalid_dap_config(self, mock_logger):
        config_runner._valid_dataset_config_data(self.invalid_dap)

        present_keys = set(self.invalid_dap.keys())
        missing_keys = self.required_dap_keys - present_keys
        missing = sorted(list(missing_keys))

        error = (
            'Dataset does not contain required keys. '
            'The following keys are missing: {}'.format(', '.join(missing))
        )
        mock_logger.error.assert_called_with(error)


class InvalidDatasetConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        example_config_yaml = """
            - file_count: 1
              path: /a/fake/path
              variable: pr

            - data_source: invalid_location_identifier
        """
        conf = yaml.safe_load(example_config_yaml)
        self.missing_data_source = conf[0]
        self.invalid_data_source = conf[1]

    @patch('ocw_evaluation_from_config.logger')
    def test_missing_data_source_config(self, mock_logger):
        config_runner._valid_dataset_config_data(self.missing_data_source)
        mock_logger.error.assert_called_with(
            'Dataset does not contain a data_source attribute.'
        )

    @patch('ocw_evaluation_from_config.logger')
    def test_invalid_data_source(self, mock_logger):
        config_runner._valid_dataset_config_data(self.invalid_data_source)
        mock_logger.error.assert_called_with(
            'Dataset does not contain a valid data_source location.'
        )


class MetricFetchTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        binary_config = """
            metrics:
                - Bias
                - StdDevRatio
        """
        unary_config = """
            metrics:
                - TemporalStdDev
        """
        self.unary_conf = yaml.safe_load(unary_config)
        self.binary_conf = yaml.safe_load(binary_config)

    def test_contains_binary_metric(self):
        ret = config_runner._contains_binary_metrics(self.binary_conf['metrics'])
        self.assertTrue(ret)

    def test_does_not_contain_binary_metric(self):
        ret = config_runner._contains_binary_metrics(self.unary_conf['metrics'])
        self.assertFalse(ret)

    def test_contains_unary_metric(self):
        ret = config_runner._contains_unary_metrics(self.unary_conf['metrics'])
        self.assertTrue(ret)
        
    def test_does_not_contain_unary_metric(self):
        ret = config_runner._contains_unary_metrics(self.binary_conf['metrics'])
        self.assertFalse(ret)


class TestValidMinimalConfig(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        no_datasets_config = """
        metrics:
            - Bias
        """
        self.no_datasets = yaml.safe_load(no_datasets_config)

        no_metrics_config = """
        datasets:
            reference:
                data_source: dap
                url: afakeurl.com
                variable: pr
        """
        self.no_metrics = yaml.safe_load(no_metrics_config)

        unary_with_reference_config = """
        datasets:
            reference:
                data_source: dap
                url: afakeurl.com
                variable: pr

        metrics:
            - TemporalStdDev
        """
        self.unary_with_reference = yaml.safe_load(unary_with_reference_config)

        unary_with_target_config = """
        datasets:
            targets:
                - data_source: dap
                  url: afakeurl.com
                  variable: pr

        metrics:
            - TemporalStdDev
        """
        self.unary_with_target = yaml.safe_load(unary_with_target_config)

        unary_no_reference_or_target = """
        datasets:
            not_ref_or_target:
                - data_source: dap
                  url: afakeurl.com
                  variable: pr

        metrics:
            - TemporalStdDev
        """
        self.unary_no_ref_or_target = yaml.safe_load(unary_no_reference_or_target)

        binary_valid_config = """
        datasets:
            reference:
                data_source: dap
                url: afakeurl.com
                variable: pr

            targets:
                - data_source: dap
                  url: afakeurl.com
                  variable: pr
        metrics:
            - Bias
        """
        self.binary_valid = yaml.safe_load(binary_valid_config)

        binary_no_reference_config = """
        datasets:
            targets:
                - data_source: dap
                  url: afakeurl.com
                  variable: pr
        metrics:
            - Bias
        """
        self.binary_no_reference = yaml.safe_load(binary_no_reference_config)

        binary_no_target_config = """
        datasets:
            reference:
                data_source: dap
                url: afakeurl.com
                variable: pr

        metrics:
            - Bias
        """
        self.binary_no_target = yaml.safe_load(binary_no_target_config)

    @patch('ocw_evaluation_from_config.logger')
    def test_no_datasets(self, mock_logger):
        ret = config_runner._valid_minimal_config(self.no_datasets)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'No datasets specified in configuration data.'
        )

    @patch('ocw_evaluation_from_config.logger')
    def test_no_metrics(self, mock_logger):
        ret = config_runner._valid_minimal_config(self.no_metrics)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'No metrics specified in configuration data.'
        )

    def test_unary_with_reference(self):
        ret = config_runner._valid_minimal_config(self.unary_with_reference)
        self.assertTrue(ret)

    def test_unary_with_target(self):
        ret = config_runner._valid_minimal_config(self.unary_with_target)
        self.assertTrue(ret)

    @patch('ocw_evaluation_from_config.logger')
    def test_unary_no_datasets(self, mock_logger):
        ret = config_runner._valid_minimal_config(self.unary_no_ref_or_target)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Unary metric in configuration data requires either a reference '
            'or target dataset to be present for evaluation. Please ensure '
            'that your config is well formed.'
        )

    def test_valid_binary(self):
        ret = config_runner._valid_minimal_config(self.binary_valid)
        self.assertTrue(ret)

    @patch('ocw_evaluation_from_config.logger')
    def test_binary_no_reference(self, mock_logger):
        ret = config_runner._valid_minimal_config(self.binary_no_reference)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Binary metric in configuration requires both a reference '
            'and target dataset to be present for evaluation. Please ensure '
            'that your config is well formed.'
        )
        
    @patch('ocw_evaluation_from_config.logger')
    def test_binary_no_target(self, mock_logger):
        ret = config_runner._valid_minimal_config(self.binary_no_target)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Binary metric in configuration requires both a reference '
            'and target dataset to be present for evaluation. Please ensure '
            'that your config is well formed.'
        )


class TestIsConfigValid(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        not_minimal_config = """
            datasets:
        """
        self.not_minimal = yaml.safe_load(not_minimal_config)

        not_well_formed_config = """
        datasets:
            reference:
                data_source: local
                file_count: 1
                path: /a/fake/path/file.py
                variable: pr

            targets:
                - data_source: local
                  file_count: 5
                  file_glob_pattern: something for globbing files here
                  variable: pr
                  optional_args:
                      name: Target1

                - data_source: esgf
                  dataset_id: fake dataset id
                  variable: pr
                  esgf_username: my esgf username
                  esgf_password: my esgf password

        metrics:
            - Bias
            - TemporalStdDev
        """
        self.not_well_formed = yaml.safe_load(not_well_formed_config)

    @patch('ocw_evaluation_from_config.logger')
    def test_not_minimal_config(self, mock_logger):
        ret = config_runner.is_config_valid(self.not_minimal)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Insufficient configuration file data for an evaluation'
        )

    @patch('ocw_evaluation_from_config.logger')
    def test_not_valid_config(self, mock_logger):
        ret = config_runner.is_config_valid(self.not_well_formed)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            'Configuration data is not well formed'
        )


class TestConfigIsWellFormed(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        malformed_reference_config = """
            datasets:
                reference:
                    data_source: notavalidlocation

            metrics:
                - Bias
        """
        self.malformed_reference_conf = yaml.safe_load(malformed_reference_config)

        malformed_target_list_config = """
            datasets:
                targets:
                    notalist: 
                        a_key: a_value

                    alsonotalist:
                        a_key: a_value

            metrics:
                - Bias
        """
        self.malformed_target_list = yaml.safe_load(malformed_target_list_config)

        missing_metric_name_config = """
            datasets:
                reference:
                    data_source: dap
                    url: afakeurl.com
                    variable: pr

            metrics:
                - NotABuiltInMetric
        """
        self.missing_metric_name = yaml.safe_load(missing_metric_name_config)

    def test_malformed_reference_config(self):
        ret = config_runner._config_is_well_formed(self.malformed_reference_conf)
        self.assertFalse(ret)

    @patch('ocw_evaluation_from_config.logger')
    def test_malformed_target_dataset_list(self, mock_logger):
        ret = config_runner._config_is_well_formed(self.malformed_target_list)
        self.assertFalse(ret)

        mock_logger.error.assert_called_with(
            "Expected to find list of target datasets but instead found "
            "object of type <type 'dict'>"
        )

    def test_not_builtin_metric(self):
        ret = config_runner._config_is_well_formed(self.missing_metric_name)
        self.assertFalse(ret)

    @patch('ocw_evaluation_from_config.logger')
    def test_warns_regarding_not_builtin_metric(self, mock_logger):
        ret = config_runner._config_is_well_formed(self.missing_metric_name)
        mock_logger.warn.assert_called_with(
            'Unable to locate metric name NotABuiltInMetric in built-in '
            'metrics. If this is not a user defined metric then please check '
            'for potential misspellings.'
        )
