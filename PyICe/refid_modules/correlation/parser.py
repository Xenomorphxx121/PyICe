from pystdf.IO import Parser
from unit_parse import parser as uparser
import pystdf.V4
import csv

RECORDTYPE = 0


class FileReader:
    def __init__(self):
        self.data = []

    def after_send(self, dataSource, data):
        self.data.append(data)

    def write(self, line):
        self.data.append(line)

    def flush(self):
        pass


def map_data(record_type, data):
    return {k: v for (k, v) in zip(record_type.fieldNames, data)}


class STDFParser:
    def __init__(self, filename):
        self._test_name_dict = {}
        with open(filename, 'rb') as file:
            p = Parser(inp=file, reopen_fn=None)
            reader = FileReader()
            p.addSink(reader)
            p.parse()
            self.parts = {}
            self.metadata = {}
            for line in reader.data:
                master_info = map_data(*line)
                record_type = type(line[RECORDTYPE])
                if record_type is pystdf.V4.Ptr:  # Parametric Test Record - This is a test within this part.
                    self._test_name_dict[master_info['TEST_TXT']] = {
                        'upper_limit': master_info['HI_LIMIT'],
                        'lower_limit': master_info['LO_LIMIT'],
                        'result': master_info['RESULT'],
                        'units': master_info['UNITS'],
                    }

    def __getitem__(self, item):
        return self._test_name_dict[item]

        # assert num_devices == 1, "Correlation STDF must have only one DUT record"


class ATE_index_utils:  # Not really a part of this parser module, but will be part of the correlation enterprise.
    def __init__(self):
        self.index_file = "file/location.csv"

    def get_stdf_location(self, dut_id):
        with open(self.index_file, 'r') as index_file:
            csvreader = csv.reader(index_file)
            for row in csvreader:
                if row[0] is dut_id:
                    stdf_file = row[0]
                    break
        return stdf_file

    def append_index(self, dut_id, stdf_file_location):
        with open(self.index_file, 'a') as index_file:
            csvwriter = csv.writer(index_file)
            csvwriter.writerow([dut_id, stdf_file_location])


class do_i_pass_corr:
    def __init__(self, dut_id, testname, bench_data, upper_diff=None, lower_diff=None, percent=None):
        ATE_utils = ATE_index_utils()
        stdf_file = ATE_utils.get_stdf_location(dut_id)
        ate_data = uparser(STDFParser(stdf_file)[testname]['result']+STDFParser(stdf_file)[testname]['units'])
        errors = self.compare(ate_data, bench_data)
        if percent:
            assert upper_diff is None and lower_diff is None
            upper_diff = ate_data * percent*0.01
            lower_diff = -1 * upper_diff
        assert (upper_diff is not None) and (lower_diff is not None), f'Limits are not defined for {self}'
        self.verdict(errors, upper_diff, lower_diff)

    @staticmethod
    def compare(ate_data, bench_data):
        error = []
        if hasattr(bench_data, '__iter__'):
            for datapoint in bench_data:
                error.append(datapoint - ate_data)
        else:
            error.append(bench_data - ate_data)
        return error

    @staticmethod
    def verdict(errors, upper_diff, lower_diff):
        pass_above = True if ((upper_diff is None) or len([err for err in errors if err > upper_diff]) == 0) else False
        pass_below = True if ((lower_diff is None) or len([err for err in errors if err < lower_diff]) == 0) else False
        if pass_above and pass_below:
            # Print victory message.
            return True
        else:
            # Print failure message along with most egregious error.
            return False


if __name__ == '__main__':
    # STDFParser(filename='example_stdf/lot2.stdf')
    STDFParser(filename='../../../../../projects/stowe_eval/correlation/REVID7/2022-01-05/5627908_LT3390_25C_CLASS_PRI_FT_TRIM_LT3390_BOS-EAGLE1_20220105_102154.std_1')

# e.g.
# corr = do_i_pass_corr('DUT1', 'ch1_vout', [1.6,1.66,1.6], percent=2)
