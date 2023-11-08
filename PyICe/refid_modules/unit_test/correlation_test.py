import pytest
from PyICe.refid_modules.correlation.correlation_analyzer import CorrelationAnalyzer
# from PyICe.refid_modules.correlation.parser import STDFParser
from PyICe.data_utils import stdf_utils

corr_ex = '../correlation/example_stdf/lot2.stdf'
# corr_ex = ['../correlation/example_stdf/lot2.stdf']
stwe_ex = '../../../../../projects/stowe_eval/correlation/REVID7/2022-01-05/5627908_LT3390_25C_CLASS_PRI_FT_TRIM_LT3390_BOS-EAGLE1_20220105_102154.std_1'


# stwe_ex = '../correlation/example_stdf/5627908_LT3390_25C_CLASS_PRI_FT_TRIM_LT3390_BOS-EAGLE1_20220105_102154.std_1'
# stwe_ex = ['../correlation/example_stdf/5627908_LT3390_25C_CLASS_PRI_FT_TRIM_LT3390_BOS-EAGLE1_20220105_102154.std_1']


@pytest.mark.parametrize('filename, part_id', [(corr_ex, '2'), (stwe_ex, '1')])
def test_ate_data_exists(filename, part_id):
    analyzer = CorrelationAnalyzer(stdf_utils.stdf_reader(filename).parts[part_id]['TESTS'])
    assert analyzer.all_target_data


@pytest.mark.parametrize('filename, part_id, testname',
                         [(corr_ex, '2', 'Src out I       <> EA_SRC'), (stwe_ex, '1', 'VOUT CH1')])
def test_parsed_data(filename, part_id, testname):
    analyzer = CorrelationAnalyzer(stdf_utils.stdf_reader(filename).parts[part_id]['TESTS'])
    parsed_data = analyzer._parsed_data(testname)
    print(parsed_data)
    assert hasattr(parsed_data, 'm')
    assert hasattr(parsed_data, 'u')


@pytest.mark.parametrize('filename, part_id, testname, kwargs',
                         [(
                          corr_ex, '2', 'Src out I       <> EA_SRC', {'units': 'A', 'upper_diff': 1, 'lower_diff': -1}),
                          (stwe_ex, '1', 'VOUT CH1', {'units': 'V', 'upper_diff': 0.1, 'lower_diff': -0.1}),
                          (stwe_ex, '1', 'VOUT CH1', {'units': 'V', 'upper_diff': 0.1, 'lower_diff': None}),
                          (stwe_ex, '1', 'VOUT CH1', {'target_data': 1, 'percent': 10}),
                          ]
                         )
def test_set_limits(filename, part_id, testname, kwargs):
    # analyzer = CorrelationAnalyzer(STDFParser(filename, part_id))
    analyzer = CorrelationAnalyzer(stdf_utils.stdf_reader(filename).parts[part_id]['TESTS'])
    # analyzer.target_data = analyzer._parsed_data(testname + '_25')
    analyzer.target_data = analyzer._parsed_data(testname)
    upper_limit, lower_limit = analyzer._set_limits(**kwargs)
    assert (upper_limit is not None) or (lower_limit is not None)


@pytest.mark.parametrize('filename, part_id, kwargs', [(corr_ex, '2',
                                                        {'testname': 'Src out I       <> EA_SRC',
                                                         'bench_data': [-0.0002],
                                                         'units': 'A', 'upper_diff': 1, 'lower_diff': -1}),
                                                       (stwe_ex, '1',
                                                        {'testname': 'VOUT CH1', 'bench_data': 0.8, 'units': 'V',
                                                         'upper_diff': 0.1, 'lower_diff': -0.1}),
                                                       (stwe_ex, '1',
                                                        {'testname': 'VOUT CH1', 'bench_data': [0.8], 'units': 'V',
                                                         'upper_diff': 0.1, 'lower_diff': -0.1}),
                                                       (stwe_ex, '1',
                                                        {'testname': 'VOUT CH1', 'bench_data': [800], 'units': 'mV',
                                                         'upper_diff': 0.1, 'lower_diff': -0.1}),
                                                       (stwe_ex, '1',
                                                        {'testname': 'VOUT CH1', 'bench_data': [800], 'units': 'mV',
                                                         'upper_diff': 0.1, 'lower_diff': None}),
                                                       (stwe_ex, '1',
                                                        {'testname': 'VOUT CH1', 'bench_data': [0.8], 'units': 'V',
                                                         'percent': 3}),
                                                       (stwe_ex, '1',
                                                        {'testname': 'VOUT CH1', 'bench_data': 800, 'units': 'mV',
                                                         'upper_diff': 0.1, 'lower_diff': -0.1}),
                                                       (stwe_ex, '1',
                                                        {'testname': 'VOUT CH1', 'bench_data': 0.8, 'units': 'V',
                                                         'upper_diff': 0.1, 'lower_diff': -0.1}),
                                                       (stwe_ex, '2',
                                                        {'testname': 'VOUT CH1', 'bench_data': 0.8, 'units': 'V',
                                                         'upper_diff': 0.1, 'lower_diff': -0.1})
                                                       ]
                         )
def test_verdict(filename, part_id, kwargs):
    analyzer = CorrelationAnalyzer(stdf_utils.stdf_reader(filename).parts[part_id]['TESTS'])
    assert analyzer.verdict(**kwargs)


@pytest.mark.parametrize('filename, part_id, kwargs', [(corr_ex, '2',
                                                        {'testname': 'Src out I       <> EA_SRC', 'bench_data': [1.3],
                                                         'units': 'A', 'upper_diff': 1, 'lower_diff': -1}),
                                                       (stwe_ex, '1',
                                                        {'testname': 'VOUT CH1', 'bench_data': 0, 'units': 'V',
                                                         'upper_diff': 0.1, 'lower_diff': -0.1}),
                                                       (stwe_ex, '1',
                                                        {'testname': 'VOUT CH1', 'bench_data': [1000], 'units': 'mV',
                                                         'upper_diff': 0.1, 'lower_diff': None}),
                                                       (stwe_ex, '1',
                                                        {'testname': 'VOUT CH1', 'bench_data': 1.2, 'units': 'V',
                                                         'upper_diff': 0.1, 'lower_diff': -0.1}),
                                                       (stwe_ex, '2',
                                                        {'testname': 'VOUT CH1', 'bench_data': 1.2, 'units': 'V',
                                                         'upper_diff': 0.1, 'lower_diff': -0.1})
                                                       ]
                         )
def test_verdict_fail(filename, part_id, kwargs):
    analyzer = CorrelationAnalyzer(stdf_utils.stdf_reader(filename).parts[part_id]['TESTS'])
    assert not analyzer.verdict(**kwargs)
