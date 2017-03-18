import sys
import os
import re
# Processes parameters from external parameter file and runs a series of stress tests.
# Program works with input file name stress_test_parameters.txt and runs a Joedog's
#       Seige Stress test for each given parameter of a specified website.
#
# Specify the location of your Joedog's Siege package in StressRun.build_and_run
#
# needs partner file named:
#          stress_test_parameters.txt
# produces output file named:
#          stress_test_results.txt


class StressRun(object):
    # class takes in a list of urls marked with whether or not they need a token, a list of paramters to be run,
    # a token if needed, and the number of runs per test.

    def __init__(self, urls, params, token=None, runs=1, outfile='stress_test_results.txt'):

        self.urls = urls
        self.params = params
        self.runs = runs
        self.token = token
        self.command = ""
        self.markedcommand = ""
        self.logfile = ""
        self.outfile = outfile
        self.create_outfile(self.outfile)
        self.sim_mode = False

    def build_and_run(self):
        siege = ""  # Specify Location of Siege Package here!
        print "\nCommands:"
        for url in self.urls:
            print url
            for parameter_set in self.params:
                self.logfile = parameter_set[0] + ".log"
                log = "-l" + parameter_set[0] + ".log"
                delay = "-d" + parameter_set[1]
                users = "-c" + parameter_set[2]
                time = "-t" + parameter_set[3]

                marker = url[0] + " " + delay + " " + users + " " + time
                commandstring = delay + " " + users + " " + time + " " + log

                if self.token and url[1] == "token":
                    commandstring += " --header=\'Authorization: Token " + self.token + "\'"
                if url[0] == "urls.txt":
                    self.command = self.command = siege + " " + commandstring + " -m " + "\'" + marker + \
                                                  "\'" + " -furls.txt"
                else:
                    self.command = siege + " " + commandstring + " -m " + "\'" + marker + "\' " + url[0]
                self.run_command()

    def run_command(self):
        output_count = 1
        for i in range(self.runs):
            print '\t' + self.command
            os.system(self.command)
            output_count += 1
            self.collect_data()

    def find_spot(self):
        # finds the number of lines returns the
        # number of data groups and does not include the file header
        ffh = open(self.logfile, 'r')
        n = 0
        for line in ffh:
            line = line.split()
            if line:
                n += 1

        data_groups = (n + 1) / 2
        current_start = (data_groups - 2) * 2
        ffh.close()
        return current_start

    def collect_data(self):

        start = self.find_spot()
        ofh = open(self.outfile, 'a')
        ffh = open(self.logfile, 'r')
        ffh.readline()

        test = self.logfile[:-4]
        marker = ""
        data = ""
        count = 0
        for line in ffh:
            line.split()
            if count == start:
                marker = line
            else:
                print "Count does not equal start."
            if marker:
                data = line
            count += 1
            ffh.close()

            testparam = []
            marker = marker[5:-5].split()
            indata = marker[1:]
            url = marker[0]

            for item in indata:
                item = item[2:]
                testparam.append(item)

            outdata = ""
            data = data.split(",")
            # print data
            count = 0
            for item in data:
                item = item.strip()
                if count == 1:
                    outdata += '\t' + test + '\t' + url + '\t' + testparam[0] + '\t' + testparam[1] + '\t' + testparam[
                        2]
                outdata += '\t' + item
                count += 1
            print >> ofh, outdata

    def create_outfile(self, outfile=None):
        if not outfile:
            outfile = "stress_test_results.txt"
        ofh = open(outfile, 'a')
        out_header = "Date & Time\tTest\tURL\tDelay\tUsers\tTime\tTrans\t Elap Time\tData Trans\tResp Time\t" \
                     "Trans Rate\tThroughput\tConcurrent\tOKAY\tFailed"
        print >> ofh, out_header
        ofh.close()


class ReadRunFile(object):

    def __init__(self, infile='stress_test_parameters.txt'):
        self.infile = open(infile)
        self.parameterList = []
        self.runs = None
        self.token = None
        self.urls = []
        self.logfiles = []

    def parse_file(self):
        parameter_mode = False
        url_mode = False
        sim_mode = False
        dataheader = None
        ufh = None
        for line in self.infile:
            line = line.strip()

            if line.startswith("#number of runs"):
                pattern = None
                line = self.infile.next()
                pattern = re.search('\d', line)

                if pattern:
                    self.runs = int(pattern.group(0))
                    print "Set to", self.runs, "runs per command."
                else:
                    print "Running the default number of runs: 1"

            elif line.startswith("#parameters"):
                url_mode = False
                parameter_mode = True

            elif line.startswith("#token"):
                self.token = self.infile.next().strip()

            elif line.startswith("#urls"):
                parameter_mode = False
                url_mode = True

            elif parameter_mode and not dataheader:
                dataheader = line

            elif parameter_mode and dataheader and line:
                self.make_parameter_list(line)

            elif url_mode:
                if line.startswith("Test Real World Simulation"):
                    if line.endswith("no"):
                        pass
                    elif line.endswith("yes"):
                        sim_mode = True
                        url_mode = False

                        print "Entering Real World Simulation Mode!"
                        next_line = self.infile.next().strip()
                        token_holder = ''

                        if next_line.endswith("yes"):
                            token_holder = 'token'

                        elif next_line.endswith("no"):
                            token_holder = 'token'

                        self.urls.append(['urls.txt', token_holder])

                elif line.startswith("Is token needed"):
                    pass

                elif line and not sim_mode:
                    print line
                    data = line.split()
                    urlinfo = [data[0], data[1]]
                    self.urls.append(urlinfo)

            elif sim_mode:
                ufh = open('urls.txt', 'a')
                print line
                print >> ufh, line

            if ufh:
                ufh.close()
            self.infile.close()

    def make_parameter_list(self, line):
        # grabs the parameters from a line and creates a string
        data = line.split()

        self.parameterList.append(data)

    def get_parameter_list(self):
        return self.parameterList

    def get_urls(self):
        return self.urls

    def get_runs(self):
        return self.runs

    def get_token(self):
        return self.token


def main():
    if len(sys.argv) < 1:
        print "USAGE: python %s" % (sys.argv[0])
        sys.exit()

    test1_parameters = 'userHomeTest_parameters.txt'
    test1_results = 'userHomeTest_results.txt'
    test1_readfile = ReadRunFile(test1_parameters)
    test1_readfile.parse_file()
    test1_parameter_list = test1_readfile.get_parameter_list()
    test1_url_list = test1_readfile.get_urls()
    test1_num_runs = test1_readfile.get_runs()
    test1_token = test1_readfile.get_token()
    test1_run = StressRun(test1_url_list, test1_parameter_list, test1_token, test1_num_runs, test1_results)
    test1_run.build_and_run()

    test2_parameters = 'userSimTest_parameters.txt'
    test2_results = 'userSimTest_results.txt'
    test2_readfile = ReadRunFile(test2_parameters)
    test2_readfile.parse_file()
    test2_parameter_list = test2_readfile.get_parameter_list()
    print test2_parameter_list
    test2_url_list = test2_readfile.get_urls()
    test2_num_runs = test2_readfile.get_runs()
    test2_token = test2_readfile.get_token()
    test2_run = StressRun(test2_url_list, test2_parameter_list, test2_token, test2_num_runs, test2_results)
    test2_run.build_and_run()

if __name__ == "__main__":
    main()
